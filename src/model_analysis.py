
import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    confusion_matrix,
    classification_report
)

MODEL_FILE = "models/best_aqi_model.joblib"
TEST_FILE = "data/processed/test_6months.csv"

OUTPUT_DIR = "data/processed/model_analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)

model = joblib.load(MODEL_FILE)
test_df = pd.read_csv(TEST_FILE)

TARGET = "target_aqi"

X_test = test_df.drop(
    columns=[TARGET, "timestamp"]
)

y_test = test_df[TARGET]

predictions = model.predict(X_test)

results = test_df[
    ["city", "timestamp", TARGET]
].copy()

results["predicted_aqi"] = predictions

results["error"] = (
    results["predicted_aqi"] -
    results[TARGET]
)

results["absolute_error"] = (
    results["error"].abs()
)

results["predicted_category"] = np.clip(
    np.rint(results["predicted_aqi"]),
    1,
    5
).astype(int)

results["actual_category"] = (
    results[TARGET]
    .round()
    .astype(int)
)

results.to_csv(
    f"{OUTPUT_DIR}/predictions.csv",
    index=False
)

print("=" * 45)
print("MODEL ANALYSIS")
print("=" * 45)

print(f"Test records: {len(results)}")

print("\nOverall Metrics:")
print(
    f"MAE: {mean_absolute_error(y_test, predictions):.4f}"
)

print(
    f"RMSE: {np.sqrt(mean_squared_error(y_test, predictions)):.4f}"
)

print(
    f"R2: {r2_score(y_test, predictions):.4f}"
)


print("\nError Statistics:")
print(
    results["absolute_error"].describe()
)


print("\nCategory Classification Report:")

print(
    classification_report(
        results["actual_category"],
        results["predicted_category"],
        labels=[1, 2, 3, 4, 5],
        zero_division=0
    )
)


print("\nConfusion Matrix:")

cm = confusion_matrix(
    results["actual_category"],
    results["predicted_category"],
    labels=[1, 2, 3, 4, 5]
)

print(cm)


# Actual vs Predicted

plt.figure(figsize=(8, 6))

plt.scatter(
    y_test,
    predictions,
    alpha=0.4
)

plt.xlabel("Actual AQI")
plt.ylabel("Predicted AQI")
plt.title("Actual vs Predicted AQI")

minimum = min(
    y_test.min(),
    predictions.min()
)

maximum = max(
    y_test.max(),
    predictions.max()
)

plt.plot(
    [minimum, maximum],
    [minimum, maximum]
)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/actual_vs_predicted.png",
    dpi=300
)

plt.close()


# Error distribution

plt.figure(figsize=(8, 6))

plt.hist(
    results["error"],
    bins=30
)

plt.xlabel("Prediction Error")
plt.ylabel("Frequency")
plt.title("AQI Prediction Error Distribution")

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/error_distribution.png",
    dpi=300
)

plt.close()


# Feature importance

preprocessor = model.named_steps["preprocessor"]
rf_model = model.named_steps["model"]

feature_names = (
    preprocessor
    .get_feature_names_out()
)

importance = pd.DataFrame({
    "feature": feature_names,
    "importance": rf_model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

importance.to_csv(
    f"{OUTPUT_DIR}/feature_importance.csv",
    index=False
)

print("\nTop 15 Important Features:")

print(
    importance.head(15).to_string(
        index=False
    )
)

print("\nAnalysis files saved to:")
print(OUTPUT_DIR)

