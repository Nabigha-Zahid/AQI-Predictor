
import os
import pandas as pd
import hopsworks
from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = "dagasalaka34"
FEATURE_GROUP_NAME = "aqi_features"
FEATURE_GROUP_VERSION = 2

OUTPUT_FILE = "data/processed/training_data_6months.csv"

API_KEY = os.getenv("HOPSWORKS_API_KEY")

if not API_KEY:
    raise ValueError("HOPSWORKS_API_KEY not found")


print("Connecting to Hopsworks...")

project = hopsworks.login(
    project=PROJECT_NAME,
    api_key_value=API_KEY
)

feature_store = project.get_feature_store()

feature_group = feature_store.get_feature_group(
    name=FEATURE_GROUP_NAME,
    version=FEATURE_GROUP_VERSION
)

print("Reading data from Hopsworks...")

df = feature_group.read()

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True
)

df = df.sort_values(
    ["city", "timestamp"]
).reset_index(drop=True)

os.makedirs(
    "data/processed",
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Training data retrieved from Hopsworks.")
print(f"Feature Group: {FEATURE_GROUP_NAME}")
print(f"Version: {FEATURE_GROUP_VERSION}")
print(f"Records: {len(df)}")
print(f"Features: {len(df.columns)}")
print(f"Saved to: {OUTPUT_FILE}")

