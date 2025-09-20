import os
import json
from get_from_db import get_aqi_data, get_aqi_by_village
import google.generativeai as genai  # Correct import

# Types is available inside google.generativeai
from google.generativeai import types  

# Load configuration from config.json
with open("config.json") as f:
    config = json.load(f)

# API Key Setup
api_key = config["API_KEY"]["key"]
genai.configure(api_key=api_key)  # Configure the client

def get_report(village, date):
    data = get_aqi_data(date, village)
    data['Village'] = village

    prompt = f"""
Generate a detailed Air Quality & Weather Health Report in html format based on this data:

{data}

The report must have exactly 8 sections (with <h2> headings, main heading in <h1>):

1. Summary
2. Gaseous Pollutants (NO, NO2, NOx, SO2, CO, pm2.5, pm10)
3. Ozone Levels
4. Weather Overview
5. Health Risks Summary
6. Cause of Pollution (Predicted by AI)
7. Safety Recommendations
8. Tips for Sensitive Groups (Children, Elderly, Pregnant Women, Respiratory Patients)

Each section should include detailed explanation, and include the Village name.
"""

    # Generate content
    response = genai.models.generate_content(
        model="models/gemini-1.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=10000  # Avoid ridiculously large numbers
        )
    )

    report = response.text
    if not report:
        report = "Sorry, the model did not generate a report."
    else:
        # Remove markdown fences
        report = report.replace("```html", "").replace("```", "").strip()

    return report
