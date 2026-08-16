
import os
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found in .env")

CITIES = {
    "Lahore": (31.5497, 74.3436),
    "Islamabad": (33.7104, 73.1338),
    "Karachi": (24.9056, 67.0822)
}

URL = "https://api.openweathermap.org/data/2.5/air_pollution/history"

END_DATE = datetime.now(timezone.utc)
START_DATE = END_DATE - timedelta(days=180)

OUTPUT_DIR = "data/historical"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_city_data(city, latitude, longitude):
    records = []
    current_start = START_DATE

    while current_start < END_DATE:
        current_end = min(
            current_start + timedelta(hours=24),
            END_DATE
        )

        params = {
            "lat": latitude,
            "lon": longitude,
            "start": int(current_start.timestamp()),
            "end": int(current_end.timestamp()),
            "appid": API_KEY
        }

        response = requests.get(
            URL,
            params=params,
            timeout=30
        )

        if response.status_code != 200:
            print(
                f"API Error: {city} "
                f"{response.status_code}: {response.text}"
            )
            current_start = current_end
            continue

        data = response.json()

        for item in data.get("list", []):
            components = item["components"]

            records.append({
                "city": city,
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": datetime.fromtimestamp(
                    item["dt"],
                    tz=timezone.utc
                ).isoformat(),
                "aqi": item["main"]["aqi"],
                "co": components["co"],
                "no": components["no"],
                "no2": components["no2"],
                "o3": components["o3"],
                "so2": components["so2"],
                "pm2_5": components["pm2_5"],
                "pm10": components["pm10"],
                "nh3": components["nh3"]
            })

        print(
            f"{city}: "
            f"{current_start.date()} to {current_end.date()} "
            f"| Records: {len(records)}"
        )

        current_start = current_end
        time.sleep(1)

    return records


all_records = []

for city, (latitude, longitude) in CITIES.items():
    city_records = fetch_city_data(
        city,
        latitude,
        longitude
    )

    all_records.extend(city_records)


df = pd.DataFrame(all_records)

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

output_file = os.path.join(
    OUTPUT_DIR,
    "historical_pollution_6months.csv"
)

df.to_csv(
    output_file,
    index=False
)

print("\nHistorical pollution collection completed.")
print(f"Cities: {df['city'].nunique()}")
print(f"Records: {len(df)}")
print(f"Start: {df['timestamp'].min()}")
print(f"End: {df['timestamp'].max()}")
print(f"Saved to: {output_file}")

