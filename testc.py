import pandas as pd

df = pd.read_csv('abcd.csv')

# Print first few rows and column names
print(df.head())
print(df.columns)
print(df['Timestamp'].head())
