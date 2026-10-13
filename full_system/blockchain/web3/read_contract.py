from contract import (
    connect_blockchain,
    get_token_contract,
    get_trading_contract
)


def read_token(w3):

    token = get_token_contract(w3)

    name = token.functions.name().call()
    symbol = token.functions.symbol().call()
    decimals = token.functions.decimals().call()
    total_supply = token.functions.totalSupply().call()

    print("\nENERGY TOKEN")
    print("-" * 40)
    print("Name       :", name)
    print("Symbol     :", symbol)
    print("Decimals   :", decimals)
    print(
        "Total supply:",
        total_supply / (10 ** decimals),
        symbol
    )


def read_trading(w3):

    trading = get_trading_contract(w3)

    trade_count = trading.functions.tradeCount().call()

    print("\nENERGY TRADING")
    print("-" * 40)
    print("Trade count:", trade_count)


def main():

    w3 = connect_blockchain()

    read_token(w3)
    read_trading(w3)


if __name__ == "__main__":
    main()