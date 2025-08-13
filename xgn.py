import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import joblib  # for saving and loading models

# ----------------------------
# Step 1: Load datasets
# ----------------------------
train_df = pd.read_csv("abc.csv")
predict_df = pd.read_csv("abcd.csv")

# ----------------------------
# Step 2: Data Cleaning
# ----------------------------

# Remove duplicates
train_df = train_df.drop_duplicates()

# Handle missing values
train_df = train_df.ffill().bfill()
predict_df = predict_df.ffill().bfill()

# Process Timestamp
if 'Timestamp' in train_df.columns:
    train_df['Timestamp'] = pd.to_datetime(train_df['Timestamp'], dayfirst=True)
    start_time = train_df['Timestamp'].min()
    train_df['time_seconds'] = (train_df['Timestamp'] - start_time).dt.total_seconds()
    train_df = train_df.drop(columns=['Timestamp'])

if 'Timestamp' in predict_df.columns:
    predict_df['Timestamp'] = pd.to_datetime(predict_df['Timestamp'], dayfirst=True)
    predict_df['time_seconds'] = (predict_df['Timestamp'] - start_time).dt.total_seconds()
    predict_df = predict_df.drop(columns=['Timestamp'])

# ----------------------------
# Step 3: Feature & Target Split
# ----------------------------
pollutant_cols = [col for col in train_df.columns if col != 'AQI']
X = train_df[pollutant_cols]
y = train_df['AQI']

# ----------------------------
# Step 4: Train-Test Split
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ----------------------------
# Step 5: Train XGBoost Model
# ----------------------------
model = xgb.XGBRegressor(
    objective='reg:squarederror',
    eval_metric='rmse',
    n_estimators=200,
    learning_rate=0.1,
    max_depth=6,
    random_state=42
)

model.fit(X_train, y_train)

# ----------------------------
# Step 6: Evaluate
# ----------------------------
y_pred = model.predict(X_test)
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
print(f"R² Score: {r2_score(y_test, y_pred):.2f}")

# ----------------------------
# Step 7: Save the trained model
# ----------------------------
joblib.dump(model, "xgb_aqi_model.joblib")
joblib.dump(pollutant_cols, "feature_columns.joblib")  # save feature order for prediction
print("Model saved as 'xgb_aqi_model.joblib' and features saved as 'feature_columns.joblib'")

# ----------------------------
# Step 8: Predict for New Data
# ----------------------------
predicted_aqi = model.predict(predict_df[pollutant_cols])
predict_df['Predicted_AQI'] = predicted_aqi

# Save results
predict_df.to_csv("predicted_aqi.csv", index=False)
print("Prediction saved to 'predicted_aqi.csv'")
