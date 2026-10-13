from .contract import (
    connect_blockchain,
    get_trading_contract
)


def read_trade(w3, trading, trade_id):

    trade = trading.functions.getTrade(
        trade_id
    ).call()

    seller = trade[0]
    buyer = trade[1]
    energy_wh = trade[2]
    price_per_kwh = trade[3]
    total_price = trade[4]
    timestamp = trade[5]

    return {
        "trade_id": trade_id,
        "seller": seller,
        "buyer": buyer,
        "energy_wh": energy_wh,
        "price_per_kwh": price_per_kwh,
        "total_price": total_price,
        "timestamp": timestamp
    }


def display_trade(trade):

    print("\nENERGY TRADE")
    print("-" * 40)

    print(
        "Trade ID       :",
        trade["trade_id"]
    )

    print(
        "Seller         :",
        trade["seller"]
    )

    print(
        "Buyer          :",
        trade["buyer"]
    )

    print(
        "Energy         :",
        trade["energy_wh"],
        "Wh"
    )

    print(
        "Energy         :",
        trade["energy_wh"] / 1000,
        "kWh"
    )

    print(
        "Price          :",
        trade["price_per_kwh"],
        "Token/kWh"
    )

    print(
        "Total price    :",
        trade["total_price"] / (10 ** 18),
        "ENG"
    )

    print(
        "Timestamp      :",
        trade["timestamp"]
    )


def main():

    w3 = connect_blockchain()

    trading = get_trading_contract(w3)

    trade_count = trading.functions.tradeCount().call()

    print(
        "Trade count:",
        trade_count
    )

    for trade_id in range(trade_count):

        trade = read_trade(
            w3,
            trading,
            trade_id
        )

        display_trade(trade)


if __name__ == "__main__":
    main()