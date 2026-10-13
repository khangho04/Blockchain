from .order import EnergyOrder
from .matching import match_orders
import math


DEFAULT_PRICE = 2.0


# validate data

def validate_energy_data(data):
    required_fields = [
        "house_id",
        "production_kwh",
        "consumption_kwh",
        "surplus_kwh"
    ]

    for field in required_fields:
        if field not in data:
            return False

    try:
        production = float(data["production_kwh"])
        consumption = float(data["consumption_kwh"])
        surplus = float(data["surplus_kwh"])
    except (TypeError, ValueError):
        return False

    if not all(math.isfinite(value) for value in [
        production, consumption, surplus
    ]):
        return False

    
    # Kiểm tra surplus có khớp với production - consumption không.
    expected_surplus = production - consumption

    if not math.isclose(
        surplus,
        expected_surplus,
        rel_tol=0.0,
        abs_tol=0.02
    ):
        return False

    if production < 0 or consumption < 0:
        return False

    return True


# create sell order

def create_sell_order(data):

    return EnergyOrder(
        house_id=data["house_id"],
        order_type="SELL",
        energy_kwh=data["surplus_kwh"],
        price_per_kwh=DEFAULT_PRICE
    )


# create buy order

def create_buy_order(data):

    return EnergyOrder(
        house_id=data["house_id"],
        order_type="BUY",
        energy_kwh=abs(data["surplus_kwh"]),
        price_per_kwh=DEFAULT_PRICE
    )


# create orders

def create_orders(energy_data):

    sell_orders = []
    buy_orders = []

    for data in energy_data:

        if not validate_energy_data(data):
            continue

        surplus = float(
            data["surplus_kwh"]
        )

        if surplus > 0:

            order = create_sell_order(
                data
            )

            sell_orders.append(order)

        elif surplus < 0:

            order = create_buy_order(
                data
            )

            buy_orders.append(order)

    return sell_orders, buy_orders


# display orders

def display_orders(
    sell_orders,
    buy_orders
):

    print("\n" + "=" * 60)
    print("P2P ENERGY MARKET")
    print("=" * 60)

    print("\nSELL ORDERS")
    print("-" * 60)

    if not sell_orders:
        print("No sell orders.")

    for order in sell_orders:
        order.display()

    print("\nBUY ORDERS")
    print("-" * 60)

    if not buy_orders:
        print("No buy orders.")

    for order in buy_orders:
        order.display()


# display transactions

def display_transactions(
    transactions
):

    print("\n" + "=" * 60)
    print("MATCHING RESULTS")
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


# display remaining orders

def display_remaining_orders(
    sell_orders,
    buy_orders
):

    print("\n" + "=" * 60)
    print("REMAINING ENERGY")
    print("=" * 60)

    print("\nSELLERS")
    print("-" * 60)

    for order in sell_orders:

        print(
            f"{order.house_id} : "
            f"{order.energy_kwh:.2f} kWh"
        )

    print("\nBUYERS")
    print("-" * 60)

    for order in buy_orders:

        print(
            f"{order.house_id} : "
            f"{order.energy_kwh:.2f} kWh"
        )


# calculate summary

def calculate_summary(transactions):

    total_energy = 0
    total_value = 0

    for transaction in transactions:

        total_energy += (
            transaction.energy_kwh
        )

        total_value += (
            transaction.total_price()
        )

    return {
        "transaction_count": len(
            transactions
        ),
        "total_energy": round(
            total_energy,
            2
        ),
        "total_value": round(
            total_value,
            2
        )
    }


# display summary

def display_summary(transactions):

    summary = calculate_summary(
        transactions
    )

    print("\n" + "=" * 60)
    print("MARKET SUMMARY")
    print("=" * 60)

    print(
        f"Transactions : "
        f"{summary['transaction_count']}"
    )

    print(
        f"Energy traded: "
        f"{summary['total_energy']:.2f} kWh"
    )

    print(
        f"Total value  : "
        f"{summary['total_value']:.2f} Token"
    )


# blockchain data

def prepare_blockchain_data(
    transactions
):

    blockchain_data = []

    for transaction in transactions:

        data = transaction.to_dict()

        blockchain_data.append(data)

    return blockchain_data


# display blockchain data

def display_blockchain_data(
    transactions
):

    data = prepare_blockchain_data(
        transactions
    )

    print("\n" + "=" * 60)
    print("BLOCKCHAIN DATA")
    print("=" * 60)

    for index, transaction in enumerate(
        data,
        start=1
    ):

        print(
            f"\nTransaction {index}"
        )

        for key, value in transaction.items():

            print(
                f"{key}: {value}"
            )


# main

def main():

    energy_data = [

        {
            "house_id": "A",
            "production_kwh": 5.1,
            "consumption_kwh": 2.0,
            "surplus_kwh": 3.1
        },

        {
            "house_id": "B",
            "production_kwh": 1.2,
            "consumption_kwh": 3.0,
            "surplus_kwh": -1.8
        },

        {
            "house_id": "C",
            "production_kwh": 3.5,
            "consumption_kwh": 2.0,
            "surplus_kwh": 1.5
        }
    ]

    sell_orders, buy_orders = create_orders(
        energy_data
    )

    display_orders(
        sell_orders,
        buy_orders
    )

    transactions = match_orders(
        sell_orders,
        buy_orders
    )

    display_transactions(
        transactions
    )

    display_remaining_orders(
        sell_orders,
        buy_orders
    )

    display_summary(
        transactions
    )

    display_blockchain_data(
        transactions
    )


if __name__ == "__main__":
    main()
