
import os
base_dir = os.path.dirname(os.path.abspath(__file__))

import pandas as pd
from predication_model import predict_aqi_from_csv
def get_file_train(train_village):
    train_dict = {
        "Mumbai": os.path.join(base_dir, 'Data_set', 'Training_data', 'Mumbai_train.csv'),
        "Nagpur": os.path.join(base_dir, 'Data_set', 'Training_data', 'Nagpur_train.csv'),
          "Nanded": os.path.join(base_dir, 'Data_set', 'Training_data', 'Nanded_train.csv'),
        "Nashik": os.path.join(base_dir, 'Data_set', 'Training_data', 'Nashik_train.csv'),
          "Pune": os.path.join(base_dir, 'Data_set', 'Training_data', 'Pune_train.csv')


        # Add more villages here if needed
    }
    return train_dict[train_village]

def get_file_input(input_village):
    input_dict = {
        "Mumbai": os.path.join(base_dir, 'Data_set', 'input_data', 'Mumbai.csv'),
        "Nagpur": os.path.join(base_dir, 'Data_set', 'input_data', 'Nagpur.csv'),
          "Nanded": os.path.join(base_dir, 'Data_set', 'input_data', 'Nanded.csv'),
        "Nashik": os.path.join(base_dir, 'Data_set', 'input_data', 'Nashik.csv'),
          "Pune": os.path.join(base_dir, 'Data_set', 'input_data', 'Pune.csv')


        # Add more villages if needed
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

    print('Filtered data for prediction:\n', filtered_df)

    if filtered_df.empty:
        return pd.DataFrame()  # Empty DataFrame instead of None

    return predict_aqi_from_csv(train_file, filtered_df)


#get_data_by_date('Mumbai', '12-02-2025')