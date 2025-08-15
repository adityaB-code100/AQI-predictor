
from flask import Flask, render_template, request
from get_data import get_data_by_date
import statistics
from get_map import mapgenerator
from data_function import next_seven_days

app = Flask(__name__)

@app.route('/p', methods=['GET', 'POST'])
def index():
    avg = None
    avg_list=[]
    if request.method == 'POST':
        village = request.form.get('village')

        date = request.form.get('date')
        #print("Selected date:", date)
        date_list=next_seven_days(date)
        #print(date_list)
        # This returns a DataFrame with Predicted_AQI column
       
        for date_i in date_list:
            df = get_data_by_date(village, date_i)
            #print("Predicted rows:\n", df)

            if not df.empty and 'Predicted_AQI' in df.columns:
                avg = statistics.mean(df['Predicted_AQI'])
                avg=int(avg)
                #print("Average AQI:", avg)
                avg_list.append(avg)
            else:
                print("No predictions available for this date.")
        
        mapgenerator(avg_list[0])
        paired_data = zip(avg_list, date_list)  # creates tuples (avg, date)

    return render_template('index4.html', paired_data=paired_data)

@app.route('/')
def home():
    return render_template("index2.html")

if __name__ == "__main__":
    app.run(debug=True)
