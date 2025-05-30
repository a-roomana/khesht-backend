import os
from typing import List

from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Server Configuration
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8000))
ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")

# CORS Configuration
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")
CORS_ALLOW_CREDENTIALS = os.environ.get("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = os.environ.get("CORS_ALLOW_METHODS", "*").split(",")
CORS_ALLOW_HEADERS = os.environ.get("CORS_ALLOW_HEADERS", "*").split(",")

# Security Configuration
ALLOW_ALL_ORIGINS = os.environ.get("ALLOW_ALL_ORIGINS", "true").lower() == "true"
