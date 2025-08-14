
from flask import Flask, render_template, request
from get_data import get_data_by_date
import statistics
from chagefinal import mapgenerator

app = Flask(__name__)

@app.route('/p', methods=['GET', 'POST'])
def index():
    avg = None
    if request.method == 'POST':
        date = request.form.get('date')
        print("Selected date:", date)

        # This returns a DataFrame with Predicted_AQI column
        df = get_data_by_date('abcd.csv', date)
        print("Predicted rows:\n", df)

        if not df.empty and 'Predicted_AQI' in df.columns:
            avg = statistics.mean(df['Predicted_AQI'])
            print("Average AQI:", avg)
        else:
            print("No predictions available for this date.")
        
        mapgenerator(avg)

    return render_template('index3.html', avg=avg)

@app.route('/')
def home():
    return render_template("index2.html")

if __name__ == "__main__":
    app.run(debug=True)
