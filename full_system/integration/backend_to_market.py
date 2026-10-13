import csv

from market.market import create_orders
from market.matching import match_orders

CSV_FILE = "backend/data/energy_data.csv"


def load_energy_data():
    energy_data = []

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            data = {
                "house_id": row["house_id"],
                "production_kwh": float(row["production_kwh"]),
                "consumption_kwh": float(row["consumption_kwh"]),
                "surplus_kwh": float(row["surplus_kwh"])
            }

            energy_data.append(data)

    return energy_data


def create_market_orders(energy_data):
    sell_orders, buy_orders = create_orders(energy_data)

    return sell_orders, buy_orders


def create_transactions(sell_orders, buy_orders):
    transactions = match_orders(
        sell_orders,
        buy_orders
    )

    return transactions


def display_energy_data(energy_data):
    print("\n" + "=" * 60)
    print("BACKEND ENERGY DATA")
    print("=" * 60)

    for data in energy_data:
        print(
            f"House {data['house_id']} | "
            f"Production: {data['production_kwh']} kWh | "
            f"Consumption: {data['consumption_kwh']} kWh | "
            f"Surplus: {data['surplus_kwh']} kWh"
        )


def display_orders(sell_orders, buy_orders):
    print("\n" + "=" * 60)
    print("P2P MARKET ORDERS")
    print("=" * 60)

    print("\nSELL ORDERS")
    print("-" * 60)

    for order in sell_orders:
        order.display()

    print("\nBUY ORDERS")
    print("-" * 60)

    for order in buy_orders:
        order.display()


def display_transactions(transactions):
    print("\n" + "=" * 60)
    print("P2P TRANSACTIONS")
    print("=" * 60)

    if not transactions:
        print("No transactions.")
        return

    for index, transaction in enumerate(
        transactions,
        start=1
    ):
        transaction.display(index)
        print("-" * 60)


def main():
    energy_data = load_energy_data()

    display_energy_data(
        energy_data
    )

    sell_orders, buy_orders = create_market_orders(
        energy_data
    )

    display_orders(
        sell_orders,
        buy_orders
    )

    transactions = create_transactions(
        sell_orders,
        buy_orders
    )

    display_transactions(
        transactions
    )


if __name__ == "__main__":
    main()