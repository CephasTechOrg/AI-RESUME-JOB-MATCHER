import re

class TextCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        
        return text.strip()
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison"""
        return text.lower().strip()
