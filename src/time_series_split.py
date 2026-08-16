
import os
import pandas as pd

INPUT_FILE = "data/processed/training_data_6months.csv"

TRAIN_FILE = "data/processed/train_6months.csv"
VALIDATION_FILE = "data/processed/validation_6months.csv"
TEST_FILE = "data/processed/test_6months.csv"

df = pd.read_csv(INPUT_FILE)

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    utc=True
)

df = df.sort_values(
    ["timestamp", "city"]
).reset_index(drop=True)

total_records = len(df)

train_end = int(total_records * 0.70)
validation_end = int(total_records * 0.85)

train_df = df.iloc[:train_end].copy()
validation_df = df.iloc[train_end:validation_end].copy()
test_df = df.iloc[validation_end:].copy()

os.makedirs(
    "data/processed",
    exist_ok=True
)

train_df.to_csv(
    TRAIN_FILE,
    index=False
)

validation_df.to_csv(
    VALIDATION_FILE,
    index=False
)

test_df.to_csv(
    TEST_FILE,
    index=False
)

print("Time-series data split completed.")
print(f"Total records: {len(df)}")
print(f"Training records: {len(train_df)}")
print(f"Validation records: {len(validation_df)}")
print(f"Test records: {len(test_df)}")

print("\nTraining period:")
print(
    f"{train_df['timestamp'].min()} "
    f"to {train_df['timestamp'].max()}"
)

print("\nValidation period:")
print(
    f"{validation_df['timestamp'].min()} "
    f"to {validation_df['timestamp'].max()}"
)

print("\nTest period:")
print(
    f"{test_df['timestamp'].min()} "
    f"to {test_df['timestamp'].max()}"
)

