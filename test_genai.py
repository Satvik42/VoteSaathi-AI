import os
from google.genai import types

try:
    config = types.GenerateContentConfig(
        system_instruction="You are VoteSaathi.",
        response_mime_type="application/json"
    )
    print("SUCCESS Config")
except Exception as e:
    import traceback
    traceback.print_exc()
