import os
import json
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
# Make sure to set GEMINI_API_KEY in your environment or .env file before running
API_KEY = os.environ.get("GEMINI_API_KEY")
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    print("WARNING: GEMINI_API_KEY environment variable not set. API calls will fail.")

# Fallback chain of models to handle exhausted API credits
FALLBACK_MODELS = [
    "gemini-3.1-flash-preview", # Priority model as requested
    "gemini-1.5-flash",         # Backup flash
    "gemini-1.5-pro"            # Backup pro
]

# System instruction strictly mapping to user requirements
SYSTEM_INSTRUCTION = """You are VoteSaathi, a highly empathetic and accurate guide for the Indian Election System. 
Respond in the language requested by the user. Do not use complex legal jargon. Provide answers in short, actionable steps. 
Acknowledge user anxiety around voting edge cases. Output your response in a JSON format containing two keys: 
'answer' (the step-by-step guidance in markdown) and 'next_suggestions' (an array of 2 to 3 related follow-up scenarios the user might face)."""

@app.route("/")
def index():
    """Render the main single-page application."""
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle incoming chat requests from the frontend and interact with Gemini API."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request. JSON body is required."}), 400
        
    query = data.get("query")
    language = data.get("language", "English")
    
    if not query:
        return jsonify({"error": "Query is required."}), 400
        
    if not API_KEY:
        return jsonify({"error": "Server is missing GEMINI_API_KEY configuration."}), 500
        
    try:
        # Construct the final prompt including user context
        prompt = f"User Query: {query}\nRequested Language: {language}"
        
        # Dynamically fetch available models to ensure we ONLY use models your API key has access to
        available_models = []
        try:
            for m in client.models.list():
                if hasattr(m, 'name') and 'gemini' in m.name.lower():
                    # Only append models that support generating content (avoid embedding models)
                    if not ('embed' in m.name.lower() or 'text-embedding' in m.name.lower()):
                        available_models.append(m.name)
        except Exception as e:
            print(f"Dynamic model fetch failed: {str(e)}")
            available_models = FALLBACK_MODELS

        # Prioritize 'flash' models (like 3.1 flash preview) to save API credits as requested
        flash_models = [m for m in available_models if 'flash' in m.lower()]
        other_models = [m for m in available_models if 'flash' not in m.lower()]
        models_to_try = flash_models + other_models

        # Fallback if list is somehow empty
        if not models_to_try:
            models_to_try = FALLBACK_MODELS

        response = None
        last_error = None
        
        for model_name in models_to_try:
            try:
                print(f"Attempting generation with model: {model_name}...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        response_mime_type="application/json"
                    )
                )
                print(f"Success with {model_name}!")
                # If successful, break out of the fallback loop
                break
            except Exception as e:
                print(f"Model {model_name} failed: {str(e)}")
                last_error = str(e)
                continue
                
        if not response:
            raise Exception(f"All dynamic fallback models failed. Last error: {last_error}")
        
        # Parse the JSON response
        response_data = json.loads(response.text)
        
        return jsonify(response_data)
        
    except json.JSONDecodeError:
        print("Error: Gemini API did not return valid JSON.")
        return jsonify({
            "error": "Failed to parse AI response.",
            "answer": "I received an unexpected format. Please try again.",
            "next_suggestions": []
        }), 500
    except Exception as e:
        error_msg = str(e)
        print(f"Error calling Gemini API: {error_msg}")
        return jsonify({
            "error": f"API Error: {error_msg}",
            "answer": "I'm sorry, I encountered an issue connecting to the Gemini engine. Please check your API key or network connection.",
            "next_suggestions": ["Try asking again", "Find my booth"]
        }), 500

@app.route("/translate_history", methods=["POST"])
def translate_history():
    """Translate existing chat history when language changes."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request. JSON body is required."}), 400
        
    texts = data.get("texts", [])
    target_language = data.get("target_language")
    
    if not texts or not target_language:
        return jsonify({"texts": texts})
        
    if not API_KEY:
        return jsonify({"error": "Server is missing GEMINI_API_KEY configuration."}), 500
        
    try:
        prompt = f"Translate the following array of strings into {target_language}. Return EXACTLY a JSON array of translated strings in the same order, and nothing else.\n\n{json.dumps(texts)}"
        
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        translated_texts = json.loads(response.text)
        return jsonify({"texts": translated_texts})
    except Exception as e:
        print(f"Translation Error: {str(e)}")
        return jsonify({"error": "Failed to translate history", "texts": texts}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
