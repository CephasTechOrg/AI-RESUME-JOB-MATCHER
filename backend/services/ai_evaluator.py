import requests
import json
from typing import Dict, List

# Use absolute imports
from utils.config import config
from utils.logger import logger

class AIEvaluator:
    def __init__(self):
        self.api_key = config.DEEPSEEK_API_KEY
        self.api_url = config.DEEPSEEK_API_URL

    def evaluate_resume(self, job_title: str, job_description: str, resume_text: str) -> Dict:
        """Evaluate resume against job description using DeepSeek API"""
        
        if not self.api_key:
            logger.warning("DeepSeek API key not found, returning mock data")
            return self._get_mock_evaluation()

        prompt = self._build_evaluation_prompt(job_title, job_description, resume_text)
        
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
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # Parse JSON response from AI
            return self._parse_ai_response(ai_response)
            
        except Exception as e:
            logger.error(f"AI API error: {str(e)}")
            return self._get_mock_evaluation()

    def _get_system_prompt(self) -> str:
        return """You are a professional recruiter and AI resume analyst.
        Evaluate the resume against the provided job description.

        ANALYZE AND SCORE THE FOLLOWING (0–100 EACH):
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
        - Overall summary (3–4 lines).

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

    def _build_evaluation_prompt(self, job_title: str, job_description: str, resume_text: str) -> str:
        return f"""
        Job Title: {job_title}
        
        Job Description:
        {job_description}
        
        Resume Content:
        {resume_text}
        
        Please analyze this resume against the job description and provide your evaluation in the specified JSON format.
        """

    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse AI response and extract JSON"""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            json_str = response_text[json_start:json_end]
            
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Failed to parse AI response: {str(e)}")
            return self._get_mock_evaluation()

    def _get_mock_evaluation(self) -> Dict:
        """Return mock data for testing when API is unavailable"""
        return {
            "scores": {
                "job_compatibility": 75,
                "structure": 82,
                "skills_relevance": 78,
                "experience_relevance": 85,
                "keyword_match": 70,
                "clarity": 88,
                "strength_comparison": 80,
                "presentation": 79,
                "improvement_readiness": 65,
                "overall_impact": 78
            },
            "missing_keywords": ["Python", "Agile Methodology", "REST APIs"],
            "suggestions": [
                "Add more quantifiable achievements in your experience section",
                "Include relevant certifications for the target role",
                "Highlight leadership experience and project management skills"
            ],
            "summary": "This resume shows solid experience but could be strengthened with more specific achievements and better keyword optimization for the target role."
        }