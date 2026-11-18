import argparse
import pandas as pd
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
import xgboost as xgb
import yaml
import logging
from mlflow.tracking import MlflowClient
import platform
import sklearn

# -----------------------------
# Configure logging
# -----------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -----------------------------
# Argument parser
# -----------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Train and register final model from config.")
    parser.add_argument("--config", type=str, required=True, help="Path to model_config.yaml")
    parser.add_argument("--data", type=str, required=True, help="Path to processed CSV dataset")
    parser.add_argument("--models-dir", type=str, required=True, help="Directory to save trained model")
    parser.add_argument("--mlflow-tracking-uri", type=str, default=None, help="MLflow tracking URI")
    return parser.parse_args()

# -----------------------------
# Load model from config
# -----------------------------
def get_model_instance(name, params):
    model_map = {
        'LinearRegression': LinearRegression,
        'RandomForest': RandomForestRegressor,
        'GradientBoosting': GradientBoostingRegressor,
        'XGBoost': xgb.XGBRegressor
    }
    if name not in model_map:
        raise ValueError(f"Unsupported model: {name}")
    return model_map[name](**params)

# -----------------------------
# Main logic
# -----------------------------
def main(args):
    # Load config
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    model_cfg = config['model']

    if args.mlflow_tracking_uri:
        mlflow.set_tracking_uri(args.mlflow_tracking_uri)
        mlflow.set_experiment(model_cfg['name'])

    # Load data
    data = pd.read_csv(args.data)
    target = model_cfg['target_variable']

    # Use all features except the target variable
    X = data.drop(columns=[target])
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Get model
    model = get_model_instance(model_cfg['best_model'], model_cfg['parameters'])

    # Start MLflow run
    with mlflow.start_run(run_name="final_training"):
        logger.info(f"Training model: {model_cfg['best_model']}")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))

        # Log params and metrics
        mlflow.log_params(model_cfg['parameters'])
        mlflow.log_metrics({'mae': mae, 'r2': r2})

        # Log and register model
        mlflow.sklearn.log_model(model, "tuned_model")
        model_name = model_cfg['name']
        model_uri = f"runs:/{mlflow.active_run().info.run_id}/tuned_model"

        logger.info("Registering model to MLflow Model Registry...")
        client = MlflowClient()
        try:
            client.create_registered_model(model_name)
        except mlflow.exceptions.RestException:
            pass  # already exists

        model_version = client.create_model_version(
            name=model_name,
            source=model_uri,
            run_id=mlflow.active_run().info.run_id
        )

        # Transition model to "Staging"
        client.transition_model_version_stage(
            name=model_name,
            version=model_version.version,
            stage="Staging"
        )

        # Add a human-readable description
        description = (
            f"Model for predicting house prices.\n"
            f"Algorithm: {model_cfg['best_model']}\n"
            f"Hyperparameters: {model_cfg['parameters']}\n"
            f"Features used: All features in the dataset except the target variable\n"
            f"Target variable: {target}\n"
            f"Trained on dataset: {args.data}\n"
            f"Model saved at: {args.models_dir}/trained/{model_name}.pkl\n"
            f"Performance metrics:\n"
            f"  - MAE: {mae:.2f}\n"
            f"  - R²: {r2:.4f}"
        )
        client.update_registered_model(name=model_name, description=description)

        # Add tags for better organization
        client.set_registered_model_tag(model_name, "algorithm", model_cfg['best_model'])
        client.set_registered_model_tag(model_name, "hyperparameters", str(model_cfg['parameters']))
        client.set_registered_model_tag(model_name, "features", "All features except target variable")
        client.set_registered_model_tag(model_name, "target_variable", target)
        client.set_registered_model_tag(model_name, "training_dataset", args.data)
        client.set_registered_model_tag(model_name, "model_path", f"{args.models_dir}/trained/{model_name}.pkl")

        # Add dependency tags
        deps = {
            "python_version": platform.python_version(),
            "scikit_learn_version": sklearn.__version__,
            "xgboost_version": xgb.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
        }
        for k, v in deps.items():
            client.set_registered_model_tag(model_name, k, v)

        # Save model locally
        save_path = f"{args.models_dir}/trained/{model_name}.pkl"
        joblib.dump(model, save_path)
        logger.info(f"Saved trained model to: {save_path}")
        logger.info(f"Final MAE: {mae:.2f}, R²: {r2:.4f}")

if __name__ == "__main__":
    args = parse_args()
    main(args)
