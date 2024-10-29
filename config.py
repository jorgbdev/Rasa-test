import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BACKEND_ENDPOINT_URL = os.getenv("BACKEND_ENDPOINT_URL")
