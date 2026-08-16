import os
import joblib
import requests
import pandas as pd

from dotenv import load_dotenv



load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

MODEL_FILE = "models/best_aqi_model.joblib"
HISTORY_FILE = "data/processed/live_history.csv"


CITIES = {
    "Lahore": {
        "lat": 31.5497,
        "lon": 74.3436
    },
    "Islamabad": {
        "lat": 33.7104,
        "lon": 73.1338
    },
    "Karachi": {
        "lat": 24.9056,
        "lon": 67.0822
    }
}


if not OPENWEATHER_API_KEY:
    raise ValueError(
        "OPENWEATHER_API_KEY not found in .env"
    )

if not os.path.exists(MODEL_FILE):
    raise FileNotFoundError(
        f"Model not found: {MODEL_FILE}"
    )

if not os.path.exists(HISTORY_FILE):
    raise FileNotFoundError(
        f"History file not found: {HISTORY_FILE}"
    )



model = joblib.load(MODEL_FILE)



history = pd.read_csv(HISTORY_FILE)

history["timestamp"] = pd.to_datetime(
    history["timestamp"],
    utc=True
)


def get_current_pollution(latitude, longitude):

    url = (
        "https://api.openweathermap.org/data/2.5/air_pollution"
    )

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": OPENWEATHER_API_KEY
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    item = data["list"][0]

    components = item["components"]

    return {
        "aqi": item["main"]["aqi"],
        "co": components.get("co", 0),
        "no": components.get("no", 0),
        "no2": components.get("no2", 0),
        "o3": components.get("o3", 0),
        "so2": components.get("so2", 0),
        "pm2_5": components.get("pm2_5", 0),
        "pm10": components.get("pm10", 0),
        "nh3": components.get("nh3", 0)
    }



def get_current_weather(latitude, longitude):

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
    )

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": data["wind"]["speed"]
    }


def get_weather_forecast(latitude, longitude):

    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
    )

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    records = []

    for item in data["list"]:

        timestamp = pd.to_datetime(
            item["dt"],
            unit="s",
            utc=True
        )

        records.append({
            "timestamp": timestamp,
            "temperature": item["main"]["temp"],
            "humidity": item["main"]["humidity"],
            "pressure": item["main"]["pressure"],
            "wind_speed": item["wind"]["speed"]
        })

    return pd.DataFrame(records)



def get_category(prediction):

    return int(
        max(
            1,
            min(
                5,
                round(float(prediction))
            )
        )
    )



def predict_city(city):

    if city not in CITIES:
        raise ValueError(
            f"Unknown city: {city}"
        )

    latitude = CITIES[city]["lat"]
    longitude = CITIES[city]["lon"]

    pollution = get_current_pollution(
        latitude,
        longitude
    )

    weather = get_current_weather(
        latitude,
        longitude
    )

    now = pd.Timestamp.now(tz="UTC")

    city_history = (
        history[
            history["city"] == city
        ]
        .sort_values("timestamp")
    )

    if len(city_history) < 24:
        raise ValueError(
            f"Not enough history for {city}"
        )

    aqi_values = city_history["aqi"].tolist()
    pm25_values = city_history["pm2_5"].tolist()
    pm10_values = city_history["pm10"].tolist()

    features = {

        "city": city,

        "latitude_pollution": latitude,
        "longitude_pollution": longitude,

        "aqi": pollution["aqi"],

        "co": pollution["co"],
        "no": pollution["no"],
        "no2": pollution["no2"],
        "o3": pollution["o3"],
        "so2": pollution["so2"],
        "pm2_5": pollution["pm2_5"],
        "pm10": pollution["pm10"],
        "nh3": pollution["nh3"],

        "latitude_weather": latitude,
        "longitude_weather": longitude,

        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "pressure": weather["pressure"],
        "wind_speed": weather["wind_speed"],

        "hour": now.hour,
        "day_of_week": now.dayofweek,
        "month": now.month,

        "aqi_lag_1": aqi_values[-1],
        "aqi_lag_3": aqi_values[-3],
        "aqi_lag_6": aqi_values[-6],
        "aqi_lag_24": aqi_values[-24],

        "pm2_5_lag_1": pm25_values[-1],
        "pm10_lag_1": pm10_values[-1]
    }

    features_df = pd.DataFrame([features])

    prediction = model.predict(
        features_df
    )[0]

    category = get_category(prediction)

    return {
        "prediction": float(prediction),
        "category": category,

        "pm2_5": float(pollution["pm2_5"]),
        "pm10": float(pollution["pm10"]),
        "co": float(pollution["co"]),
        "no2": float(pollution["no2"]),
        "o3": float(pollution["o3"]),
        "so2": float(pollution["so2"]),
        "nh3": float(pollution["nh3"]),

        "temperature": float(weather["temperature"]),
        "humidity": float(weather["humidity"]),
        "pressure": float(weather["pressure"]),
        "wind_speed": float(weather["wind_speed"])
    }



