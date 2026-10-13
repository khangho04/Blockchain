from .contract import (
    connect_blockchain,
    get_token_contract
)

from .config import (
    OWNER_ADDRESS,
    OWNER_PRIVATE_KEY,
    BUYER_ADDRESS
)


def create_transaction(
    w3,
    token
):

    owner_address = w3.to_checksum_address(
        OWNER_ADDRESS
    )

    buyer_address = w3.to_checksum_address(
        BUYER_ADDRESS
    )

    amount = w3.to_wei(
        100,
        "ether"
    )

    nonce = w3.eth.get_transaction_count(
        owner_address
    )

    transaction = token.functions.transfer(
        buyer_address,
        amount
    ).build_transaction({
        "from": owner_address,
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
        OWNER_PRIVATE_KEY
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