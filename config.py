import os
from dotenv import load_dotenv

load_dotenv()  # Load values from .env

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecret')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecret')
    MONGO_URI = os.getenv('MONGO_URI')  # ✅ Must match the env var name
