import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
    API_AUTH_TOKEN = os.getenv("APP_AUTH_TOKEN", "")
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "900"))
    MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "20000"))
    LOCATION_REQUIRED_KEYWORDS = os.getenv(
        "LOCATION_REQUIRED_KEYWORDS",
        "onsite,on site,in-office,in office,hybrid"
    ).split(",")
    
config = Config()
