import pandas as pd
import os
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from pathlib import Path


# =========================
# LOAD DATA
# =========================


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "AI_model" / "ai_dataset.csv"

df = pd.read_csv(DATA_FILE)


# =========================
# ENCODE HOUSE ID
# =========================

house_mapping = {
    "A": 0,
    "B": 1,
    "C": 2
}

df["house_id"] = df["house_id"].map(house_mapping)


# =========================
# FEATURES
# =========================

features = [
    "house_id",
    "hour",
    "temperature",
    "humidity",
    "solar_irradiance"
]

X = df[features]

y = df["production_kwh"]


# =========================
# TRAIN / TEST SPLIT BY TIME
# =========================

# Giữ timestamp để chia dữ liệu theo thời gian.
# Không đưa timestamp trực tiếp vào features.
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sắp xếp theo thời gian
df = df.sort_values("timestamp").reset_index(drop=True)

# Chia 80% dữ liệu thời gian đầu để train,
# 20% dữ liệu thời gian cuối để test.
split_index = int(len(df) * 0.8)

train_df = df.iloc[:split_index].copy()
test_df = df.iloc[split_index:].copy()

X_train = train_df[features]
y_train = train_df["production_kwh"]

X_test = test_df[features]
y_test = test_df["production_kwh"]

print(f"Training samples: {len(X_train)}")
print(f"Testing samples : {len(X_test)}")
print(f"Train period    : {train_df['timestamp'].min()} "
      f"to {train_df['timestamp'].max()}")
print(f"Test period     : {test_df['timestamp'].min()} "
      f"to {test_df['timestamp'].max()}")




# =========================
# MODEL
# =========================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# =========================
# TRAIN
# =========================

print("Training Production model...")

model.fit(
    X_train,
    y_train
)


# =========================
# PREDICTION
# =========================

y_pred = model.predict(X_test)


# =========================
# EVALUATION
# =========================

mae = mean_absolute_error(
    y_test,
    y_pred
)

mse = mean_squared_error(
    y_test,
    y_pred
)

rmse = mse ** 0.5

r2 = r2_score(
    y_test,
    y_pred
)


print("\n" + "=" * 60)
print("PRODUCTION MODEL RESULTS")
print("=" * 60)

print(f"MAE  : {mae:.4f} kWh")
print(f"RMSE : {rmse:.4f} kWh")
print(f"R2   : {r2:.4f}")


# =========================
# SAVE MODEL
# =========================

os.makedirs(
    PROJECT_ROOT / "AI_model" / "models",
    exist_ok=True
)

model_path = PROJECT_ROOT / "AI_model" / "models" / "production_model.pkl"

joblib.dump(
    model,
    model_path
)

print("\nModel saved to:")
print(model_path)
