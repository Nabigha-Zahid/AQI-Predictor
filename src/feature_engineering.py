
import os
import pandas as pd

INPUT_FILE = "data/processed/historical_dataset_6months.csv"
OUTPUT_FILE = "data/processed/features_6months.csv"

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True
)

df = df.sort_values(
    ["city", "timestamp"]
).reset_index(drop=True)

df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek
df["month"] = df["timestamp"].dt.month

df["aqi_lag_1"] = (
    df.groupby("city")["aqi"]
    .shift(1)
)

df["aqi_lag_3"] = (
    df.groupby("city")["aqi"]
    .shift(3)
)

df["aqi_lag_6"] = (
    df.groupby("city")["aqi"]
    .shift(6)
)

df["aqi_lag_24"] = (
    df.groupby("city")["aqi"]
    .shift(24)
)

df["pm2_5_lag_1"] = (
    df.groupby("city")["pm2_5"]
    .shift(1)
)

df["pm10_lag_1"] = (
    df.groupby("city")["pm10"]
    .shift(1)
)

df["target_aqi"] = (
    df.groupby("city")["aqi"]
    .shift(-1)
)

df = df.dropna().reset_index(drop=True)

os.makedirs(
    "data/processed",
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Feature engineering completed.")
print(f"Records: {len(df)}")
print(f"Features: {len(df.columns)}")
print(f"Saved to: {OUTPUT_FILE}")

