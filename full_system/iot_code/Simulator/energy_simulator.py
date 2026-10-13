import random
import csv


HOUSES = ["A", "B", "C"]

SOLAR_BASE = [
    0, 0, 0, 0, 0, 0,
    0.2, 0.8, 1.5, 2.5, 3.5, 4.5,
    5.0, 5.2, 4.8, 4.0, 2.8, 1.2,
    0, 0, 0, 0, 0, 0
]

CONSUMPTION_BASE = [
    1.0, 0.8, 0.8, 0.8, 0.8, 1.0,
    1.5, 2.0, 2.2, 1.8, 1.8, 2.0,
    2.5, 2.2, 2.0, 2.0, 2.2, 3.0,
    4.0, 4.5, 4.5, 4.0, 3.0, 2.0
]

SOLAR_IRRADIANCE_BASE = [
    0, 0, 0, 0, 0, 0,
    100, 250, 400, 550, 700, 850,
    950, 1000, 900, 750, 550, 300,
    0, 0, 0, 0, 0, 0
]


def simulate_environment(hour):
    temperature = 24 + (
        8 * max(
            0,
            1 - abs(hour - 13) / 13
        )
    )

    temperature += random.uniform(
        -1.5,
        1.5
    )

    humidity = 80 - (
        25 * max(
            0,
            1 - abs(hour - 13) / 13
        )
    )

    humidity += random.uniform(
        -5,
        5
    )

    solar_irradiance = (
        SOLAR_IRRADIANCE_BASE[hour]
        + random.uniform(-30, 30)
    )

    solar_irradiance = max(
        0,
        solar_irradiance
    )

    return {
        "temperature": round(
            temperature,
            2
        ),
        "humidity": round(
            humidity,
            2
        ),
        "solar_irradiance": round(
            solar_irradiance,
            2
        )
    }


def simulate_house(
    house,
    solar_base,
    consumption_base
):
    house_data = []

    for hour in range(24):

        production = solar_base[hour]
        consumption = consumption_base[hour]

        if house == "A":
            production *= 1.2
            consumption *= 0.9

        elif house == "B":
            production *= 0.5
            consumption *= 1.2

        elif house == "C":
            production *= 0.9
            consumption *= 1.0

        production += random.uniform(
            -0.1,
            0.1
        )

        consumption += random.uniform(
            -0.1,
            0.1
        )

        production = max(
            0,
            production
        )

        consumption = max(
            0,
            consumption
        )

        surplus = (
            production
            - consumption
        )

        if surplus > 0:
            status = "SELLER"

        elif surplus < 0:
            status = "BUYER"

        else:
            status = "BALANCED"

        environment = simulate_environment(
            hour
        )

        house_data.append({
            "hour": hour,
            "house_id": house,
            "temperature": environment[
                "temperature"
            ],
            "humidity": environment[
                "humidity"
            ],
            "solar_irradiance": environment[
                "solar_irradiance"
            ],
            "production_kwh": round(
                production,
                2
            ),
            "consumption_kwh": round(
                consumption,
                2
            ),
            "surplus_kwh": round(
                surplus,
                2
            ),
            "status": status
        })

    return house_data


def simulate_all_houses():

    data = []

    for house in HOUSES:

        house_data = simulate_house(
            house,
            SOLAR_BASE,
            CONSUMPTION_BASE
        )

        data.extend(
            house_data
        )

    return data


def display_table(data):

    print("\nP2P ENERGY TRADING SIMULATOR")
    print("=" * 130)

    print(
        f"{'Hour':<6}"
        f"{'House':<8}"
        f"{'Temp':<10}"
        f"{'Humidity':<12}"
        f"{'Irradiance':<14}"
        f"{'Production':<15}"
        f"{'Consumption':<15}"
        f"{'Surplus':<12}"
        f"{'Status':<12}"
    )

    print("-" * 130)

    for row in data:

        print(
            f"{row['hour']:<6}"
            f"{row['house_id']:<8}"
            f"{row['temperature']:<10.2f}"
            f"{row['humidity']:<12.2f}"
            f"{row['solar_irradiance']:<14.2f}"
            f"{row['production_kwh']:<15.2f}"
            f"{row['consumption_kwh']:<15.2f}"
            f"{row['surplus_kwh']:<12.2f}"
            f"{row['status']:<12}"
        )

    print("=" * 130)


def display_summary(data):

    print("\nSUMMARY")
    print("=" * 70)

    print(
        f"{'House':<10}"
        f"{'Production':<15}"
        f"{'Consumption':<15}"
        f"{'Surplus':<15}"
        f"{'Role':<10}"
    )

    print("-" * 70)

    for house in HOUSES:

        house_data = [
            row
            for row in data
            if row["house_id"] == house
        ]

        total_production = sum(
            row["production_kwh"]
            for row in house_data
        )

        total_consumption = sum(
            row["consumption_kwh"]
            for row in house_data
        )

        total_surplus = (
            total_production
            - total_consumption
        )

        if total_surplus > 0:
            role = "SELLER"

        elif total_surplus < 0:
            role = "BUYER"

        else:
            role = "BALANCED"

        print(
            f"{house:<10}"
            f"{total_production:<15.2f}"
            f"{total_consumption:<15.2f}"
            f"{total_surplus:<15.2f}"
            f"{role:<10}"
        )

    print("=" * 70)


def save_to_csv(
    data,
    filename="dataset.csv"
):
    with open(
        filename,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
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

        for row in data:

            writer.writerow([
                row["hour"],
                row["house_id"],
                row["temperature"],
                row["humidity"],
                row["solar_irradiance"],
                row["production_kwh"],
                row["consumption_kwh"],
                row["surplus_kwh"],
                row["status"]
            ])

    print(
        f"\nDataset saved: {filename}"
    )


def main():

    data = simulate_all_houses()

    display_table(data)

    display_summary(data)

    save_to_csv(data)

    print("\nSimulation completed!")


if __name__ == "__main__":
    main()