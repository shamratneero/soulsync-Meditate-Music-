import json
import re
from openai import OpenAI

import os
from dotenv import load_dotenv
import os

load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_mood_and_respond(message):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
    "You are a supportive and emotionally intelligent assistant. "
    "Your response must ONLY be a valid JSON object with this structure:\n\n"
    '{ "reply": "...", "mood": "...", "should_suggest": true }\n\n'
    "Allowed mood values: sad, happy, anxious, angry, calm.\n\n"
    "Wrap your entire JSON response between <json> and </json> tags. "
    "Do not explain, greet, or output anything else. Only output:\n\n"
    "<json>{ \"reply\": \"...\", \"mood\": \"...\", \"should_suggest\": true }</json>"
)

                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.7,
            max_tokens=300
        )

        raw = response.choices[0].message.content.strip()
        print("🔍 Raw GPT response:", raw)

        #match = re.search(r"\{.*?\}", raw, re.DOTALL)

        match = re.search(r"<json>\s*(\{.*?\})\s*</json>", raw, re.DOTALL)

        if not match:
            raise ValueError("No valid JSON found in GPT response.")

        cleaned = json.loads(match.group(0))
        print("Parsed Value:", cleaned)

        return (
            cleaned.get("reply", "I'm here for you."),
            cleaned.get("mood", "neutral"),
            cleaned.get("should_suggest", False)
        )

    except Exception as e:
        print("GPT error:", e)
        return "Sorry, I couldn’t respond right now.", "neutral", False
