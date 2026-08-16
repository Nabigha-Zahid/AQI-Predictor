
import os
import pandas as pd
import hopsworks
from dotenv import load_dotenv

load_dotenv()

INPUT_FILE = "data/processed/features_6months.csv"

PROJECT_NAME = "dagasalaka34"
FEATURE_GROUP_NAME = "aqi_features"
FEATURE_GROUP_VERSION = 2

API_KEY = os.getenv("HOPSWORKS_API_KEY")

if not API_KEY:
    raise ValueError("HOPSWORKS_API_KEY not found")

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True
)

print("Connecting to Hopsworks...")

project = hopsworks.login(
    project=PROJECT_NAME,
    api_key_value=API_KEY
)

feature_store = project.get_feature_store()

print("Connected to Feature Store.")
print(f"Project: {PROJECT_NAME}")
print(f"Records: {len(df)}")
print(f"Features: {len(df.columns)}")


feature_group = feature_store.get_or_create_feature_group(
    name=FEATURE_GROUP_NAME,
    version=FEATURE_GROUP_VERSION,
    description="Six-month historical AQI forecasting features",
    primary_key=["city", "timestamp"],
    event_time="timestamp",
    online_enabled=False,
    time_travel_format="HUDI"
)



feature_group.insert(
    df,
    write_options={
        "wait_for_job": True
    }
)

print("Feature Store update completed.")
print(f"Feature Group: {FEATURE_GROUP_NAME}")
print(f"Version: {FEATURE_GROUP_VERSION}")
print(f"Records: {len(df)}")

