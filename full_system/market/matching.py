from datetime import datetime

from .transaction import EnergyTransaction


def check_orders(sell_orders, buy_orders):
    if not sell_orders:
        return False

    if not buy_orders:
        return False

    return True


def get_next_seller(sell_orders, index):
    while index < len(sell_orders):

        if sell_orders[index].energy_kwh > 0:
            return index

        index += 1

    return index


def get_next_buyer(buy_orders, index):
    while index < len(buy_orders):

        if buy_orders[index].energy_kwh > 0:
            return index

        index += 1

    return index


def can_match(seller, buyer):
    if seller.energy_kwh <= 0:
        return False

    if buyer.energy_kwh <= 0:
        return False

    if buyer.price_per_kwh < seller.price_per_kwh:
        return False

    return True


def calculate_trade_energy(seller, buyer):
    return min(
        seller.energy_kwh,
        buyer.energy_kwh
    )


def calculate_trade_price(seller):
    return seller.price_per_kwh


def create_transaction(
    seller,
    buyer,
    trade_energy,
    trade_price
):
    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    return EnergyTransaction(
        seller=seller.house_id,
        buyer=buyer.house_id,
        energy_kwh=round(
            trade_energy,
            2
        ),
        price_per_kwh=round(
            trade_price,
            2
        ),
        timestamp=timestamp
    )


def update_orders(
    seller,
    buyer,
    trade_energy
):
    seller.energy_kwh = round(
        max(
            0,
            seller.energy_kwh - trade_energy
        ),
        2
    )

    buyer.energy_kwh = round(
        max(
            0,
            buyer.energy_kwh - trade_energy
        ),
        2
    )


def match_orders(sell_orders, buy_orders):

    transactions = []

    if not check_orders(
        sell_orders,
        buy_orders
    ):
        return transactions

    seller_index = 0
    buyer_index = 0

    while (
        seller_index < len(sell_orders)
        and buyer_index < len(buy_orders)
    ):

        seller_index = get_next_seller(
            sell_orders,
            seller_index
        )

        buyer_index = get_next_buyer(
            buy_orders,
            buyer_index
        )

        if seller_index >= len(sell_orders):
            break

        if buyer_index >= len(buy_orders):
            break

        seller = sell_orders[seller_index]
        buyer = buy_orders[buyer_index]

        if not can_match(
            seller,
            buyer
        ):
            buyer_index += 1
            continue

        trade_energy = calculate_trade_energy(
            seller,
            buyer
        )

        trade_price = calculate_trade_price(
            seller
        )

        transaction = create_transaction(
            seller,
            buyer,
            trade_energy,
            trade_price
        )

        transactions.append(transaction)

        update_orders(
            seller,
            buyer,
            trade_energy
        )

    return transactions

