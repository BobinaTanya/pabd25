"""This is full life cycle for ml model with CatBoost"""

from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.pipeline import Pipeline
from collections import defaultdict
from joblib import dump, load
import datetime
import argparse
import pandas as pd
import numpy as np
import re
import os
from parse_cian import parse
import logging
import warnings

warnings.filterwarnings("ignore")

TRAIN_SIZE = 0.2
MODEL_NAME = "best_catboost_model.joblib"

logging.basicConfig(
    filename="model_training.log",
    filemode="a",
    format="%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

def train_model():
    """Train CatBoost model and save"""
    df = pd.read_csv("data/processed/df.csv", index_col=0)
    y = df["price"]
    X = df.drop(columns="price")
    
    # Указываем категориальные признаки
    cat_features = ['rooms_count']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=1 - TRAIN_SIZE, random_state=42
    )

    # Инициализируем CatBoost с оптимальными параметрами
    model = CatBoostRegressor(
        iterations=1000,
        learning_rate=0.05,
        depth=6,
        cat_features=cat_features,
        random_seed=42,
        loss_function='RMSE',
        verbose=100 
    )
    
    # Обучение модели
    model.fit(
        X_train, y_train,
        eval_set=(X_test, y_test),
        early_stopping_rounds=50,
        plot=False
    )
    
    # Сохранение модели
    t = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    model_path = f"models/catboost_model_{t}.joblib"
    dump(model, model_path)
    logging.info(f"Trained CatBoost model saved to {model_path}")
    
    return model_path

def test_model(model_path):
    """Test CatBoost model with metrics"""
    df = pd.read_csv("data/processed/df.csv", index_col=0)
    y = df["price"]
    X = df.drop(columns="price")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=1 - TRAIN_SIZE, random_state=42
    )
    
    model = load(model_path)
    predict = model.predict(X_test)

    metrics = {
        'RMSE': np.sqrt(mean_squared_error(y_test, predict)),
        'MAE': mean_absolute_error(y_test, predict),
        'R2': r2_score(y_test, predict),
        'MAPE': np.mean(np.abs((y_test - predict) / y_test)) * 100
    }
    
    logging.info("Model evaluation metrics:")
    for name, value in metrics.items():
        logging.info(f"{name}: {value:.4f}")
    
    return metrics

if __name__ == "__main__":
    """Parse arguments and run lifecycle steps"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--split",
        type=float,
        help="Split data, test relative size, from 0 to 1",
        default=TRAIN_SIZE,
    )
    parser.add_argument("-m", "--model", help="Model name", default=MODEL_NAME)
    parser.add_argument(
        "-d",
        "--download_new",
        help="True or False",
        default=False,
        action=argparse.BooleanOptionalAction,
    )
    args = parser.parse_args()

    if args.download_new:
        parse_cian()
        preprocess_data()
    
    model_path = train_model()
    test_metrics = test_model(model_path)
    
    # Вывод метрик в консоль
    print("\nModel Test Metrics:")
    for metric, value in test_metrics.items():
        print(f"{metric}: {value:.4f}")