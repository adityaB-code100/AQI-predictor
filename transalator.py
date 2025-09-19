from flask import Flask, request
import google.generativeai as genai
import os
import json

# Load Gemini API Key
# ✅ Load configuration from config.json
with open("config.json") as f:
    config = json.load(f)


#-------------API Key Setup-------------
api_key = config["API_KEY"]["key"]
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")  # You can use gemini-pro or gemini-1.5-pro for better quality

def translator_gemini(text, target_language):
    if not text or not target_language:
        return "Please enter text and select a target language."

    try:
        prompt = f"Translate the following text into {target_language}:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error using Gemini API: {e}"

# # Test
# p = translator("hello Rutik, how is your team?", "Hindi")
# print(p)
