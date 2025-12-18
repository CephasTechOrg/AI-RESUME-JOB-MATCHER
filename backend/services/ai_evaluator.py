import hashlib
import json
from typing import Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Flexible imports to work whether launched as package ("backend.main") or module ("main")
try:
    from backend.utils.config import config
    from backend.utils.logger import logger
    from backend.services.keyword_matcher import KeywordMatcher
    from backend.services.quality_gate import QualityGate
    from backend.utils.cache import ResponseCache
    from backend.utils.security import scrub_pii
except ImportError:
    from utils.config import config
    from utils.logger import logger
    from services.keyword_matcher import KeywordMatcher
    from services.quality_gate import QualityGate
    from utils.cache import ResponseCache
    from utils.security import scrub_pii


class AIEvaluator:
    def __init__(self):
        self.api_key = config.DEEPSEEK_API_KEY
        self.api_url = config.DEEPSEEK_API_URL
        self.keyword_matcher = KeywordMatcher()
        self.quality_gate = QualityGate()
        self.cache = ResponseCache(ttl_seconds=config.CACHE_TTL_SECONDS)

        self.session = requests.Session()
        retries = Retry(
            total=2,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def evaluate_resume(
        self,
        job_title: str,
        job_description: str,
        resume_text: str,
        intern_level: str = "general"
    ) -> Dict:
        """Evaluate resume against job description using DeepSeek API"""
        truncated_resume = (resume_text or "")[: config.MAX_TEXT_LENGTH]
        cache_key = hashlib.sha256(
            f"{job_title}:{job_description}:{truncated_resume}:{intern_level}".encode("utf-8")
        ).hexdigest()
        cached = self.cache.get(cache_key)
        if cached:
            cached["cache_status"] = "hit"
            return cached

        if not self.api_key:
            logger.warning("DeepSeek API key not found, returning mock data")
            keyword_report = self.keyword_matcher.evaluate(
                resume_text=truncated_resume,
                job_description=job_description,
                intern_level=intern_level
            )
            result = self._build_keyword_driven_fallback(keyword_report, job_description, truncated_resume)
            self.cache.set(cache_key, result)
            return result

        prompt = self._build_evaluation_prompt(job_title, job_description, truncated_resume, intern_level)

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }

            response = self.session.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=config.REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()

            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]

            # Parse JSON response from AI
            evaluation = self._parse_ai_response(ai_response)

            keyword_report = self.keyword_matcher.evaluate(
                resume_text=truncated_resume,
                job_description=job_description,
                intern_level=intern_level
            )

            evaluation["scores"]["keyword_match"] = keyword_report["score"]
            evaluation["missing_keywords"] = keyword_report["missing_keywords"]
            evaluation["keyword_matches"] = keyword_report.get("matches", [])

            quality = self.quality_gate.run(truncated_resume, job_description, evaluation["keyword_matches"])
            evaluation["quality_gates"] = quality
            evaluation["cache_status"] = "miss"
            evaluation["source"] = "ai"

            self.cache.set(cache_key, evaluation)
            return evaluation

        except Exception as e:
            logger.error(f"AI API error: {scrub_pii(str(e))}")
            keyword_report = self.keyword_matcher.evaluate(
                resume_text=truncated_resume,
                job_description=job_description,
                intern_level=intern_level
            )
            result = self._build_keyword_driven_fallback(keyword_report, job_description, truncated_resume)
            self.cache.set(cache_key, result)
            return result

    def _get_system_prompt(self) -> str:
        return """You are a professional recruiter and AI resume analyst.
        Evaluate the resume against the provided job description.

        ANALYZE AND SCORE THE FOLLOWING (0-100 EACH):
        1. Job Compatibility
        2. Resume Structure and Formatting
        3. Skills Relevance
        4. Experience Relevance
        5. Keyword Match
        6. Writing Clarity and Tone
        7. Resume Strength vs Typical Applicants
        8. Professional Presentation
        9. Improvement Readiness
        10. Overall Impact Score

        ALSO RETURN:
        - List of missing or weak keywords.
        - 5 short improvement suggestions if improvement needed.
        - Overall summary (3-4 lines).

        TREAT KEYWORDS FLEXIBLY:
        - Consider synonyms: debugging ~ fixing issues/troubleshooting; testing ~ QA/verification; GitHub Flow ~ version control/source control.
        - Collaboration terms (teamwork, standups, pair programming, code reviews) are interchangeable signals.
        - If advanced skills are present (production, deployments, system design), assume basics like programming/web fundamentals, Git, debugging, and testing are covered even if not spelled out.
        - For intern levels, freshmen tolerate basics, seniors expect ownership; REWARD candidates who exceed the selected level. Do NOT penalize or warn for being overqualified—treat that as a positive signal.

        CONTEXTUAL SCORING:
        - Reward recent experience and measurable impact (users reached, revenue, performance gains).
        - Treat overqualification as a positive: bump "strength_comparison" and "overall_impact" when advanced signals appear.

        RETURN OUTPUT IN JSON FORMAT ONLY:
        {
          "scores": {
            "job_compatibility": 85,
            "structure": 78,
            "skills_relevance": 90,
            "experience_relevance": 82,
            "keyword_match": 75,
            "clarity": 88,
            "strength_comparison": 80,
            "presentation": 85,
            "improvement_readiness": 70,
            "overall_impact": 83
          },
          "missing_keywords": ["keyword1", "keyword2"],
          "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
          "summary": "Overall summary here"
        }"""

    def _build_evaluation_prompt(
        self,
        job_title: str,
        job_description: str,
        resume_text: str,
        intern_level: str = "general"
    ) -> str:
        level_note = ""
        if "intern" in job_title.lower():
            level_note = f"""The candidate selected an intern level of "{intern_level}".
- Be more forgiving for "freshman" (intro/basics), moderate for "sophomore"/"junior", and tighter for "senior".
- Recognize equivalent phrases (synonyms) for testing, debugging, and version control (e.g., Git, GitHub, git flow, fixing bugs, troubleshooting, unit tests, QA).
- Responsibilities and requirements can use varied verbs (contribute/assist/participate/own); interpret them as coverage if intent matches.
- If stronger/advanced signals exist, infer the basics are already covered and avoid flagging them as missing."""

        return f"""
        Job Title: {job_title}

        Job Description:
        {job_description}

        {level_note}

        Resume Content:
        {resume_text}

        Please analyze this resume against the job description and provide your evaluation in the specified JSON format.
        """

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response and extract JSON"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse AI response: {scrub_pii(str(e))}")
            return self._get_mock_evaluation()

    def _get_mock_evaluation(self) -> Dict:
        """Static mock used when parsing fails."""
        return {
            "scores": {
                "job_compatibility": 70,
                "structure": 72,
                "skills_relevance": 68,
                "experience_relevance": 65,
                "keyword_match": 60,
                "clarity": 75,
                "strength_comparison": 70,
                "presentation": 73,
                "improvement_readiness": 65,
                "overall_impact": 70,
            },
            "missing_keywords": [],
            "keyword_matches": [],
            "quality_gates": {"warnings": [], "hallucinated": [], "pii_detected": {}},
            "cache_status": "miss",
            "suggestions": ["Add concrete metrics and outcomes to key bullets."],
            "summary": "Mock evaluation used when the AI response could not be parsed.",
        }

    def _build_keyword_driven_fallback(self, keyword_report: Dict, job_description: str, resume_text: str) -> Dict:
        """
        Build a deterministic evaluation using keyword coverage when the AI API is unavailable.
        Keeps scores tied to resume content to avoid always-100 results.
        """
        kw_score = keyword_report.get("score", 0)
        missing = keyword_report.get("missing_keywords", [])
        matches = keyword_report.get("matches", [])

        job_compatibility = max(40, min(95, round(kw_score * 0.8 + 20)))
        skills_relevance = max(40, min(95, round(kw_score * 0.85 + 15)))
        experience_relevance = max(40, min(95, round(kw_score * 0.75 + 20)))
        structure = 75
        clarity = 78
        strength_comparison = max(35, min(90, round(kw_score * 0.6 + 25)))
        presentation = 76
        improvement_readiness = max(30, min(90, 100 - kw_score // 2))
        overall = max(40, min(95, round((job_compatibility + skills_relevance + experience_relevance + kw_score) / 4)))

        suggestions = []
        if missing:
            suggestions.append(
                f"Add 2-3 bullets demonstrating {', '.join(missing[:4])} with ownership + metrics."
            )
        if kw_score < 85:
            suggestions.append("Add 1-2 lines on testing/debugging (e.g., Jest/Playwright, root-cause fixes).")
        if kw_score < 90:
            suggestions.append("Quantify impact (latency, users, revenue, error-rate) per project.")
        suggestions.append("Ensure each project lists tech stack, tests, and debugging outcomes.")

        quality = self.quality_gate.run(resume_text, job_description, matches)

        return {
            "scores": {
                "job_compatibility": job_compatibility,
                "structure": structure,
                "skills_relevance": skills_relevance,
                "experience_relevance": experience_relevance,
                "keyword_match": kw_score,
                "clarity": clarity,
                "strength_comparison": strength_comparison,
                "presentation": presentation,
                "improvement_readiness": improvement_readiness,
                "overall_impact": overall,
            },
            "missing_keywords": missing,
            "keyword_matches": matches,
            "quality_gates": quality,
            "cache_status": "miss",
            "source": "fallback",
            "suggestions": suggestions,
            "summary": (
                "Keyword-based fallback analysis. Improve by covering missing concepts, "
                "quantifying outcomes, and highlighting tests/debugging."
            ),
        }

    def connectivity_check(self) -> Dict:
        """Best-effort check for API key presence and network reachability."""
        key_present = bool(self.api_key)
        reachable = False
        error = None
        if not key_present:
            return {"api_key_present": False, "api_reachable": False, "error": "Missing DEEPSEEK_API_KEY"}
        try:
            probe = self.session.get(self.api_url, timeout=5)
            reachable = probe.status_code < 500
        except Exception as exc:  # noqa: BLE001
            error = scrub_pii(str(exc))
        return {"api_key_present": key_present, "api_reachable": reachable, "error": error}

    def chat_follow_up(
        self,
        question: str,
        job_title: str,
        job_description: str,
        resume_text: str,
        evaluation: Dict,
    ) -> Dict:
        """
        Lightweight follow-up Q&A using the same model with provided context.
        """
        truncated_resume = (resume_text or "")[: config.MAX_TEXT_LENGTH]
        cache_key = hashlib.sha256(
            f"chat:{question}:{job_title}:{job_description}:{truncated_resume}".encode("utf-8")
        ).hexdigest()
        cached = self.cache.get(cache_key)
        if cached:
            return {"answer": cached, "cache_status": "hit"}

        if not self.api_key:
            answer = self._build_chat_fallback(question, evaluation)
            self.cache.set(cache_key, answer)
            return {"answer": answer, "cache_status": "miss"}

        try:
            prompt = self._build_chat_prompt(question, job_title, job_description, truncated_resume, evaluation)
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": self._get_chat_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.35,
                "max_tokens": 800,
            }
            response = self.session.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                json=payload,
                timeout=config.REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            self.cache.set(cache_key, content)
            return {"answer": content, "cache_status": "miss"}
        except Exception as e:
            logger.error(f"Chat API error: {scrub_pii(str(e))}")
            answer = self._build_chat_fallback(question, evaluation)
            self.cache.set(cache_key, answer)
            return {"answer": answer, "cache_status": "miss"}

    def _get_chat_system_prompt(self) -> str:
        return (
            "You are a concise resume coach. Use the provided evaluation, job description, "
            "and resume context to answer follow-up questions in 3-6 bullet points, with concrete examples. "
            "Avoid repeating the full evaluation; focus on new, actionable guidance."
        )

    def _build_chat_prompt(
        self,
        question: str,
        job_title: str,
        job_description: str,
        resume_text: str,
        evaluation: Dict,
    ) -> str:
        summary = evaluation.get("summary", "")
        missing = ", ".join(evaluation.get("missing_keywords", [])[:6])
        suggestions = "; ".join(evaluation.get("suggestions", [])[:4])
        return f"""
        Job Title: {job_title}
        Job Description: {job_description}

        Resume (excerpt):
        {resume_text[:1200]}

        Prior evaluation summary: {summary}
        Missing/weak areas: {missing}
        Prior suggestions: {suggestions}

        Follow-up question: {question}
        Please respond with 3-6 concise bullets tailored to the resume and JD, including concrete examples or phrasing where possible.
        """

    def _build_chat_fallback(self, question: str, evaluation: Dict) -> str:
        missing = evaluation.get("missing_keywords", [])
        suggestions = evaluation.get("suggestions", [])
        parts = []
        if missing:
            parts.append(f"Cover missing areas: {', '.join(missing[:5])}.")
        if suggestions:
            parts.append(f"Quick wins: {suggestions[0]}")
        parts.append("Add 1-2 bullets with metrics (users, latency, revenue) and testing/debugging proof.")
        parts.append("Mirror JD wording for top requirements and align with role level expectations.")
        return " • ".join(parts)
