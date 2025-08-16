
from flask import Flask, render_template, request
import statistics
from get_map import mapgenerator
from data_function import next_seven_days
from get_from_db import get_aqi_data ,get_aqi_by_village # your function from previous step

app = Flask(__name__)

@app.route('/dashbord', methods=['GET', 'POST'])
def index_route():
    avg_list = []
    mean_list = []
    paired_data = []
    pollutant_data = {}

    if request.method == 'POST':
        village = request.form.get('village')
        date = request.form.get('date')
        date_list = next_seven_days(date)  # Get next 7 days including this one

        for date_i in date_list:
            # Fetch AQI data from MongoDB for this date and village
            data = get_aqi_data(date_i, village=village)

            if data:
                mean_list.append(data)
                # For average AQI card
                if 'Predicted_AQI_mean' in data:
                    avg_list.append(data['Predicted_AQI_mean'])
                    #print(data['Predicted_AQI_mean'])
            else:
                print(f"No data found for {village} on {date_i}")
        village_aqi_data = get_aqi_by_village(date)

        if avg_list:
            # Generate map for the first date's AQI
            mapgenerator(village_aqi_data)

        paired_data = zip(avg_list, date_list)  # For AQI cards
        if mean_list:
            pollutant_data = mean_list[0]  # Show first day's data by default

    # GET request or no data fallback
    return render_template(
        'index6.html',
        pollutant_data=pollutant_data,
        paired_data=paired_data
    )

@app.route('/')
def home():
    return render_template("index2.html")

if __name__ == "__main__":
    app.run(debug=True)
