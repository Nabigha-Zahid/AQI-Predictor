
import os
import pandas as pd

INPUT_FILE = "data/processed/training_data_6months.csv"
OUTPUT_FILE = "data/processed/live_history.csv"

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True
)

df = df.sort_values(
    ["city", "timestamp"]
).reset_index(drop=True)

# Keep the latest 24 observations for each city.
# These observations are needed for lag features.
history = (
    df.groupby("city", group_keys=False)
      .tail(24)
      .copy()
)

history = history[
    [
        "city",
        "timestamp",
        "aqi",
        "pm2_5",
        "pm10"
    ]
]

os.makedirs(
    "data/processed",
    exist_ok=True
)

history.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Live history prepared.")
print(f"Records: {len(history)}")
print(f"Cities: {history['city'].nunique()}")
print(f"Saved to: {OUTPUT_FILE}")

print("\nRecords per city:")
print(history["city"].value_counts())

