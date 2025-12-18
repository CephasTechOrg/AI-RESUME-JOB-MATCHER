import re
from typing import Dict, List, Tuple

try:
    from backend.services.semantic_embedder import SemanticEmbedder
except ImportError:
    from services.semantic_embedder import SemanticEmbedder

BASE_CONCEPTS = {
    "debugging": {
        "label": "Debugging / fixing issues",
        "tier": "core",
        "weight": 1.0,
        "synonyms": [
            "debugging",
            "debugged",
            "fix bugs",
            "fixed bugs",
            "fix issues",
            "bug fixes",
            "bug-fixes",
            "bug fixing",
            "resolved defects",
            "troubleshoot",
            "troubleshooting",
            "resolve issues",
            "resolved issues",
            "fixing issues",
            "bugfix",
            "bug fix",
            "bug-fix",
            "bugfixes",
            "fixing technical issues",
            "technical issues",
            "api errors",
            "reduce api errors",
            "production issues",
            "issue resolution",
            "bug triage",
            "fixing code",
            "stability fixes",
        ],
    },
    "testing": {
        "label": "Testing / writing tests",
        "tier": "core",
        "weight": 1.0,
        "synonyms": [
            "unit test",
            "unit tests",
            "integration test",
            "integration tests",
            "automated tests",
            "qa testing",
            "qa",
            "test coverage",
            "tested features",
            "wrote tests",
            "test cases",
            "verification",
            "unit testing",
            "test automation",
            "quality assurance",
            "testing features",
            "tests",
            "testing",
            "test suites",
            "playwright",
            "pytest",
            "jest",
            "smoke tests",
            "regression tests",
            "test plan",
            "test scripts",
        ],
    },
    "version_control": {
        "label": "Version control (Git/GitHub)",
        "tier": "core",
        "weight": 1.0,
        "synonyms": [
            "git",
            "github",
            "gitlab",
            "bitbucket",
            "version control",
            "git workflow",
            "git workflows",
            "git flow",
            "github flow",
            "git version control",
            "source control",
            "merge request",
            "pull request",
            "git branching",
            "git workflows",
            "git repos",
            "git repository",
            "git repositories",
            "git commits",
            "branch strategy",
            "code reviews",
            "pr reviews",
            "git operations",
        ],
    },
    "teamwork": {
        "label": "Team collaboration",
        "tier": "core",
        "weight": 0.9,
        "synonyms": [
            "collaborated",
            "cross functional",
            "team meetings",
            "team meeting",
            "standups",
            "standup",
            "scrum meetings",
            "scrum",
            "pair programming",
            "paired with",
            "worked with team",
            "worked with teammates",
            "collaboration",
            "team sync",
            "collaborated in team meetings",
            "teamwork",
            "teammates meetings",
            "stakeholder updates",
            "project updates",
            "sprint ceremonies",
        ],
    },
    "assigned_tasks": {
        "label": "Assigned tasks / feature work",
        "tier": "basic",
        "weight": 0.6,
        "synonyms": [
            "assigned tasks",
            "assigned work",
            "project tasks",
            "feature work",
            "implement features",
            "ticket",
            "jira ticket",
            "story points",
            "backlog item",
            "user stories",
            "tasks",
            "task list",
            "deliverables",
            "sprint tasks",
            "work items",
        ],
    },
    "clean_code": {
        "label": "Clean, maintainable code",
        "tier": "core",
        "weight": 0.7,
        "synonyms": [
            "clean code",
            "maintainable code",
            "readable code",
            "refactored code",
            "code quality",
            "linting",
            "code cleanup",
            "refactoring",
            "codebase hygiene",
            "style guide",
        ],
    },
    "learning_mindset": {
        "label": "Learning mindset",
        "tier": "basic",
        "weight": 0.5,
        "synonyms": [
            "learning new tools",
            "self learning",
            "self-taught",
            "curious",
            "eager to learn",
            "willingness to learn",
            "explore new tools",
            "research new tech",
            "learning mindset",
            "continuous learning",
        ],
    },
    "programming_fundamentals": {
        "label": "Programming fundamentals",
        "tier": "basic",
        "weight": 1.0,
        "synonyms": [
            "python",
            "javascript",
            "typescript",
            "java",
            "c++",
            "c#",
            "go",
            "loops",
            "functions",
            "data structures",
            "algorithms",
            "variables",
            "control flow",
            "conditionals",
            "recursion",
            "object oriented",
            "oop",
            "classes",
            "ds&a",
            "fundamentals",
        ],
    },
    "web_fundamentals": {
        "label": "Web/app fundamentals",
        "tier": "basic",
        "weight": 0.8,
        "synonyms": [
            "html",
            "css",
            "frontend",
            "backend",
            "api",
            "rest api",
            "database",
            "sql",
            "nosql",
            "express",
            "react",
            "django",
            "flask",
            "full stack",
            "client server",
            "http",
            "deployment",
            "hosting",
            "web app",
            "web application",
            "server side",
            "client side",
        ],
    },
    "advanced_engineering": {
        "label": "Advanced engineering experience",
        "tier": "advanced",
        "weight": 0.6,
        "synonyms": [
            "production",
            "deployment",
            "scalability",
            "microservices",
            "distributed systems",
            "cloud",
            "kubernetes",
            "docker",
            "cicd",
            "continuous integration",
            "continuous deployment",
            "mlops",
            "devops",
            "system design",
            "architecture",
            "high availability",
        ],
    },
}


