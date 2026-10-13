from .contract import (
    connect_blockchain,
    get_trading_contract
)

from .config import (
    BUYER_ADDRESS,
    BUYER_PRIVATE_KEY,
    SELLER_ADDRESS
)


def create_transaction(
    w3,
    trading
):

    buyer_address = w3.to_checksum_address(
        BUYER_ADDRESS
    )

    seller_address = w3.to_checksum_address(
        SELLER_ADDRESS
    )

    energy_wh = 1800
    price_per_kwh = 2

    nonce = w3.eth.get_transaction_count(
        buyer_address
    )

    transaction = trading.functions.executeTrade(
        seller_address,
        buyer_address,
        energy_wh,
        price_per_kwh
    ).build_transaction({
        "from": buyer_address,
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
        "gas": 500000,
        "gasPrice": w3.eth.gas_price
    })

    return transaction


def send_transaction(
    w3,
    transaction
):

    signed = w3.eth.account.sign_transaction(
        transaction,
        BUYER_PRIVATE_KEY
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed.raw_transaction
    )

    return tx_hash


def main():

    w3 = connect_blockchain()

    trading = get_trading_contract(w3)

    transaction = create_transaction(
        w3,
        trading
    )

    tx_hash = send_transaction(
        w3,
        transaction
    )

    print(
        "Transaction:",
        tx_hash.hex()
    )

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash
    )

    print(
        "Status:",
        receipt.status
    )

    print(
        "Block:",
        receipt.blockNumber
    )


if __name__ == "__main__":
    main()