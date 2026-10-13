
from web3 import Web3
from blockchain.web3.contract import connect_blockchain, get_token_contract
from blockchain.web3.config import (
    OWNER_PRIVATE_KEY,
    BUYER_ADDRESS,
    SELLER_ADDRESS,
)

# Kết nối blockchain local
w3 = connect_blockchain()
token = get_token_contract(w3)

# Địa chỉ owner lấy trực tiếp từ Smart Contract
owner_address = Web3.to_checksum_address(
    token.functions.owner().call()
)

buyer = Web3.to_checksum_address(BUYER_ADDRESS)
seller = Web3.to_checksum_address(SELLER_ADDRESS)

# Cấp 100 ENG cho Buyer và 100 ENG cho Seller
amount = Web3.to_wei(100, "ether")

for address, name in [(buyer, "Buyer B"), (seller, "Seller A")]:
    tx = token.functions.mint(
        address, amount
    ).build_transaction({
        "from": owner_address,
        "nonce": w3.eth.get_transaction_count(owner_address),
        "chainId": w3.eth.chain_id,
        "gas": 150000,
        "gasPrice": w3.eth.gas_price,
    })

    signed_tx = w3.eth.account.sign_transaction(
        tx, private_key=OWNER_PRIVATE_KEY
    )

    tx_hash = w3.eth.send_raw_transaction(
        signed_tx.raw_transaction
    )
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status != 1:
        raise RuntimeError(f"Mint failed for {name}")

    print(f"{name}: minted 100 ENG")
    print(f"Transaction: {tx_hash.hex()}")

print("\nToken balances:")
for address, name in [(buyer, "Buyer B"), (seller, "Seller A")]:
    balance = token.functions.balanceOf(address).call()
    print(f"{name}: {Web3.from_wei(balance, 'ether')} ENG")