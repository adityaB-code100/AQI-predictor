
from flask import Flask, render_template, request,jsonify
import statistics,math
from datetime import datetime
from get_map import mapgenerator
from data_function import next_seven_days
from get_from_db import get_aqi_data ,get_aqi_by_village # your function from previous step
import pandas as pd
import numpy as np
from filter_function import filter_off,classify_pollutants
from data_graph import create_aqi_forecast_chart
app = Flask(__name__)

def get_current_date():
    # Format: YYYY-MM-DD
    return datetime.now().strftime("%Y-%m-%d")

@app.route('/dashbord', methods=['GET', 'POST'])
def index_route():
    aqi_list = []
    mean_list = []
    paired_data = []
    pollutant_data = {}
    avg_aqi_7_days=None
    worst_aqi=None
    best_aqi=None
    avg_3card_dict={}
    avg_3date_dict={}
    passing_data={}
    pollutants=None
    pm_list=[]
    if request.method == 'POST':
        village = request.form.get('village')
        date = request.form.get('date')
        date_list = next_seven_days(date)
        print(date_list)  # Get next 7 days including this one

        for date_i in date_list:
            # Fetch AQI data from MongoDB for this date and village
            #print(date_i,village)
            data = get_aqi_data(date_i, village=village)
            #print(data)
            if data:
                mean_list.append(data)
                # For average AQI card
                if 'Predicted_AQI' in data:
                    aqi_list.append(data['Predicted_AQI'])
                    print(data['Predicted_AQI'])

                if 'PM2.5' in data:
                    pm_list.append(data['PM2.5'])
                    print("pm2.3",data['PM2.5'])
            else:

                print(f"No data found for {village} on {date_i}")

        data = get_aqi_data(date, village=village)
        print(data)
        pollutants=classify_pollutants(filter_off(data))
        print(pollutants)
        # Get AQI by village (for map)
        village_aqi_data = get_aqi_by_village(date)
        print(village_aqi_data )


        # Average AQI for 7 days
        if aqi_list and not math.isnan(np.mean(aqi_list)):
            avg_aqi_7_days = int(np.mean(aqi_list))
        else:
            avg_aqi_7_days = None

        # Worst AQI
        if aqi_list:
            worst_aqi = np.max(aqi_list)
        else:
            worst_aqi = None

        # Best AQI (cleaning out None/NaN first)
        aqi_clean = [x for x in aqi_list if x is not None and not np.isnan(x)]
        if aqi_clean:
            best_aqi = np.min(aqi_clean)
        else:
            best_aqi = None

        print(worst_aqi, best_aqi, "aqi")
        print("avg", avg_aqi_7_days)

        # Generate map if we have AQI data
        if village_aqi_data:
           mapgenerator(village_aqi_data)

        # Build paired data safely
        if aqi_list and date_list:
            paired_data = dict(zip(aqi_list, date_list))

        # Fill 3-card dictionary safely
        if worst_aqi in paired_data:
            avg_3card_dict['worst_aqi'] = paired_data[worst_aqi]
        else:
            avg_3card_dict['worst_aqi'] = None

        if best_aqi in paired_data:
            avg_3card_dict['best_aqi'] = paired_data[best_aqi]
        else:
            avg_3card_dict['best_aqi'] = None

        print(avg_3card_dict)
        print(paired_data)

        # Default pollutant data
        pollutant_data = mean_list[0] if mean_list else None
        passing_data = dict(zip(date_list,aqi_list))
        passing_pollutant = dict(zip(date_list,pm_list))

        print(passing_data)
       
        graph_html = create_aqi_forecast_chart(date_list, aqi_list)


        # Render template
        return render_template(
            'aqi.html',
            passing_data=passing_data,
            avg_3card_dict=avg_3card_dict,
            avg_aqi_7_days=avg_aqi_7_days,
            worst_aqi=worst_aqi,
            best_aqi=best_aqi,
            pollutants=pollutants,
            passing_pollutant=passing_pollutant,
             graph_html=graph_html,
                 village=village


            
        )







