from .contract import (
    connect_blockchain,
    get_token_contract
)

from .config import (
    BUYER_ADDRESS,
    ENERGY_TRADING_ADDRESS
)


def get_allowance(
    w3,
    token
):

    buyer_address = w3.to_checksum_address(
        BUYER_ADDRESS
    )

    trading_address = w3.to_checksum_address(
        ENERGY_TRADING_ADDRESS
    )

    allowance = token.functions.allowance(
        buyer_address,
        trading_address
    ).call()

    decimals = token.functions.decimals().call()

    return allowance / (10 ** decimals)


def main():

    w3 = connect_blockchain()

    token = get_token_contract(w3)

    allowance = get_allowance(
        w3,
        token
    )

    print("\nTOKEN ALLOWANCE")
    print("-" * 40)

    print(
        "Buyer:",
        BUYER_ADDRESS
    )

    print(
        "EnergyTrading:",
        ENERGY_TRADING_ADDRESS
    )

    print(
        "Allowance:",
        allowance,
        "ENG"
    )


if __name__ == "__main__":
    main()