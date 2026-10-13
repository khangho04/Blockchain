import copy
from integration.ai_processor import predict_all_houses
from market.market import create_orders
from market.matching import match_orders


def convert_ai_results_to_energy_data(results):

    energy_data = []

    for result in results:

        energy_data.append({
            "house_id": result["house_id"],
            "production_kwh": result["predicted_production"],
            "consumption_kwh": result["predicted_consumption"],
            "surplus_kwh": result["predicted_surplus"]
        })

    return energy_data


def create_market_transactions(energy_data):

    sell_orders, buy_orders = create_orders(
        energy_data
    )

    original_sell_orders = copy.deepcopy(
        sell_orders
    )

    original_buy_orders = copy.deepcopy(
        buy_orders
    )

    transactions = match_orders(
        sell_orders,
        buy_orders
    )

    return (
        original_sell_orders,
        original_buy_orders,
        sell_orders,
        buy_orders,
        transactions
    )


def display_results(
    energy_data,
    original_sell_orders,
    original_buy_orders,
    sell_orders,
    buy_orders,
    transactions
):

    print("\n" + "=" * 60)
    print("AI → P2P MARKET")
    print("=" * 60)

    print("\nAI ENERGY DATA")
    print("-" * 60)

    for data in energy_data:

        print(
            f"House {data['house_id']} | "
            f"Production: "
            f"{data['production_kwh']} kWh | "
            f"Consumption: "
            f"{data['consumption_kwh']} kWh | "
            f"Surplus: "
            f"{data['surplus_kwh']} kWh"
        )

    print("\nSELL ORDERS")
    print("-" * 60)

    for order in original_sell_orders:

        order.display()

    print("\nBUY ORDERS")
    print("-" * 60)

    for order in original_buy_orders:

        order.display()

    print("\nP2P TRANSACTIONS")
    print("-" * 60)

    if not transactions:

        print("No transactions.")

        return

    for index, transaction in enumerate(
        transactions,
        start=1
    ):

        transaction.display(
            index
        )


def main():

    results = predict_all_houses(
        hour=12
    )

    energy_data = convert_ai_results_to_energy_data(
        results
    )

    (
        original_sell_orders,
        original_buy_orders,
        sell_orders,
        buy_orders,
        transactions
    ) = create_market_transactions(
        energy_data
    )

    display_results(
        energy_data,
        original_sell_orders,
        original_buy_orders,
        sell_orders,
        buy_orders,
        transactions
    )


if __name__ == "__main__":

    main()