from .contract import (
    connect_blockchain,
    get_token_contract
)

from .config import (
    OWNER_ADDRESS,
    BUYER_ADDRESS,
    SELLER_ADDRESS
)


def get_balance(
    w3,
    token,
    address
):

    address = w3.to_checksum_address(
        address
    )

    balance = token.functions.balanceOf(
        address
    ).call()

    decimals = token.functions.decimals().call()

    return balance / (10 ** decimals)


def main():

    w3 = connect_blockchain()

    token = get_token_contract(w3)

    owner_balance = get_balance(
        w3,
        token,
        OWNER_ADDRESS
    )

    buyer_balance = get_balance(
        w3,
        token,
        BUYER_ADDRESS
    )

    seller_balance = get_balance(
    w3,
    token,
    SELLER_ADDRESS
)

    print("\nENERGY TOKEN BALANCE")
    print("-" * 40)

    print(
        "Owner:",
        owner_balance,
        "ENG"
    )

    print(
        "Seller:",
        seller_balance,
        "ENG"
    )

    print(
        "Buyer:",
        buyer_balance,
        "ENG"
    )


if __name__ == "__main__":
    main()