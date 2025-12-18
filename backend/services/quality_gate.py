import re
from typing import Dict, List, Tuple

try:
    from backend.utils.config import config
except ImportError:
    from utils.config import config


class QualityGate:
    """Linting and constraint checks for resumes prior to scoring."""

    def lint_resume(self, resume_text: str) -> List[str]:
        issues: List[str] = []
        if not resume_text:
            issues.append("Resume text is empty after parsing.")
            return issues

        if len(resume_text) > config.MAX_TEXT_LENGTH:
            issues.append(f"Resume truncated to {config.MAX_TEXT_LENGTH} characters for analysis.")

        if re.search(r"\\s{3,}", resume_text):
            issues.append("Excessive spacing detected; normalize spacing for readability.")

        if re.search(r"(.{0,80}\\n){3,}", resume_text):
            issues.append("Multiple short lines detected; ensure consistent bullet formatting.")

        return issues

    def detect_pii_presence(self, resume_text: str) -> Dict[str, bool]:
        email = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", resume_text or ""))
        phone = bool(re.search(r"\\b\\+?\\d[\\d\\s().-]{7,}\\b", resume_text or ""))
        location = bool(re.search(r"\\b(?:[A-Z][a-z]+\\s?){1,2},?\\s?(?:[A-Z]{2}|[A-Za-z]+)\\b", resume_text or ""))
        return {"email": email, "phone": phone, "location": location}

    def detect_location_requirement(self, job_description: str) -> bool:
        jd_text = (job_description or "").lower()
        return any(keyword in jd_text for keyword in config.LOCATION_REQUIRED_KEYWORDS)

    def detect_hallucinated_keywords(self, matches: List[Dict]) -> List[str]:
        """Flags semantic matches that are low-confidence."""
        hallucinated = []
        for match in matches:
            if match.get("method") == "semantic" and match.get("score", 1.0) < 0.6:
                hallucinated.append(match["label"])
        return hallucinated

    def contact_location_gates(self, job_description: str, resume_text: str) -> List[str]:
        warnings: List[str] = []
        pii = self.detect_pii_presence(resume_text)

        if not pii["email"]:
            warnings.append("Add a contact email so recruiters can reach you.")
        if not pii["phone"]:
            warnings.append("Add a phone number for fast scheduling.")

        if self.detect_location_requirement(job_description) and not pii["location"]:
            warnings.append("JD requires onsite/hybrid; include your city/region to confirm location fit.")
        return warnings

    def run(self, resume_text: str, job_description: str, matches: List[Dict]) -> Dict:
        lint_warnings = self.lint_resume(resume_text)
        hallucinated = self.detect_hallucinated_keywords(matches)
        contact_warnings = self.contact_location_gates(job_description, resume_text)

        gates: List[str] = lint_warnings + contact_warnings
        if hallucinated:
            gates.append(f"Low-confidence matches for: {', '.join(hallucinated[:5])}. Clarify with concrete bullets.")

        return {
            "warnings": gates,
            "hallucinated": hallucinated,
            "pii_detected": self.detect_pii_presence(resume_text),
        }
