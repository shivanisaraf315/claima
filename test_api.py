import google.genai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"Key found: {api_key[:10]}...")

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello in one word"
)
print(f"Gemini replied: {response.text}")