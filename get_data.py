

import pandas as pd
from model import predict_aqi_from_csv

def get_data_by_date(csv_file='abcd.csv', input_date='12-08-2024'):
    """
    Filters rows from CSV that match the input date and returns DataFrame
    with Predicted_AQI column.
    """
    df = pd.read_csv(csv_file)

    # Clean timestamp column
    df['Timestamp'] = df['Timestamp'].astype(str).str.strip()
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%d-%m-%Y %H:%M', errors='coerce')

    # Convert input date to datetime (assumes HTML input gives YYYY-MM-DD)
    search_date = pd.to_datetime(input_date, format='%Y-%m-%d', errors='coerce')

    # Filter rows for that date
    filtered_df = df[df['Timestamp'].dt.date == search_date.date()]
    filtered_df = filtered_df.sort_values(by='Timestamp')

    print('Filtered data for prediction:\n', filtered_df)

    if filtered_df.empty:
        return pd.DataFrame()  # Empty DataFrame instead of None

    return predict_aqi_from_csv('abc.csv', filtered_df)
