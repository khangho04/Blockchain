from web3 import Web3
from copy import deepcopy

from integration.ai_processor import predict_all_houses
from market.market import create_orders
from market.matching import match_orders

from blockchain.web3.contract import (
    connect_blockchain,
    get_token_contract,
    get_trading_contract,
    get_trade
)

from blockchain.web3.config import (
    SELLER_ADDRESS,
    BUYER_ADDRESS,
    BUYER_PRIVATE_KEY
)


HOUSE_ADDRESSES = {
    "A": SELLER_ADDRESS,
    "B": BUYER_ADDRESS
}


def convert_ai_results_to_energy_data(results):
    energy_data = []

    for result in results:
        energy_data.append({
            "house_id": result["house_id"],
            "production_kwh": result["predicted_production"],
            "consumption_kwh": result["predicted_consumption"],
            "surplus_kwh": result["predicted_surplus"]
        })

    return energy_data


def create_market_transactions(energy_data):
    sell_orders, buy_orders = create_orders(
        energy_data
    )

    # Lưu trạng thái lệnh ban đầu để hiển thị
    display_sell_orders = deepcopy(sell_orders)
    display_buy_orders = deepcopy(buy_orders)

    # Hàm này sẽ cập nhật lượng điện còn lại trong các lệnh gốc
    transactions = match_orders(
        sell_orders,
        buy_orders
    )

    return (
        display_sell_orders,
        display_buy_orders,
        transactions
    )


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

def ensure_buyer_balance(
    w3,
    token,
    buyer,
    required_amount,
    decimals
):
    buyer = Web3.to_checksum_address(buyer)

    # Tai khoan deployer dau tien cua Hardhat local
    owner = Web3.to_checksum_address(w3.eth.accounts[0])

    # Xac nhan deployer la owner cua EnergyToken
    contract_owner = Web3.to_checksum_address(
        token.functions.owner().call()
    )

    if contract_owner != owner:
        raise RuntimeError(
            "Hardhat accounts[0] khong phai owner cua EnergyToken. "
            "Hay kiem tra lai tai khoan deploy contract."
        )

    balance = token.functions.balanceOf(buyer).call()

    print(
        f"Buyer balance: "
        f"{balance / (10 ** decimals):.6f} ENG"
    )
    print(
        f"Required payment: "
        f"{required_amount / (10 ** decimals):.6f} ENG"
    )

    if balance >= required_amount:
        print("Buyer token balance is sufficient.")
        return

    amount_to_mint = required_amount - balance

    print(
        f"Minting {amount_to_mint / (10 ** decimals):.6f} ENG "
        f"to Buyer..."
    )

    tx_hash = token.functions.mint(
        buyer,
        amount_to_mint
    ).transact({
        "from": owner,
        "gas": 200000
    })

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status != 1:
        raise RuntimeError("Mint transaction failed.")

    new_balance = token.functions.balanceOf(buyer).call()

    print("Mint transaction:", tx_hash.hex())
    print(
        f"Buyer balance after mint: "
        f"{new_balance / (10 ** decimals):.6f} ENG"
    )

    if new_balance < required_amount:
        raise RuntimeError("Buyer balance is still insufficient.")

