
from flask import Flask, render_template, request
from get_data import get_data_by_date
import statistics
from get_map import mapgenerator
from data_function import next_seven_days
import pandas as pd


app = Flask(__name__)

@app.route('/p', methods=['GET', 'POST'])
def index():
    avg_list = []
    mean_list = []

    if request.method == 'POST':
        village = request.form.get('village')
        date = request.form.get('date')
        date_list = next_seven_days(date)

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
                            mean_dict[col + '_mean'] = int(col_mean)

                # Optional: store the date in the dict
                mean_dict['date'] = date_i

                mean_list.append(mean_dict)
            else:
                print("No predictions available for this date.")

        if avg_list:
            mapgenerator(avg_list[0])

        paired_data = zip(avg_list, date_list)        # for AQI cards
        pollutant_data = mean_list[0]     
        #print(mean_list)              # pass the list of dictionaries directly

    else:
        paired_data = []
        pollutant_data = mean_list[0]

    return render_template('index4.html',     pollutant_data=pollutant_data   ,paired_data=paired_data)
                           #mean_list=mean_list,date_list=date_list)

@app.route('/')
def home():
    return render_template("index2.html")

if __name__ == "__main__":
    app.run(debug=True)
