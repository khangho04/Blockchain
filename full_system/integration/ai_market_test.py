from integration.ai_processor import predict_all_houses

from market.market import (
    create_orders,
    display_orders,
    display_transactions,
    display_remaining_orders,
    display_summary,
    display_blockchain_data,
)

from market.matching import match_orders


def main():
    print("\n" + "=" * 70)
    print("AI -> P2P ENERGY MARKET TEST")
    print("=" * 70)

    # 1. Get predictions from backend CSV
    predictions = predict_all_houses(hour=12)

    if not predictions:
        print("No predictions available.")
        return

    # 2. Convert AI predictions into market input
    energy_data = []

    for result in predictions:
        production = float(result["predicted_production"])
        consumption = float(result["predicted_consumption"])
        surplus = round(production - consumption, 2)

        energy_data.append({
            "house_id": result["house_id"],
            "production_kwh": production,
            "consumption_kwh": consumption,
            "surplus_kwh": surplus,
        })

    # 3. Create market orders
    sell_orders, buy_orders = create_orders(energy_data)

    display_orders(sell_orders, buy_orders)

    # 4. Match orders (simulation only)
    transactions = match_orders(sell_orders, buy_orders)

    display_transactions(transactions)

    # 5. Display remaining orders and summary
    display_remaining_orders(sell_orders, buy_orders)
    display_summary(transactions)

    # 6. Show data format prepared for blockchain
    # This only prints data; it does NOT submit transactions.
    display_blockchain_data(transactions)

    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE - NO BLOCKCHAIN TRANSACTION SENT")
    print("=" * 70)


if __name__ == "__main__":
    main()

