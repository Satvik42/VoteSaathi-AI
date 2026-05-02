import os
from google import genai

try:
    API_KEY = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=API_KEY) if API_KEY else genai.Client()
    print("Available Models for generate_content:")
    for m in client.models.list():
        # Check if generateContent is supported
        if "generateContent" in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    import traceback
    traceback.print_exc()
