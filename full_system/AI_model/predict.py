import joblib
import pandas as pd
from pathlib import Path

# =========================
# LOAD MODELS
# =========================

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "AI_model" / "models"

production_model = joblib.load(
    MODEL_DIR / "production_model.pkl"
)

consumption_model = joblib.load(
    MODEL_DIR / "consumption_model.pkl"
)

# =========================
# HOUSE MAPPING
# =========================

house_mapping = {
    "A": 0,
    "B": 1,
    "C": 2
}


# =========================
# PREDICTION FUNCTION
# =========================

def predict_energy(
    house_id,
    hour,
    temperature,
    humidity,
    solar_irradiance
):

    house_number = house_mapping[house_id]

    input_data = pd.DataFrame([
        {
            "house_id": house_number,
            "hour": hour,
            "temperature": temperature,
            "humidity": humidity,
            "solar_irradiance": solar_irradiance
        }
    ])

    predicted_production = production_model.predict(
        input_data
    )[0]

    predicted_consumption = consumption_model.predict(
        input_data
    )[0]

    predicted_production = max(
        0,
        predicted_production
    )

    predicted_consumption = max(
        0,
        predicted_consumption
    )

    predicted_surplus = (
        predicted_production
        - predicted_consumption
    )

    if predicted_surplus > 0:
        status = "SELLER"

    elif predicted_surplus < 0:
        status = "BUYER"

    else:
        status = "BALANCED"

    return {
        "house_id": house_id,
        "predicted_production": round(
            predicted_production,
            2
        ),
        "predicted_consumption": round(
            predicted_consumption,
            2
        ),
        "predicted_surplus": round(
            predicted_surplus,
            2
        ),
        "status": status
    }


# =========================
# TEST
# =========================

if __name__ == "__main__":

    result = predict_energy(
        house_id="A",
        hour=12,
        temperature=32,
        humidity=60,
        solar_irradiance=850
    )

    print("\n" + "=" * 60)
    print("AI ENERGY PREDICTION")
    print("=" * 60)

    print(
        f"House       : {result['house_id']}"
    )

    print(
        f"Production  : "
        f"{result['predicted_production']} kWh"
    )

    print(
        f"Consumption : "
        f"{result['predicted_consumption']} kWh"
    )

    print(
        f"Surplus     : "
        f"{result['predicted_surplus']} kWh"
    )

    print(
        f"Status      : "
        f"{result['status']}"
    )