def predict_next_3_days(city):

    if city not in CITIES:
        raise ValueError(
            f"Unknown city: {city}"
        )

    latitude = CITIES[city]["lat"]
    longitude = CITIES[city]["lon"]


    current_pollution = get_current_pollution(
        latitude,
        longitude
    )


    forecast = get_weather_forecast(
        latitude,
        longitude
    )



    city_history = (
        history[
            history["city"] == city
        ]
        .sort_values("timestamp")
    )

    if len(city_history) < 24:
        raise ValueError(
            f"Not enough history for {city}"
        )

    aqi_values = city_history["aqi"].tolist()
    pm25_values = city_history["pm2_5"].tolist()
    pm10_values = city_history["pm10"].tolist()



    forecast["date"] = (
        forecast["timestamp"]
        .dt.date
    )

    today = pd.Timestamp.now(
        tz="UTC"
    ).date()

    future_forecast = forecast[
        forecast["date"] > today
    ].copy()

    daily_rows = []

    for date, group in future_forecast.groupby("date"):

        if len(group) == 0:
            continue

        target_hour = 12

        group = group.copy()

        group["hour_difference"] = (
            group["timestamp"].dt.hour - target_hour
        ).abs()

        selected = (
            group
            .sort_values("hour_difference")
            .iloc[0]
        )

        daily_rows.append(selected)

    daily_forecast = pd.DataFrame(
        daily_rows
    )


    daily_forecast = (
        daily_forecast
        .sort_values("timestamp")
        .head(3)
    )

    if len(daily_forecast) < 3:
        raise ValueError(
            "OpenWeather did not return enough future "
            "forecast data for 3 days."
        )

    predictions = []



    future_pollution = current_pollution.copy()


    for _, row in daily_forecast.iterrows():

        timestamp = row["timestamp"]

        features = {

            "city": city,

            "latitude_pollution": latitude,
            "longitude_pollution": longitude,

            "aqi": future_pollution["aqi"],

            "co": future_pollution["co"],
            "no": future_pollution["no"],
            "no2": future_pollution["no2"],
            "o3": future_pollution["o3"],
            "so2": future_pollution["so2"],
            "pm2_5": future_pollution["pm2_5"],
            "pm10": future_pollution["pm10"],
            "nh3": future_pollution["nh3"],

            "latitude_weather": latitude,
            "longitude_weather": longitude,

            "temperature": row["temperature"],
            "humidity": row["humidity"],
            "pressure": row["pressure"],
            "wind_speed": row["wind_speed"],

            "hour": timestamp.hour,
            "day_of_week": timestamp.dayofweek,
            "month": timestamp.month,

            "aqi_lag_1": aqi_values[-1],
            "aqi_lag_3": aqi_values[-3],
            "aqi_lag_6": aqi_values[-6],
            "aqi_lag_24": aqi_values[-24],

            "pm2_5_lag_1": pm25_values[-1],
            "pm10_lag_1": pm10_values[-1]
        }

        features_df = pd.DataFrame(
            [features]
        )

        prediction = float(
            model.predict(
                features_df
            )[0]
        )

        category = get_category(
            prediction
        )

        predictions.append({
            "date": str(
                timestamp.date()
            ),
            "predicted_aqi": round(
                prediction,
                2
            ),
            "category": category
        })

  

        aqi_values.append(
            prediction
        )

        pm25_values.append(
            future_pollution["pm2_5"]
        )

        pm10_values.append(
            future_pollution["pm10"]
        )

    return predictions



if __name__ == "__main__":

    print("=" * 60)
    print("AQI PREDICTION")
    print("=" * 60)

    for city in CITIES:

        try:

            result = predict_city(city)

            print(
                f"\n{city}"
            )

            print(
                f"Current AQI: "
                f"{result['prediction']:.2f}"
            )

            print(
                f"Current Category: "
                f"{result['category']}"
            )

            print("\nNext 3 Days:")

            forecast = predict_next_3_days(
                city
            )

            for day in forecast:

                print(
                    f"{day['date']} | "
                    f"AQI: {day['predicted_aqi']} | "
                    f"Category: {day['category']}"
                )

        except Exception as error:

            print(
                f"\n{city} ERROR:"
            )

            print(error)