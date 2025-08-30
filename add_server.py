#This File is made to add data
from get_data import get_data_by_date
import statistics
from get_map import mapgenerator
from data_for_server import next_days
from data_function import next_seven_days
import pandas as pd
from testc import save_aqi_to_mongo   # <-- updated function from before
from avg import calculate_and_store_monthly_mean_aqi
from processing import index2
def index():
    start_date = '2025-08-29'
    date_list = next_days(start_date)
    village_list = ['Mumbai', 'Nagpur','Nanded','Nashik','Pune']   # Add more if needed

    for village in village_list:
        avg_list = []
        mean_list = []

        for date_i in date_list:
            df = get_data_by_date(village, date_i)

            if not df.empty and 'Predicted_AQI' in df.columns:
                # Average AQI for this date
                avg = int(statistics.mean(df['Predicted_AQI']))
                avg_list.append(avg)

                # Compute all numeric column means for this date
                mean_dict = {}
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]) and col.lower() != 'time':
                        col_mean = df[col].mean()
                        if pd.notna(col_mean):
                            mean_dict[col.replace("(ug/m³)", "").replace("(°C)", "").replace("(%)", "").strip() ] = int(col_mean)

                # Store date in dict
                mean_dict['date'] = date_i
                mean_list.append(mean_dict)

            else:
                print(f"⚠️ No predictions available for {village} on {date_i}.")

        # Debug print
        print(f"\n✅ Processed data for {village}:")
        #print(mean_list)
        calculate_and_store_monthly_mean_aqi()
        # Save to MongoDB (new format: one document per date, inside 'data' each village)
        if mean_list:
            save_aqi_to_mongo(mean_list, city=village)



           # Optional: map for first avg only
    # if avg_list:
    #         mapgenerator({village: avg_list[0]})
        
    index2()
if __name__ == "__main__":
    index()
