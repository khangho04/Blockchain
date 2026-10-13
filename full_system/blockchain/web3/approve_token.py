from .contract import (
    connect_blockchain,
    get_token_contract
)

from .config import (
    BUYER_ADDRESS,
    BUYER_PRIVATE_KEY,
    ENERGY_TRADING_ADDRESS
)


def create_transaction(
    w3,
    token
):

    buyer_address = w3.to_checksum_address(
        BUYER_ADDRESS
    )

    trading_address = w3.to_checksum_address(
        ENERGY_TRADING_ADDRESS
    )

    amount = w3.to_wei(
        3.6,
        "ether"
    )

    nonce = w3.eth.get_transaction_count(
        buyer_address
    )

    transaction = token.functions.approve(
        trading_address,
        amount
    ).build_transaction({
        "from": buyer_address,
        "nonce": nonce,
        "chainId": w3.eth.chain_id,
        "gas": 100000,
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

    token = get_token_contract(w3)

    transaction = create_transaction(
        w3,
        token
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