LEVEL_MULTIPLIERS = {
    "freshman": 0.85,
    "sophomore": 0.95,
    "junior": 1.0,
    "senior": 1.1,
    "general": 1.0,
}


class KeywordMatcher:
    """Combines synonym matching with semantic similarity to reduce false negatives."""

    def __init__(self, concepts: Dict[str, Dict] = None, embedder: SemanticEmbedder = None):
        self.concepts = concepts or BASE_CONCEPTS
        self.embedder = embedder or SemanticEmbedder()

    @staticmethod
    def _normalize_text(text: str) -> str:
        lowered = text.lower()
        lowered = re.sub(r"[^a-z0-9+/#.& ]+", " ", lowered)
        return re.sub(r"\s+", " ", lowered).strip()

    def _phrase_present(self, haystack: str, phrase: str) -> bool:
        # Require word boundaries to avoid false positives (e.g., "api" in "capabilities", "git" in "digital").
        pattern = rf"(?<!\\w){re.escape(phrase)}(?!\\w)"
        return re.search(pattern, haystack) is not None

    def _chunk_text(self, text: str) -> List[str]:
        raw_chunks = re.split(r"[.;\\n]", text or "")
        return [chunk.strip() for chunk in raw_chunks if len(chunk.strip()) > 5]

    def _detect_recency_and_impact(self, resume_text: str) -> Tuple[bool, bool]:
        recent = bool(re.search(r"20(2[3-9]|3\\d)", resume_text or ""))
        impact = bool(re.search(r"\\b\\d+%|\\b\\d+\\s?(k|m|million|billion)\\b", (resume_text or "").lower()))
        return recent, impact

    def evaluate(self, resume_text: str, job_description: str, intern_level: str = "general") -> Dict:
        normalized_resume = self._normalize_text(resume_text or "")
        normalized_jd = self._normalize_text(job_description or "")

        # If the job description doesn't look like an intern role, keep level general
        level_key = intern_level.lower().strip() or "general"
        if "intern" not in normalized_jd and "intern" not in normalized_resume:
            level_key = "general"
        multiplier = LEVEL_MULTIPLIERS.get(level_key, 1.0)

        tier_rank = {"basic": 1, "core": 2, "advanced": 3}
        concept_results = {}
        total_weight = 0.0
        resume_chunks = self._chunk_text(resume_text)
        matches: List[Dict] = []

        for concept_key, concept in self.concepts.items():
            weight = concept.get("weight", 1.0) * multiplier
            total_weight += weight
            found = False
            method = "none"
            matched_phrase = None
            semantic_score = 0.0

            for phrase in concept["synonyms"]:
                norm_phrase = self._normalize_text(phrase)
                # Only count matches present in the resume; JD text should not auto-satisfy keywords.
                if norm_phrase and self._phrase_present(normalized_resume, norm_phrase):
                    found = True
                    method = "exact"
                    matched_phrase = phrase
                    break
                if not found and self.embedder and self.embedder.model:
                    hit, score, candidate = self.embedder.any_above_threshold(
                        phrase, resume_chunks, threshold=0.62
                    )
                    if hit:
                        found = True
                        method = "semantic"
                        matched_phrase = candidate or phrase
                        semantic_score = score
                        break

            concept_results[concept_key] = {
                "label": concept["label"],
                "weight": weight,
                "tier": concept.get("tier", "core"),
                "found": found,
                "method": method,
                "matched_phrase": matched_phrase,
                "semantic_score": semantic_score,
            }
            if found:
                matches.append(
                    {
                        "key": concept_key,
                        "label": concept["label"],
                        "method": method,
                        "matched_phrase": matched_phrase or "",
                        "score": semantic_score or 1.0,
                    }
                )

        matched_concepts = {key for key, data in concept_results.items() if data["found"]}
        highest_tier_hit = max(
            [tier_rank.get(concept_results[key]["tier"], 1) for key in matched_concepts],
            default=0,
        )

        # Advanced evidence implies core practices and fundamentals even if not explicitly listed.
        if "advanced_engineering" in matched_concepts:
            matched_concepts.update({"debugging", "testing", "version_control", "clean_code"})

        # If any core or advanced signals show up, do not penalize for missing basic fundamentals.
        if highest_tier_hit >= tier_rank["core"]:
            for key, data in concept_results.items():
                if data["tier"] == "basic":
                    matched_concepts.add(key)

        # Advanced coverage implies core expectations as well.
        if highest_tier_hit >= tier_rank["advanced"]:
            for key, data in concept_results.items():
                if data["tier"] == "core":
                    matched_concepts.add(key)

        matched_weight = sum(
            data["weight"]
            for key, data in concept_results.items()
            if key in matched_concepts
        )

        score = 0
        if total_weight:
            score = round(max(0.0, min(100.0, (matched_weight / total_weight) * 100)))

        # Recency/impact boosts to reward up-to-date, outcome-focused resumes.
        recent, impact = self._detect_recency_and_impact(resume_text)
        if recent:
            score = min(100, score + 4)
        if impact:
            score = min(100, score + 5)

        # Overqualified logic: strong senior signals should nearly max out freshman/sophomore/general scoring.
        if highest_tier_hit >= tier_rank["advanced"]:
            if level_key in ("freshman", "sophomore"):
                score = min(100, max(score, 98))
            elif level_key == "general":
                score = min(100, max(score, 95))

        missing = [
            (key, data["label"])
            for key, data in concept_results.items()
            if key not in matched_concepts
        ]

        return {
            "score": score,
            "missing_keywords": [label for _, label in missing],
            "intern_level": level_key,
            "matches": matches,
        }
