import json
import glob
import pandas as pd


# Raw JSON files ka path
files = glob.glob("data/raw/*.json")

records = []

# Har JSON file read karo
for file in files:

    with open(file, "r") as f:
        data = json.load(f)

    records.append(data)


# JSON records ko DataFrame mein convert karo
df = pd.DataFrame(records)


# Timestamp ko datetime mein convert karo
df["timestamp"] = pd.to_datetime(df["timestamp"])


# Timestamp ke according sort karo
df = df.sort_values("timestamp")


# Processed folder create karo
import os
os.makedirs("data/processed", exist_ok=True)


# CSV save karo
output_file = "data/processed/weather_air_quality.csv"

df.to_csv(output_file, index=False)


print("\n================================")
print("DATA PROCESSING COMPLETED")
print("================================")

print("\nNumber of records:", len(df))

print("\nColumns:")
print(df.columns.tolist())

print("\nDataset:")
print(df)

print("\nSaved to:", output_file)