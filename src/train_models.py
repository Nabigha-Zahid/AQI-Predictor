
import os
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from xgboost import XGBRegressor


TRAIN_FILE = "data/processed/train_6months.csv"
VALIDATION_FILE = "data/processed/validation_6months.csv"
TEST_FILE = "data/processed/test_6months.csv"

RESULT_FILE = "data/processed/model_comparison_6months.csv"
MODEL_DIR = "models"

os.makedirs(MODEL_DIR, exist_ok=True)


train_df = pd.read_csv(TRAIN_FILE)
validation_df = pd.read_csv(VALIDATION_FILE)
test_df = pd.read_csv(TEST_FILE)


TARGET = "target_aqi"

DROP_COLUMNS = [
    TARGET,
    "timestamp"
]


X_train = train_df.drop(columns=DROP_COLUMNS)
y_train = train_df[TARGET]

X_validation = validation_df.drop(columns=DROP_COLUMNS)
y_validation = validation_df[TARGET]

X_test = test_df.drop(columns=DROP_COLUMNS)
y_test = test_df[TARGET]


categorical_features = [
    "city"
]

numeric_features = [
    column
    for column in X_train.columns
    if column not in categorical_features
]


preprocessor = ColumnTransformer(
    transformers=[
        (
            "city",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),
        (
            "numeric",
            StandardScaler(),
            numeric_features
        )
    ]
)


models = {

    "Multiple Linear Regression": LinearRegression(),

    "Ridge Regression": Ridge(
        alpha=1.0
    ),

    "Random Forest": RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    ),

    "XGBoost": XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=-1
    )
}


validation_results = []
trained_models = {}


print("=" * 40)
print("MODEL TRAINING")
print("=" * 40)

print(f"Training records: {len(train_df)}")
print(f"Validation records: {len(validation_df)}")
print(f"Test records: {len(test_df)}")
print(f"Features before encoding: {len(X_train.columns)}")


for name, model in models.items():

    print("\n" + "=" * 40)
    print(name)
    print("=" * 40)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    pipeline.fit(
        X_train,
        y_train
    )

    validation_predictions = pipeline.predict(
        X_validation
    )

    mae = mean_absolute_error(
        y_validation,
        validation_predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_validation,
            validation_predictions
        )
    )

    r2 = r2_score(
        y_validation,
        validation_predictions
    )

    print(f"Validation MAE: {mae:.4f}")
    print(f"Validation RMSE: {rmse:.4f}")
    print(f"Validation R2: {r2:.4f}")

    validation_results.append({
        "model": name,
        "validation_mae": mae,
        "validation_rmse": rmse,
        "validation_r2": r2
    })

    trained_models[name] = pipeline


results_df = pd.DataFrame(
    validation_results
)

results_df = results_df.sort_values(
    "validation_mae"
).reset_index(drop=True)


best_model_name = results_df.iloc[0]["model"]

best_model = trained_models[
    best_model_name
]


print("\n")
print("=" * 40)
print("MODEL VALIDATION RESULTS")
print("=" * 40)

print(
    results_df.to_string(
        index=False
    )
)

print("\nBest Model:")
print(best_model_name)


print("\n")
print("=" * 40)
print("FINAL TEST EVALUATION")
print("=" * 40)

test_predictions = best_model.predict(
    X_test
)

test_mae = mean_absolute_error(
    y_test,
    test_predictions
)

test_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        test_predictions
    )
)

test_r2 = r2_score(
    y_test,
    test_predictions
)

print(f"Model: {best_model_name}")
print(f"MAE: {test_mae:.4f}")
print(f"RMSE: {test_rmse:.4f}")
print(f"R2 Score: {test_r2:.4f}")


results_df["test_mae"] = np.nan
results_df["test_rmse"] = np.nan
results_df["test_r2"] = np.nan

best_index = results_df.index[
    results_df["model"] == best_model_name
][0]

results_df.loc[
    best_index,
    "test_mae"
] = test_mae

results_df.loc[
    best_index,
    "test_rmse"
] = test_rmse

results_df.loc[
    best_index,
    "test_r2"
] = test_r2


results_df.to_csv(
    RESULT_FILE,
    index=False
)


model_path = os.path.join(
    MODEL_DIR,
    "best_aqi_model.joblib"
)

joblib.dump(
    best_model,
    model_path
)


print("\n")
print("Model comparison saved to:")
print(RESULT_FILE)

print("\nBest model saved to:")
print(model_path)

