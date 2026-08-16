
import pandas as pd

INPUT_FILE = "data/processed/training_data_6months.csv"

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True
)

print("Training Data Validation")
print("=========================")

print(f"Records: {len(df)}")
print(f"Features: {len(df.columns)}")

print("\nMissing Values:")
print(df.isnull().sum()[df.isnull().sum() > 0])

duplicates = df.duplicated(
    subset=["city", "timestamp"]
).sum()

print("\nDuplicate City-Timestamp Records:")
print(duplicates)

print("\nTimestamp Range:")
print(f"Start: {df['timestamp'].min()}")
print(f"End: {df['timestamp'].max()}")

print("\nRecords by City:")
print(df["city"].value_counts().sort_index())

print("\nTarget Distribution:")
print(
    df["target_aqi"]
    .value_counts()
    .sort_index()
)

print("\nTarget Statistics:")
print(
    df["target_aqi"]
    .describe()
)

