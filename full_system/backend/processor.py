import csv
import os
from datetime import datetime


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FOLDER = os.path.join(
    BASE_DIR,
    "data"
)

CSV_FILE = os.path.join(
    DATA_FOLDER,
    "energy_data.csv"
)


def create_data_folder():

    if not os.path.exists(DATA_FOLDER):

        os.makedirs(DATA_FOLDER)


def validate_data(data):

    required_fields = [
        "hour",
        "house_id",
        "temperature",
        "humidity",
        "solar_irradiance",
        "production_kwh",
        "consumption_kwh"
    ]

    for field in required_fields:

        if field not in data:

            print(
                f"ERROR: Missing field: {field}"
            )

            return False

    if data["house_id"] not in [
        "A",
        "B",
        "C"
    ]:

        print(
            f"ERROR: Invalid house ID: "
            f"{data['house_id']}"
        )

        return False

    hour = int(data["hour"])

    if hour < 0 or hour > 23:

        print(
            "ERROR: Invalid hour"
        )

        return False

    if float(data["production_kwh"]) < 0:

        print(
            "ERROR: Production cannot be negative"
        )

        return False

    if float(data["consumption_kwh"]) < 0:

        print(
            "ERROR: Consumption cannot be negative"
        )

        return False

    if float(data["humidity"]) < 0 or \
       float(data["humidity"]) > 100:

        print(
            "ERROR: Invalid humidity"
        )

        return False

    if float(data["solar_irradiance"]) < 0:

        print(
            "ERROR: Solar irradiance cannot be negative"
        )

        return False

    return True


def calculate_surplus(
    production,
    consumption
):

    return production - consumption


def determine_status(surplus):

    if surplus > 0:

        return "SELLER"

    elif surplus < 0:

        return "BUYER"

    else:

        return "BALANCED"


def save_to_csv(data):

    create_data_folder()

    file_exists = os.path.exists(
        CSV_FILE
    )

    with open(
        CSV_FILE,
        "a",
        newline=""
    ) as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "timestamp",
                "hour",
                "house_id",
                "temperature",
                "humidity",
                "solar_irradiance",
                "production_kwh",
                "consumption_kwh",
                "surplus_kwh",
                "status"
            ])

        writer.writerow([
            data["timestamp"],
            data["hour"],
            data["house_id"],
            data["temperature"],
            data["humidity"],
            data["solar_irradiance"],
            data["production_kwh"],
            data["consumption_kwh"],
            data["surplus_kwh"],
            data["status"]
        ])


def process_energy_data(data):

    if not validate_data(data):

        return

    hour = int(
        data["hour"]
    )

    temperature = float(
        data["temperature"]
    )

    humidity = float(
        data["humidity"]
    )

    solar_irradiance = float(
        data["solar_irradiance"]
    )

    production = float(
        data["production_kwh"]
    )

    consumption = float(
        data["consumption_kwh"]
    )

    surplus = calculate_surplus(
        production,
        consumption
    )

    status = determine_status(
        surplus
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    processed_data = {

        "timestamp":
            timestamp,

        "hour":
            hour,

        "house_id":
            data["house_id"],

        "temperature":
            round(
                temperature,
                2
            ),

        "humidity":
            round(
                humidity,
                2
            ),

        "solar_irradiance":
            round(
                solar_irradiance,
                2
            ),

        "production_kwh":
            round(
                production,
                2
            ),

        "consumption_kwh":
            round(
                consumption,
                2
            ),

        "surplus_kwh":
            round(
                surplus,
                2
            ),

        "status":
            status
    }

    print("\n" + "=" * 60)

    print(
        "PROCESSED ENERGY DATA"
    )

    print("-" * 60)

    print(
        f"House       : "
        f"{processed_data['house_id']}"
    )

    print(
        f"Hour        : "
        f"{processed_data['hour']}"
    )

    print(
        f"Temperature : "
        f"{processed_data['temperature']} °C"
    )

    print(
        f"Humidity    : "
        f"{processed_data['humidity']} %"
    )

    print(
        f"Irradiance  : "
        f"{processed_data['solar_irradiance']} W/m²"
    )

    print(
        f"Production  : "
        f"{processed_data['production_kwh']} kWh"
    )

    print(
        f"Consumption : "
        f"{processed_data['consumption_kwh']} kWh"
    )

    print(
        f"Surplus     : "
        f"{processed_data['surplus_kwh']} kWh"
    )

    print(
        f"Status      : "
        f"{processed_data['status']}"
    )

    print("=" * 60)

    save_to_csv(
        processed_data
    )

    print(
        "Data saved to "
        f"{CSV_FILE}"
    )