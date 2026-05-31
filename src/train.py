from pathlib import Path
import json
import os

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


DATA_PATH = Path(os.getenv("DATA_PATH", "data/transactions.csv"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/model.joblib"))
METRICS_PATH = Path(os.getenv("METRICS_PATH", "models/metrics.json"))
MODEL_VERSION = os.getenv("MODEL_VERSION", "1.0.0")


def parse_money(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace(" ", "", regex=False)
        .astype(float)
    )


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, sep=None, engine="python")
    df.columns = [col.strip() for col in df.columns]

    df["list_price"] = parse_money(df["list_price"])
    df["standard_cost"] = parse_money(df["standard_cost"])

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        format="%d.%m.%Y",
        errors="coerce",
    )

    df["transaction_month"] = df["transaction_date"].dt.month
    df["transaction_dayofweek"] = df["transaction_date"].dt.dayofweek

    df["online_order"] = df["online_order"].astype(str)
    df["product_id"] = df["product_id"].astype(str)

    return df


def build_pipeline() -> Pipeline:
    categorical_features = [
        "product_id",
        "online_order",
        "order_status",
        "brand",
        "product_line",
        "product_class",
        "product_size",
    ]

    numeric_features = [
        "list_price",
        "transaction_month",
        "transaction_dayofweek",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        min_samples_leaf=1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def main() -> None:
    df = load_data()

    target = "standard_cost"

    features = [
        "product_id",
        "online_order",
        "order_status",
        "brand",
        "product_line",
        "product_class",
        "product_size",
        "list_price",
        "transaction_month",
        "transaction_dayofweek",
    ]

    df = df.dropna(subset=features + [target])

    if len(df) < 5:
        raise ValueError("Dataset is too small. Add more rows before training.")

    X = df[features]
    y = df[target]

    test_size = 0.25 if len(df) < 50 else 0.2

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=42,
    )

    pipeline = build_pipeline()

    mlflow.set_experiment("standard-cost-regression")

    with mlflow.start_run(run_name=f"standard-cost-model-{MODEL_VERSION}"):
        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_test)

        mae = mean_absolute_error(y_test, predictions)
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        r2 = r2_score(y_test, predictions)

        metrics = {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
            "model_version": MODEL_VERSION,
            "rows_total": int(len(df)),
            "rows_train": int(len(X_train)),
            "rows_test": int(len(X_test)),
        }

        mlflow.log_param("model_type", "RandomForestRegressor")
        mlflow.log_param("n_estimators", 200)
        mlflow.log_param("target", target)

        mlflow.log_metric("mae", mae)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        mlflow.sklearn.log_model(pipeline, "model")

        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(
            {
                "model": pipeline,
                "features": features,
                "metrics": metrics,
            },
            MODEL_PATH,
        )

        with METRICS_PATH.open("w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=2, ensure_ascii=False)

    print("Training finished")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
