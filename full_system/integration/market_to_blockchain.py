import csv

from web3 import Web3

from market.market import create_orders
from market.matching import match_orders

from blockchain.web3.contract import (
    connect_blockchain,
    get_token_contract,
    get_trading_contract
)

from blockchain.web3.config import (
    SELLER_ADDRESS,
    BUYER_ADDRESS,
    BUYER_PRIVATE_KEY
)


CSV_FILE = "backend/data/energy_data.csv"

HOUSE_ADDRESSES = {
    "A": SELLER_ADDRESS,
    "B": BUYER_ADDRESS
}


def load_energy_data():
    energy_data = []

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            energy_data.append({
                "house_id": row["house_id"],
                "production_kwh": float(
                    row["production_kwh"]
                ),
                "consumption_kwh": float(
                    row["consumption_kwh"]
                ),
                "surplus_kwh": float(
                    row["surplus_kwh"]
                )
            })

    return energy_data


def create_market_transactions(energy_data):
    sell_orders, buy_orders = create_orders(
        energy_data
    )

    transactions = match_orders(
        sell_orders,
        buy_orders
    )

    return transactions


def convert_kwh_to_wh(energy_kwh):
    return int(
        round(energy_kwh * 1000)
    )


def calculate_total_price(
    energy_wh,
    price_per_kwh,
    decimals
):
    return (
        energy_wh
        * price_per_kwh
        * 10 ** decimals
        // 1000
    )


def ensure_allowance(
    w3,
    token,
    buyer,
    trading_address,
    required_amount
):
    allowance = token.functions.allowance(
        buyer,
        trading_address
    ).call()

    print(
        f"Current allowance: "
        f"{allowance / 10 ** token.functions.decimals().call()} ENG"
    )

    if allowance >= required_amount:
        print("Allowance is sufficient.")
        return

    print("Allowance is insufficient.")
    print("Sending approval transaction...")

    nonce = w3.eth.get_transaction_count(
        buyer
    )

    transaction = token.functions.approve(
        trading_address,
        required_amount
    ).build_transaction({
        "from": buyer,
        "nonce": nonce,
        "gas": 100000,
        "gasPrice": w3.eth.gas_price
    })

    signed = w3.eth.account.sign_transaction(
        transaction,
        BUYER_PRIVATE_KEY
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed.raw_transaction
    )

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    if receipt.status != 1:
        raise RuntimeError(
            "Approval transaction failed."
        )

    print(
        "Approval transaction:",
        tx_hash.hex()
    )


def execute_trade(
    w3,
    trading,
    seller,
    buyer,
    energy_wh,
    price_per_kwh
):
    nonce = w3.eth.get_transaction_count(
        buyer
    )

    transaction = trading.functions.executeTrade(
        seller,
        buyer,
        energy_wh,
        price_per_kwh
    ).build_transaction({
        "from": buyer,
        "nonce": nonce,
        "gas": 300000,
        "gasPrice": w3.eth.gas_price
    })

    signed = w3.eth.account.sign_transaction(
        transaction,
        BUYER_PRIVATE_KEY
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed.raw_transaction
    )

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    return tx_hash, receipt


def main():
    energy_data = load_energy_data()

    transactions = create_market_transactions(
        energy_data
    )

    if not transactions:
        print("No market transactions.")
        return

    w3 = connect_blockchain()

    token = get_token_contract(w3)
    trading = get_trading_contract(w3)

    decimals = token.functions.decimals().call()

    print("\n" + "=" * 60)
    print("MARKET → BLOCKCHAIN")
    print("=" * 60)

    for transaction in transactions:

        seller_id = transaction.seller
        buyer_id = transaction.buyer

        seller = Web3.to_checksum_address(
            HOUSE_ADDRESSES[seller_id]
        )

        buyer = Web3.to_checksum_address(
            HOUSE_ADDRESSES[buyer_id]
        )

        energy_kwh = transaction.energy_kwh

        energy_wh = convert_kwh_to_wh(
            energy_kwh
        )

        price_per_kwh = int(
            transaction.price_per_kwh
        )

        total_price = calculate_total_price(
            energy_wh,
            price_per_kwh,
            decimals
        )

        total_price_eng = (
            total_price / 10 ** decimals
        )

        print("\nSeller       :", seller_id)
        print("Buyer        :", buyer_id)
        print(
            "Energy       :",
            energy_kwh,
            "kWh"
        )
        print(
            "Energy       :",
            energy_wh,
            "Wh"
        )
        print(
            "Price        :",
            price_per_kwh,
            "Token/kWh"
        )
        print(
            "Total        :",
            total_price_eng,
            "ENG"
        )

        ensure_allowance(
            w3,
            token,
            buyer,
            trading.address,
            total_price
        )

        tx_hash, receipt = execute_trade(
            w3,
            trading,
            seller,
            buyer,
            energy_wh,
            price_per_kwh
        )

        print(
            "\nTrade transaction hash:",
            tx_hash.hex()
        )

        print(
            "Status:",
            receipt.status
        )

        print(
            "Block:",
            receipt.blockNumber
        )

        print("=" * 60)


if __name__ == "__main__":
    main()