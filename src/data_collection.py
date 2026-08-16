import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv



load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("OPENWEATHER_API_KEY not found in .env file")



CITIES = [
    "Lahore",
    "Islamabad",
    "Karachi"
]



WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

AIR_POLLUTION_URL = (
    "https://api.openweathermap.org/data/2.5/air_pollution"
)


RAW_DATA_DIR = "data/raw"

os.makedirs(RAW_DATA_DIR, exist_ok=True)



for city in CITIES:

    print("CITY:", city)



    weather_params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    weather_response = requests.get(
        WEATHER_URL,
        params=weather_params,
        timeout=10
    )

    if weather_response.status_code != 200:

        print(
            "Weather Error:",
            weather_response.status_code,
            weather_response.text
        )

        continue


    # Convert JSON response into Python dictionary
    weather_data = weather_response.json()


    latitude = weather_data["coord"]["lat"]
    longitude = weather_data["coord"]["lon"]



    temperature = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]
    pressure = weather_data["main"]["pressure"]
    wind_speed = weather_data["wind"]["speed"]


    print("Latitude:", latitude)
    print("Longitude:", longitude)

    print("Temperature:", temperature, "°C")
    print("Humidity:", humidity, "%")
    print("Pressure:", pressure, "hPa")
    print("Wind Speed:", wind_speed, "m/s")




    pollution_params = {
        "lat": latitude,
        "lon": longitude,
        "appid": API_KEY
    }

    pollution_response = requests.get(
        AIR_POLLUTION_URL,
        params=pollution_params,
        timeout=10
    )


    if pollution_response.status_code != 200:

        print(
            "Pollution Error:",
            pollution_response.status_code,
            pollution_response.text
        )

        continue


    # Convert JSON response
    pollution_data = pollution_response.json()


    # Get latest pollution information
    pollution = pollution_data["list"][0]




    aqi = pollution["main"]["aqi"]



    components = pollution["components"]

    co = components["co"]
    no = components["no"]
    no2 = components["no2"]
    o3 = components["o3"]
    so2 = components["so2"]
    pm2_5 = components["pm2_5"]
    pm10 = components["pm10"]
    nh3 = components["nh3"]


    print("\n--- AIR QUALITY ---")

    print("AQI:", aqi)
    print("CO:", co)
    print("NO:", no)
    print("NO2:", no2)
    print("O3:", o3)
    print("SO2:", so2)
    print("PM2.5:", pm2_5)
    print("PM10:", pm10)
    print("NH3:", nh3)



    # 7. COMBINE WEATHER + AIR QUALITY DATA

    record = {

        # City
        "city": city,

        # Time
        "timestamp": datetime.now().isoformat(),

        # Location
        "latitude": latitude,
        "longitude": longitude,

        # Weather
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure,
        "wind_speed": wind_speed,


        "aqi": aqi,


        "co": co,
        "no": no,
        "no2": no2,
        "o3": o3,
        "so2": so2,
        "pm2_5": pm2_5,
        "pm10": pm10,
        "nh3": nh3
    }


    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{RAW_DATA_DIR}/{city}_{timestamp}.json"
    )


    with open(filename, "w") as file:

        json.dump(
            record,
            file,
            indent=4
        )


    print("\nSaved:", filename)


print("DATA COLLECTION COMPLETED")
