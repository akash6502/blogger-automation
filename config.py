import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    
    # Blogger Config
    BLOG_ID = os.getenv("BLOG_ID")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CLIENT_SECRET_FILE = os.getenv("CLIENT_SECRET_FILE", "credentials.json")
    PIXEL_API_KEY = os.getenv("PIXEL_API_KEY")
    
    # App Config
    DEBUG = os.getenv("DEBUG", "True") == "True"
