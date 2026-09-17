import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def generate_ai_summary(disease, symptoms, description, precautions, medications, diet, workout):
    if client is None:
        print("AI summary skipped: GEMINI_API_KEY not found in environment.")
        return None

    prompt = f"""
You are a helpful medical assistant explaining a preliminary AI prediction to a patient.
Do not diagnose independently — you are only explaining an existing prediction in simple terms.

Predicted condition: {disease}
Reported symptoms: {', '.join(symptoms)}
Description: {description}
Precautions: {precautions}
Suggested medications: {medications}
Suggested diet: {diet}
Suggested workout: {workout}

Write a short (4-6 sentence), warm, easy-to-understand summary for the patient explaining:
1. What this condition generally means
2. Why these precautions/diet/medication suggestions make sense
3. A gentle reminder to consult a real doctor before acting on this

Keep it concise, no headings, plain paragraph text.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"AI summary generation failed: {e}")
        return None