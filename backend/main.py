
import sys
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)



from src.live_prediction import (
    predict_city,
    predict_next_3_days
)



app = FastAPI(
    title="AQI Prediction API",
    description="Live Air Quality Prediction API",
    version="1.0.0"
)




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



SUPPORTED_CITIES = [
    "Lahore",
    "Islamabad",
    "Karachi"
]


@app.get("/")
def home():

    return {
        "message": "AQI Prediction API is running",
        "status": "online"
    }



@app.get("/predict/{city}")
def predict(city: str):

    city = city.title()

    if city not in SUPPORTED_CITIES:

        raise HTTPException(
            status_code=400,
            detail=(
                "City must be Lahore, Islamabad, or Karachi"
            )
        )

    try:

        result = predict_city(city)

        return {

            "city": city,

            "predicted_aqi": round(
                result["prediction"],
                2
            ),

            "category": result["category"],

            "pollution": {

                "pm2_5": round(
                    result["pm2_5"],
                    2
                ),

                "pm10": round(
                    result["pm10"],
                    2
                ),

                "co": round(
                    result["co"],
                    2
                ),

                "no2": round(
                    result["no2"],
                    2
                ),

                "o3": round(
                    result["o3"],
                    2
                ),

                "so2": round(
                    result["so2"],
                    2
                ),

                "nh3": round(
                    result["nh3"],
                    2
                )
            },

            "weather": {

                "temperature": round(
                    result["temperature"],
                    2
                ),

                "humidity": round(
                    result["humidity"],
                    2
                ),

                "pressure": round(
                    result["pressure"],
                    2
                ),

                "wind_speed": round(
                    result["wind_speed"],
                    2
                )
            }
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )



@app.get("/forecast/{city}")
def forecast(city: str):

    city = city.title()

    if city not in SUPPORTED_CITIES:

        raise HTTPException(
            status_code=400,
            detail=(
                "City must be Lahore, Islamabad, or Karachi"
            )
        )

    try:

        forecast_data = predict_next_3_days(
            city
        )

        return {

            "city": city,

            "forecast": forecast_data
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )

