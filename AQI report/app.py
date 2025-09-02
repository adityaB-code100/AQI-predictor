from flask import Flask, render_template, request
from datetime import datetime
from google import genai
from google.genai import types
from get_from_db import get_aqi_data
client = genai.Client(api_key="AIzaSyBwYlyXOLW8TRle-6KUUKeAOXYHZQbtqB8")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Collect all form data
    data=get_aqi_data("2025-09-02",'Pune')
    print(data)
   # data = {
        # "PM2.5": request.form.get('pm25'),
        # "PM10": request.form.get('pm10'),
        # "NO": request.form.get('no'),
        # "NO2": request.form.get('no2'),
        # "NOx": request.form.get('nox'),
        # "NH3": request.form.get('nh3'),
        # "SO2": request.form.get('so2'),
        # "CO": request.form.get('co'),
        # "Ozone": request.form.get('ozone'),
        # "Benzene": request.form.get('benzene'),
        # "Toluene": request.form.get('toluene'),
        # "Xylene": request.form.get('xylene'),
        # "O-Xylene": request.form.get('o_xylene'),
        # "Eth-Benzene": request.form.get('eth_benzene'),
        # "MP-Xylene": request.form.get('mp_xylene'),
        # "Air Temperature (°C)": request.form.get('at'),
    #     "Relative Humidity (%)": request.form.get('rh'),
    #     "Wind Speed (m/s)": request.form.get('ws'),
    #     "Wind Direction (deg)": request.form.get('wd'),
    #     "Rainfall (mm)": request.form.get('rf'),
    #     "Total Rainfall (mm)": request.form.get('tot_rf'),
    #     "Solar Radiation (W/m²)": request.form.get('sr'),
    #     "Barometric Pressure (mmHg)": request.form.get('bp'),
    #     "Temperature 2m (°C)": request.form.get('temperature_2m'),
    #     "Relative Humidity 2m (%)": request.form.get('relative_humidity_2m'),
    #     "Rain 2m (mm)": request.form.get('rain'),
    #     "Surface Pressure (hPa)": request.form.get('surface_pressure'),
    #     "Wind Speed 10m (km/h)": request.form.get('wind_speed_10m'),
    #     "Wind Speed 100m (km/h)": request.form.get('wind_speed_100m'),
    #     "Wind Direction 10m (°)": request.form.get('wind_direction_10m'),
    #     "Wind Direction 100m (°)": request.form.get('wind_direction_100m')
    # }

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

    # Get current date and time (separate date and time)
    now = datetime.now()
    current_date = now.strftime("%d-%m-%Y")
    current_time = now.strftime("%H:%M:%S")

    return render_template(
        'report.html',
        report=report,
        data=data,
        current_date=current_date,
        current_time=current_time
    )

if __name__ == "__main__":
    app.run(debug=True)
