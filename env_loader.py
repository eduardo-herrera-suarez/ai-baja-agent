from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("Loaded environment variables:")
print(f"OPENAI_API_KEY: {OPENAI_API_KEY is not None}")
print(f"TAVILY_API_KEY: {TAVILY_API_KEY is not None}")
print(f"GROQ_API_KEY: {GROQ_API_KEY is not None}")

