from flask import Flask, request, redirect, url_for, session, render_template, flash, jsonify,render_template_string
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from functools import wraps
from Fastserver import save_or_update_data
# AQI imports
import statistics, math
from datetime import datetime
import pandas as pd
import numpy as np
from get_map import mapgenerator
from data_function import next_seven_days
from get_from_db import get_aqi_data, get_aqi_by_village
from filter_function import filter_off, classify_pollutants
from data_graph import create_aqi_forecast_chart
from get_avg_graph import plot_monthly_aqi
from get_user import get_data
from data_for_server import next_days

app = Flask(__name__)


def index2():
    start_date = '2025-09-04'
    date_list = next_days(start_date)
    village_list = ['Mumbai','Nagpur','Nanded','Nashik','Pune']   # Add more if needed
    for village in village_list:

        for date_i in date_list:
            print(date_i,village)
            processing_data(date_i,village)





def processing_data(input_date,village):
    aqi_list, mean_list, pm_list = [], [], []
    avg_aqi_7_days = worst_aqi = best_aqi = None
    avg_3card_dict, passing_data, pollutants = {}, {}, None
    date_list = next_seven_days(input_date)
    print(date_list)

    
    for date_k in date_list:
        data = get_aqi_data(date_k, village=village)
        if data:
            mean_list.append(data)
            if "Predicted_AQI" in data:
                aqi_list.append(data["Predicted_AQI"])
            if "PM2.5" in data:
                pm_list.append(data["PM2.5"])

    data = get_aqi_data(input_date, village=village)
    if data:
        pollutants = classify_pollutants(filter_off(data))

    village_aqi_data = get_aqi_by_village(input_date)
    print(village_aqi_data)

#Map Generation

    if village_aqi_data:
        mapgenerator(input_date,village_aqi_data)
        
    if aqi_list:
        # Remove None and NaN values
        clean_values = [x for x in aqi_list if x is not None and not math.isnan(x)]
        print(clean_values)
        if clean_values:  # only if we have valid values
            avg_aqi_7_days = sum(clean_values) // (len(clean_values)+1) # integer average
            worst_aqi = max(clean_values)
            best_aqi = min(clean_values)
    print(worst_aqi,best_aqi)

    paired_data = dict(zip(aqi_list, date_list))
    avg_3card_dict["worst_aqi"] = paired_data.get(worst_aqi)
    avg_3card_dict["best_aqi"] = paired_data.get(best_aqi)
    print("printing dict",avg_3card_dict)
   # Keep aligned lists using index

    record=[]
    for date_p, value in zip(date_list, aqi_list):
        record.append({"date": date_p, "value": value})

    passing_data=record
    record1=[]
    for date_p, value in zip(date_list, pm_list):
            record1.append({"date": date_p, "value": value})

    passing_pollutant=record1

    

    graph_html = create_aqi_forecast_chart(date_list, aqi_list)
    avg_graph=plot_monthly_aqi(village)


    data_dict = {
    "date": input_date,
    "village": village,
    "passing_data": passing_data,
    "avg_3card_dict": avg_3card_dict,
    "avg_aqi_7_days": avg_aqi_7_days,
    "pollutants": pollutants,
    "passing_pollutant": passing_pollutant,
    "graph_html": graph_html,
    "avg_graph": avg_graph,
    "worst_aqi":worst_aqi,
    "best_aqi":best_aqi,
    "date_list":date_list,
    "village_aqi_data": village_aqi_data
}
    #save_aqi_to_mongo(records, city, mongo_uri="mongodb://localhost:27017/", db_name="AQI_Project", collection_name="processed_data")
    save_or_update_data(input_date,village,data_dict)

    print(f" process for {input_date} village {village}")

#processing_data("12-08-2025",'Pune')


index2()