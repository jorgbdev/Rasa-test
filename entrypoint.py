from dotenv import load_dotenv
from rasa.__main__ import main

load_dotenv()  # take environment variables from .env.

if __name__ == "__main__":
    main()
