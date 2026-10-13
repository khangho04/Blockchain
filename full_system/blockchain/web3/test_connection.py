from contract import connect_blockchain


def main():

    w3 = connect_blockchain()

    print(
        "Connected:",
        w3.is_connected()
    )

    print(
        "Chain ID:",
        w3.eth.chain_id
    )

    print(
        "Block:",
        w3.eth.block_number
    )


if __name__ == "__main__":
    main()