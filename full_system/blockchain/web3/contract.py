import json
from pathlib import Path

from web3 import Web3

from .config import (
    RPC_URL,
    ENERGY_TOKEN_ADDRESS,
    ENERGY_TRADING_ADDRESS
)


BASE_DIR = Path(__file__).resolve().parents[1]


TOKEN_ABI_PATH = (
    BASE_DIR
    / "artifacts"
    / "contracts"
    / "EnergyToken.sol"
    / "EnergyToken.json"
)


TRADING_ABI_PATH = (
    BASE_DIR
    / "artifacts"
    / "contracts"
    / "EnergyTrading.sol"
    / "EnergyTrading.json"
)



def connect_blockchain():
    w3 = Web3(
        Web3.HTTPProvider(RPC_URL)
    )

    if not w3.is_connected():
        raise ConnectionError(
            "Cannot connect to blockchain"
        )

    chain_id = w3.eth.chain_id

    if chain_id != 31337:
        raise RuntimeError(
            f"Wrong blockchain network: "
            f"chain_id={chain_id}, expected=31337"
        )

    print(f"Connected to local Hardhat. Chain ID: {chain_id}")

    return w3



def load_abi(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data["abi"]


def get_token_contract(w3):

    abi = load_abi(
        TOKEN_ABI_PATH
    )

    return w3.eth.contract(
        address=Web3.to_checksum_address(
            ENERGY_TOKEN_ADDRESS
        ),
        abi=abi
    )


def get_trading_contract(w3):

    abi = load_abi(
        TRADING_ABI_PATH
    )

    return w3.eth.contract(
        address=Web3.to_checksum_address(
            ENERGY_TRADING_ADDRESS
        ),
        abi=abi
    )

def get_trade(
    w3,
    trade_id
):

    contract = get_trading_contract(
        w3
    )

    trade = contract.functions.getTrade(
        trade_id
    ).call()

    return {
        "seller": trade[0],
        "buyer": trade[1],
        "energyWh": trade[2],
        "pricePerKwh": trade[3],
        "totalPrice": trade[4],
        "timestamp": trade[5]
    }