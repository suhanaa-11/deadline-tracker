import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ No API key found — check your .env file")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-flash-latest")
    response = model.generate_content("Say hello in one short sentence.")
    print("✅ API key works! Response:", response.text)