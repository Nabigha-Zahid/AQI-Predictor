
import os
import joblib
import pandas as pd


MODEL_FILE = "models/best_aqi_model.joblib"


def predict_aqi(data):
    """
    Generate AQI prediction using the trained Random Forest model.

    data must contain the same feature columns used during training,
    including the lag features.
    """

    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(
            f"Model not found: {MODEL_FILE}"
        )

    model = joblib.load(MODEL_FILE)

    df = pd.DataFrame([data])

    required_columns = [
        "city",
        "latitude_pollution",
        "longitude_pollution",
        "aqi",
        "co",
        "no",
        "no2",
        "o3",
        "so2",
        "pm2_5",
        "pm10",
        "nh3",
        "latitude_weather",
        "longitude_weather",
        "temperature",
        "humidity",
        "pressure",
        "wind_speed",
        "hour",
        "day_of_week",
        "month",
        "aqi_lag_1",
        "aqi_lag_3",
        "aqi_lag_6",
        "aqi_lag_24",
        "pm2_5_lag_1",
        "pm10_lag_1"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required features: {missing}"
        )

    df = df[required_columns]

    prediction = model.predict(df)[0]

    # Convert continuous prediction to AQI category 1-5
    predicted_category = int(
        max(1, min(5, round(prediction)))
    )

    return prediction, predicted_category


if __name__ == "__main__":

    sample_data = {
        "city": "Lahore",
        "latitude_pollution": 31.5497,
        "longitude_pollution": 74.3436,

        "aqi": 3,
        "co": 500.0,
        "no": 5.0,
        "no2": 20.0,
        "o3": 40.0,
        "so2": 5.0,
        "pm2_5": 30.0,
        "pm10": 50.0,
        "nh3": 10.0,

        "latitude_weather": 31.5497,
        "longitude_weather": 74.3436,

        "temperature": 30.0,
        "humidity": 60.0,
        "pressure": 1005.0,
        "wind_speed": 3.0,

        "hour": 12,
        "day_of_week": 3,
        "month": 8,

        "aqi_lag_1": 3.0,
        "aqi_lag_3": 3.0,
        "aqi_lag_6": 4.0,
        "aqi_lag_24": 3.0,

        "pm2_5_lag_1": 28.0,
        "pm10_lag_1": 48.0
    }

    prediction, category = predict_aqi(
        sample_data
    )

    print("=" * 40)
    print("AQI PREDICTION")
    print("=" * 40)

    print(
        f"Predicted AQI value: {prediction:.2f}"
    )

    print(
        f"Predicted AQI category: {category}"
    )
