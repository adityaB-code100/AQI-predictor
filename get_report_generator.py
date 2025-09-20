
import os ,json


from get_from_db import get_aqi_data, get_aqi_by_village
from google import genai
from google.genai import types






# ✅ Load configuration from config.json
with open("config.json") as f:
    config = json.load(f)


#-------------API Key Setup-------------
api_key = config["API_KEY"]["key"] 
client = genai.Client(api_key=api_key)



def get_report(village, date):
    data=get_aqi_data(date,village)
    data['Village'] = village
    #print(data)


    prompt = f"""
Generate a detailed Air Quality & Weather Health Report in html format based on this data:

{data}

The report must have exactly 7 sections (Only This Sections) with <h2> headings and Main heading is in <h1> as follows:

1. Summary
2. Gaseous Pollutants (NO, NO2, NOx, SO2, CO,pm2.5,pm10) 
3. Ozone Levels
4. Weather Overview
5. Health Risks Summary
6. cause of pollution (Predicted By you )
7. Safety Recommendations
8. Tips for Sensitive Groups (Children, Elderly, Pregnant Women, Respiratory Patients)

Each section should include detailed explanation,
also add Village name in it
Do not skip any section. give me all 8 section Detail.
"""
# Generate content
    response = client.models.generate_content(
        model="models/gemini-1.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=1000000000
        )
    )

    report = response.text
    if not report:
        report = "Sorry, the model did not generate a report."
    else:
        # Remove markdown fences
        report = report.replace("```html", "").replace("```", "").strip()

    return report

