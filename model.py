# import pandas as pd
# import numpy as np
# import xgboost as xgb
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import mean_squared_error, r2_score

# def predict_aqi_from_csv(train_csv, input_df,save_model_path='xgb_aqi_model.joblib'):
#     """
#     Train AQI model from train_csv and predict AQI for input_df.

#     Parameters:
#     - train_csv: path to training CSV with AQI column
#     - input_df: pandas DataFrame with same features as train_csv (except AQI)

#     Returns:
#     - input_df with a new column 'Predicted_AQI'
#     """
#     # ----------------------------
#     # Load training data
#     # ----------------------------
#     train_df = pd.read_csv(train_csv)

#     # Clean data
#     train_df = train_df.drop_duplicates().ffill().bfill()
#     input_df = input_df.ffill().bfill()

#     # Process Timestamp
#     if 'Timestamp' in train_df.columns:
#         train_df['Timestamp'] = pd.to_datetime(train_df['Timestamp'], format='%d-%m-%Y %H:%M')
#         start_time = train_df['Timestamp'].min()
#         train_df['time_seconds'] = (train_df['Timestamp'] - start_time).dt.total_seconds()
#         train_df = train_df.drop(columns=['Timestamp'])

#     if 'Timestamp' in input_df.columns:
#         input_df['Timestamp'] = pd.to_datetime(input_df['Timestamp'], format='%d-%m-%Y %H:%M')
#         input_df['time_seconds'] = (input_df['Timestamp'] - start_time).dt.total_seconds()
#         input_df = input_df.drop(columns=['Timestamp'])

#     # ----------------------------
#     # Feature & target split
#     # ----------------------------
#     feature_cols = [col for col in train_df.columns if col != 'AQI']
#     X = train_df[feature_cols]
#     y = train_df['AQI']

#     # ----------------------------
#     # Train XGBoost
#     # ----------------------------
#     model = xgb.XGBRegressor(
#         objective='reg:squarederror',
#         eval_metric='rmse',
#         n_estimators=200,
#         learning_rate=0.1,
#         max_depth=6,
#         random_state=42
#     )
#     model.fit(X, y)

#     # ----------------------------
#     # Predict for input_df
#     # ----------------------------
#     input_df['Predicted_AQI'] = model.predict(input_df[feature_cols])
#     print( input_df['Predicted_AQI'])
#     return input_df
import pandas as pd
import xgboost as xgb

def predict_aqi_from_csv(train_csv, input_df, save_model_path='xgb_aqi_model.joblib'):
    """
    Train AQI model from train_csv and predict AQI for input_df.
    Returns DataFrame with new column 'Predicted_AQI'.
    """
    # Load and clean training data
    train_df = pd.read_csv(train_csv).drop_duplicates().ffill().bfill()
    input_df = input_df.ffill().bfill()

    # Process Timestamp → numeric feature
    if 'Timestamp' in train_df.columns:
        train_df['Timestamp'] = pd.to_datetime(train_df['Timestamp'], format='%d-%m-%Y %H:%M', errors='coerce')
        start_time = train_df['Timestamp'].min()
        train_df['time_seconds'] = (train_df['Timestamp'] - start_time).dt.total_seconds()
        train_df.drop(columns=['Timestamp'], inplace=True)

    if 'Timestamp' in input_df.columns:
        input_df['Timestamp'] = pd.to_datetime(input_df['Timestamp'], format='%d-%m-%Y %H:%M', errors='coerce')
        input_df['time_seconds'] = (input_df['Timestamp'] - start_time).dt.total_seconds()
        input_df.drop(columns=['Timestamp'], inplace=True)

    # Split features & target
    feature_cols = [col for col in train_df.columns if col != 'AQI']
    X_train = train_df[feature_cols]
    y_train = train_df['AQI']

    # Train XGBoost model
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        eval_metric='rmse',
        n_estimators=200,
        learning_rate=0.1,
        max_depth=6,
        random_state=42
    )
    model.fit(X_train, y_train)

    # Predict
    input_df['Predicted_AQI'] = model.predict(input_df[feature_cols])
    print("Predictions:\n", input_df['Predicted_AQI'])

    return input_df
