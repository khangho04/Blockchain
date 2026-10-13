import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# CONFIGURATION
NUM_DAYS = 90

HOUSES = ["A", "B", "C"]

# RELATIVE OUTPUT PA

# Thư mục chứa file generate_dataset.py
BASE_DIR = Path(__file__).resolve().parent

# File output nằm cùng thư mục với generate_dataset.py
OUTPUT_FILE = BASE_DIR / "ai_dataset.csv"

# HOUSE CONFIGURATION

HOUSE_CONFIG = {
    "A": {
        "solar_factor": 1.2,
        "consumption_factor": 0.9
    },

    "B": {
        "solar_factor": 0.5,
        "consumption_factor": 1.2
    },

    "C": {
        "solar_factor": 0.9,
        "consumption_factor": 1.0
    }
}

# SOLAR MODEL
def calculate_solar_irradiance(hour):

    solar_profile = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 50,
        7: 150,
        8: 300,
        9: 450,
        10: 600,
        11: 750,
        12: 850,
        13: 900,
        14: 850,
        15: 700,
        16: 500,
        17: 250,
        18: 50,
        19: 0,
        20: 0,
        21: 0,
        22: 0,
        23: 0
    }

    return solar_profile[hour]

# TEMPERATURE MODEL

def calculate_temperature(hour):

    temperature_profile = {
        0: 25,
        1: 25,
        2: 24.5,
        3: 24.5,
        4: 24,
        5: 24,
        6: 25,
        7: 26,
        8: 28,
        9: 29,
        10: 30,
        11: 31,
        12: 32,
        13: 33,
        14: 33,
        15: 32,
        16: 31,
        17: 30,
        18: 29,
        19: 28,
        20: 27,
        21: 27,
        22: 26,
        23: 26
    }

    noise = np.random.normal(0, 0.5)

    return temperature_profile[hour] + noise


# HUMIDITY MODEL

def calculate_humidity(hour):

    humidity_profile = {
        0: 80,
        1: 81,
        2: 82,
        3: 83,
        4: 84,
        5: 84,
        6: 82,
        7: 80,
        8: 76,
        9: 72,
        10: 68,
        11: 64,
        12: 60,
        13: 58,
        14: 58,
        15: 60,
        16: 64,
        17: 68,
        18: 72,
        19: 75,
        20: 77,
        21: 78,
        22: 79,
        23: 80
    }

    noise = np.random.normal(0, 2)

    return max(
        0,
        min(100, humidity_profile[hour] + noise)
    )

# CONSUMPTION MODEL

def calculate_consumption(hour, house_factor):

    consumption_profile = {
        0: 1.0,
        1: 0.8,
        2: 0.8,
        3: 0.8,
        4: 0.8,
        5: 1.0,
        6: 1.5,
        7: 2.0,
        8: 2.2,
        9: 1.8,
        10: 1.8,
        11: 2.0,
        12: 2.5,
        13: 2.2,
        14: 2.0,
        15: 2.0,
        16: 2.2,
        17: 3.0,
        18: 4.0,
        19: 4.5,
        20: 4.5,
        21: 4.0,
        22: 3.0,
        23: 2.0
    }

    base = consumption_profile[hour] * house_factor

    noise = np.random.normal(0, 0.15)

    return max(0, base + noise)


# PRODUCTION MODEL

def calculate_production(
    solar_irradiance,
    solar_factor
):

    production = (
        solar_irradiance / 1000
    ) * 6 * solar_factor

    noise = np.random.normal(0, 0.1)

    return max(0, production + noise)

# GENERATE DATASET

def generate_dataset():

    rows = []

    start_date = datetime(2026, 1, 1)

    for day in range(NUM_DAYS):

        current_date = start_date + timedelta(days=day)

        for hour in range(24):

            solar_irradiance = calculate_solar_irradiance(
                hour
            )

            temperature = calculate_temperature(
                hour
            )

            humidity = calculate_humidity(
                hour
            )

            for house in HOUSES:

                solar_factor = HOUSE_CONFIG[house][
                    "solar_factor"
                ]

                consumption_factor = HOUSE_CONFIG[house][
                    "consumption_factor"
                ]

                production = calculate_production(
                    solar_irradiance,
                    solar_factor
                )

                consumption = calculate_consumption(
                    hour,
                    consumption_factor
                )

                timestamp = current_date.replace(
                    hour=hour,
                    minute=0,
                    second=0
                )

                rows.append({
                    "timestamp": timestamp,
                    "house_id": house,
                    "hour": hour,
                    "temperature": round(
                        temperature,
                        2
                    ),
                    "humidity": round(
                        humidity,
                        2
                    ),
                    "solar_irradiance": solar_irradiance,
                    "production_kwh": round(
                        production,
                        2
                    ),
                    "consumption_kwh": round(
                        consumption,
                        2
                    )
                })

    df = pd.DataFrame(rows)

    # Lưu dataset
    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("=" * 60)
    print("AI DATASET GENERATED")
    print("=" * 60)

    print(
        f"Number of samples: {len(df)}"
    )

    print("\nFirst 10 samples:")
    print(
        df.head(10)
    )

    print("\nDataset saved to:")
    print(
        OUTPUT_FILE
    )

if __name__ == "__main__":
    generate_dataset()