def ensure_allowance(
    w3,
    token,
    buyer,
    trading_address,
    required_amount
):
    decimals = token.functions.decimals().call()

    allowance = token.functions.allowance(
        buyer,
        trading_address
    ).call()

    print(
        f"Current allowance: "
        f"{allowance / 10 ** decimals:.2f} ENG"
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


def display_ai_results(results):
    print("\n" + "=" * 60)
    print("AI PREDICTION")
    print("=" * 60)

    for result in results:
        print(
            f"House {result['house_id']} | "
            f"Production: "
            f"{result['predicted_production']} kWh | "
            f"Consumption: "
            f"{result['predicted_consumption']} kWh | "
            f"Surplus: "
            f"{result['predicted_surplus']} kWh | "
            f"Status: "
            f"{result['status']}"
        )


def display_market(
    sell_orders,
    buy_orders,
    transactions
):
    print("\n" + "=" * 60)
    print("P2P MARKET")
    print("=" * 60)

    print("\nSELL ORDERS")
    print("-" * 60)

    for order in sell_orders:
        order.display()

    print("\nBUY ORDERS")
    print("-" * 60)

    for order in buy_orders:
        order.display()

    print("\nP2P TRANSACTIONS")
    print("-" * 60)

    if not transactions:
        print("No transactions.")
        return

    for index, transaction in enumerate(
        transactions,
        start=1
    ):
        transaction.display(index)

def verify_trade(
    w3,
    trading,
    trade_id,
    expected_seller,
    expected_buyer,
    expected_energy_wh,
    expected_price_per_kwh,
    expected_total_price
):
    trade = get_trade(
        w3,
        trade_id
    )

    seller = Web3.to_checksum_address(
        trade["seller"]
    )

    buyer = Web3.to_checksum_address(
        trade["buyer"]
    )

    energy_wh = trade["energyWh"]
    price_per_kwh = trade["pricePerKwh"]
    total_price = trade["totalPrice"]

    print("\n" + "=" * 60)
    print("BLOCKCHAIN VERIFICATION")
    print("=" * 60)

    print("Trade ID       :", trade_id)
    print("Seller         :", seller)
    print("Buyer          :", buyer)
    print("Energy         :", energy_wh, "Wh")
    print("Price          :", price_per_kwh, "Token/kWh")
    print(
        "Total          :",
        total_price / 10 ** 18,
        "ENG"
    )

    verification = (
        seller == expected_seller
        and buyer == expected_buyer
        and energy_wh == expected_energy_wh
        and price_per_kwh == expected_price_per_kwh
        and total_price == expected_total_price
    )

    if verification:
        print("\nVerification   : SUCCESS")
    else:
        print("\nVerification   : FAILED")

    print("=" * 60)

    return verification


def main():
    print("\n" + "=" * 60)
    print("END-TO-END ENERGY TRADING")
    print("=" * 60)

    results = predict_all_houses(
        hour=12
    )

    display_ai_results(
        results
    )

    energy_data = (
        convert_ai_results_to_energy_data(
            results
        )
    )

    sell_orders, buy_orders, transactions = (
        create_market_transactions(
            energy_data
        )
    )

    display_market(
        sell_orders,
        buy_orders,
        transactions
    )

    if not transactions:
        print("\nNo blockchain transaction required.")
        return

    w3 = connect_blockchain()

    token = get_token_contract(w3)
    trading = get_trading_contract(w3)

    decimals = token.functions.decimals().call()

    print("\n" + "=" * 60)
    print("MARKET → BLOCKCHAIN")
    print("=" * 60)
    
    trade_count_before = trading.functions.tradeCount().call()

    for transaction in transactions:
        seller_id = transaction.seller
        buyer_id = transaction.buyer

        if seller_id not in HOUSE_ADDRESSES:
            raise ValueError(f"Unknown seller: {seller_id}")

        if buyer_id not in HOUSE_ADDRESSES:
            raise ValueError(f"Unknown buyer: {buyer_id}")

        seller = Web3.to_checksum_address(
            HOUSE_ADDRESSES[seller_id]
        )
        buyer = Web3.to_checksum_address(
            HOUSE_ADDRESSES[buyer_id]
        )

        energy_kwh = transaction.energy_kwh
        energy_wh = convert_kwh_to_wh(energy_kwh)
        price_per_kwh = int(transaction.price_per_kwh)

        total_price = calculate_total_price(
            energy_wh,
            price_per_kwh,
            decimals
        )
        total_price_eng = total_price / 10 ** decimals

        print("\nSeller       :", seller_id)
        print("Seller addr  :", seller)
        print("Buyer        :", buyer_id)
        print("Buyer addr   :", buyer)
        print("Energy       :", energy_kwh, "kWh")
        print("Energy       :", energy_wh, "Wh")
        print("Price        :", price_per_kwh, "Token/kWh")
        print("Total        :", total_price_eng, "ENG")

        
        ensure_buyer_balance(
            w3,
            token,
            buyer,
            total_price,
            decimals
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

        print("\nTrade transaction hash:", tx_hash.hex())
        print("Status:", receipt.status)
        print("Block:", receipt.blockNumber)

        if receipt.status != 1:
            raise RuntimeError("Trade transaction failed.")

        trade_id = trading.functions.tradeCount().call() - 1

        verification = verify_trade(
            w3,
            trading,
            trade_id,
            seller,
            buyer,
            energy_wh,
            price_per_kwh,
            total_price
        )

        if not verification:
            raise RuntimeError(
                f"Blockchain verification failed for trade {trade_id}."
            )

    print(
        "\nNew trades recorded:",
        trading.functions.tradeCount().call() - trade_count_before
    )




if __name__ == "__main__":
    main()