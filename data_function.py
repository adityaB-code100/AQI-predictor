from datetime import datetime, timedelta

def next_seven_days(start_date_str):
    # Parse HTML date format (YYYY-MM-DD)
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    
    # Return dates in DD-MM-YYYY format
    date_list = [(start_date + timedelta(days=i)).strftime("%d-%m-%Y") for i in range(7)]
    return date_list
