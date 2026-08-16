
import os
import requests
import pandas as pd
from datetime import datetime, timedelta

CITIES = {
    "Lahore": (31.5497, 74.3436),
    "Islamabad": (33.7104, 73.1338),
    "Karachi": (24.9056, 67.0822)
}

URL = "https://archive-api.open-meteo.com/v1/archive"

START_DATE = "2026-02-16"
END_DATE = "2026-08-15"

OUTPUT_DIR = "data/historical"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "historical_weather_6months.csv"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

records = []

for city, (latitude, longitude) in CITIES.items():

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "surface_pressure,"
            "wind_speed_10m"
        ),
        "timezone": "UTC",
        "temperature_unit": "celsius",
        "wind_speed_unit": "ms"
    }

    response = requests.get(
        URL,
        params=params,
        timeout=60
    )

    if response.status_code != 200:
        print(f"API Error for {city}: {response.status_code}")
        print(response.text)
        continue

    data = response.json()
    hourly = data["hourly"]

    for i in range(len(hourly["time"])):

        records.append({
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": hourly["time"][i],
            "temperature": hourly["temperature_2m"][i],
            "humidity": hourly["relative_humidity_2m"][i],
            "pressure": hourly["surface_pressure"][i],
            "wind_speed": hourly["wind_speed_10m"][i]
        })

    print(
        f"{city}: "
        f"{len(hourly['time'])} weather records collected"
    )

df = pd.DataFrame(records)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True
)

df = df.drop_duplicates(
    subset=["city", "timestamp"]
)

df = df.sort_values(
    ["city", "timestamp"]
).reset_index(drop=True)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nHistorical weather collection completed.")
print(f"Cities: {df['city'].nunique()}")
print(f"Records: {len(df)}")
print(f"Start: {df['timestamp'].min()}")
print(f"End: {df['timestamp'].max()}")
print(f"Saved to: {OUTPUT_FILE}")