@app.route("/save_coords", methods=["POST"])
def save_coords():
    data = request.json
    lat = data.get("lat")
    lng = data.get("lng")

    print(f"Received coordinates: {lat}, {lng}")  # <-- You can save to DB instead

    return jsonify({"status": "success", "lat": lat, "lng": lng})





@app.route('/')
def Home_page():
    aqi_list = []
    mean_list = []
    paired_data = []
    pollutant_data = {}
    avg_aqi_7_days=None
    worst_aqi=None
    best_aqi=None
    avg_3card_dict={}
    avg_3date_dict={}
    passing_data={}
    pollutants=None
    pm_list=[]
    date = get_current_date()
    village='VillageA'

    if date:
        
        date_list = next_seven_days(date)
        print(date_list)  # Get next 7 days including this one

        for date_i in date_list:
            # Fetch AQI data from MongoDB for this date and village
            #print(date_i,village)
            data = get_aqi_data(date_i, village=village)
            #print(data)
            if data:
                mean_list.append(data)
                # For average AQI card
                if 'Predicted_AQI' in data:
                    aqi_list.append(data['Predicted_AQI'])
                    print(data['Predicted_AQI'])

                if 'PM2.5' in data:
                    pm_list.append(data['PM2.5'])
                    print("pm2.3",data['PM2.5'])
            else:

                print(f"No data found for {village} on {date_i}")

        data = get_aqi_data(date, village=village)
        print(data)
        pollutants=classify_pollutants(filter_off(data))
        print(pollutants)
        # Get AQI by village (for map)
        village_aqi_data = get_aqi_by_village(date)
        print(village_aqi_data )


        # Average AQI for 7 days
        if aqi_list and not math.isnan(np.mean(aqi_list)):
            avg_aqi_7_days = int(np.mean(aqi_list))
        else:
            avg_aqi_7_days = None

        # Worst AQI
        if aqi_list:
            worst_aqi = np.max(aqi_list)
        else:
            worst_aqi = None

        # Best AQI (cleaning out None/NaN first)
        aqi_clean = [x for x in aqi_list if x is not None and not np.isnan(x)]
        if aqi_clean:
            best_aqi = np.min(aqi_clean)
        else:
            best_aqi = None

        print(worst_aqi, best_aqi, "aqi")
        print("avg", avg_aqi_7_days)

        # Generate map if we have AQI data
        if village_aqi_data:
           mapgenerator(village_aqi_data)

        # Build paired data safely
        if aqi_list and date_list:
            paired_data = dict(zip(aqi_list, date_list))

        # Fill 3-card dictionary safely
        if worst_aqi in paired_data:
            avg_3card_dict['worst_aqi'] = paired_data[worst_aqi]
        else:
            avg_3card_dict['worst_aqi'] = None

        if best_aqi in paired_data:
            avg_3card_dict['best_aqi'] = paired_data[best_aqi]
        else:
            avg_3card_dict['best_aqi'] = None

        print(avg_3card_dict)
        print(paired_data)

        # Default pollutant data
        pollutant_data = mean_list[0] if mean_list else None
        passing_data = dict(zip(date_list,aqi_list))
        passing_pollutant = dict(zip(date_list,pm_list))

        print(passing_data)
       
        graph_html = create_aqi_forecast_chart(date_list, aqi_list)


        # Render template
        return render_template(
            'aqi.html',
            passing_data=passing_data,
            avg_3card_dict=avg_3card_dict,
            avg_aqi_7_days=avg_aqi_7_days,
            worst_aqi=worst_aqi,
            best_aqi=best_aqi,
            pollutants=pollutants,
            passing_pollutant=passing_pollutant,
             graph_html=graph_html,
             date = date,
    village=village
            
        )





if __name__ == "__main__":
    app.run(debug=True)
