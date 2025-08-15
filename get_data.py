

import pandas as pd
from model import predict_aqi_from_csv

def get_file_train(train_village):
    train_dict = {
        "VillageA": r"E:\Enginnering\Projects\AQI VIsuliser\Data_set\Training data\abc.csv",
         "VillageB": r"E:\Enginnering\Projects\AQI VIsuliser\Data_set\Training data\abc.csv",
          "VillageC": r"E:\Enginnering\Projects\AQI VIsuliser\Data_set\Training data\abc.csv"
    }
    return train_dict[train_village]

def get_file_input(input_village):
    input_dict = {
        "VillageA": r"E:\Enginnering\Projects\AQI VIsuliser\Data_set\input_data\abcd.csv",
        "VillageB": r"E:\Enginnering\Projects\AQI VIsuliser\Data_set\input_data\abcd.csv",
        "VillageC": r"E:\Enginnering\Projects\AQI VIsuliser\Data_set\input_data\abcd.csv"
    
    }
    return input_dict[input_village]


def get_data_by_date(village, input_date):
    """
    Filters rows from CSV that match the input date and returns DataFrame
    with Predicted_AQI column.
    """
    input_file=get_file_input(village)
    train_file=get_file_train(village)

    df = pd.read_csv(input_file, encoding="utf-8")

    # Clean timestamp column
    df['Timestamp'] = df['Timestamp'].astype(str).str.strip()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y %H:%M', errors='coerce')

    # Convert input date to datetime (assumes HTML input gives YYYY-MM-DD)
    search_date = pd.to_datetime(input_date, format='%d-%m-%Y', errors='coerce')

    # Filter rows for that date
    filtered_df = df[df['Timestamp'].dt.date == search_date.date()]
    filtered_df = filtered_df.sort_values(by='Timestamp')

    #print('Filtered data for prediction:\n', filtered_df)

    if filtered_df.empty:
        return pd.DataFrame()  # Empty DataFrame instead of None

    return predict_aqi_from_csv(train_file, filtered_df)


#get_data_by_date('VillageA', '12-02-2025')