
import os
import pandas as pd

POLLUTION_FILE = "data/historical/historical_pollution_6months.csv"
WEATHER_FILE = "data/historical/historical_weather_6months.csv"
OUTPUT_FILE = "data/processed/historical_dataset_6months.csv"

pollution = pd.read_csv(POLLUTION_FILE)
weather = pd.read_csv(WEATHER_FILE)

pollution["timestamp"] = pd.to_datetime(
    pollution["timestamp"],
    utc=True
)

weather["timestamp"] = pd.to_datetime(
    weather["timestamp"],
    utc=True
)

pollution = pollution.drop_duplicates(
    subset=["city", "timestamp"]
)

weather = weather.drop_duplicates(
    subset=["city", "timestamp"]
)

merged = pd.merge(
    pollution,
    weather,
    on=["city", "timestamp"],
    how="inner",
    suffixes=("_pollution", "_weather")
)

merged = merged.sort_values(
    ["city", "timestamp"]
).reset_index(drop=True)

os.makedirs(
    "data/processed",
    exist_ok=True
)

merged.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Historical datasets merged successfully.")
print(f"Pollution records: {len(pollution)}")
print(f"Weather records: {len(weather)}")
print(f"Merged records: {len(merged)}")
print(f"Start: {merged['timestamp'].min()}")
print(f"End: {merged['timestamp'].max()}")
print(f"Saved to: {OUTPUT_FILE}")

