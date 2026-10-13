from market.order import EnergyOrder
from market.matching import match_orders
from market.market import validate_energy_data, create_orders



def run_test(name, sell_orders, buy_orders, expected_count):
    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    transactions = match_orders(sell_orders, buy_orders)

    print("Transactions created:", len(transactions))

    # Kiểm tra số lượng giao dịch
    assert len(transactions) == expected_count, (
        f"FAILED: expected {expected_count} transactions, "
        f"got {len(transactions)}"
    )

    # Chỉ kiểm tra thuộc tính khi thực sự có giao dịch
    for index, transaction in enumerate(transactions):
        transaction.display(index)

        assert transaction.energy_kwh > 0, (
            "Energy must be positive"
        )

        assert transaction.price_per_kwh > 0, (
            "Price must be positive"
        )

        expected_total = round(
            transaction.energy_kwh * transaction.price_per_kwh,
            2,
        )

        actual_total = transaction.total_price()
        assert abs(actual_total - expected_total) < 0.001, (
            f"Incorrect total: expected {expected_total}, "
            f"got {actual_total}"
)

    print("RESULT: PASS")


def test_invalid_energy_data():
    print("\n" + "=" * 60)
    print("TEST 8-10 - INVALID ENERGY DATA")
    print("=" * 60)

    # Dữ liệu hợp lệ làm mẫu
    valid_data = {
        "house_id": "A",
        "production_kwh": 5.0,
        "consumption_kwh": 2.0,
        "surplus_kwh": 3.0,
    }

    # TEST 8: Sản lượng âm
    data = valid_data.copy()
    data["production_kwh"] = -1.0

    assert validate_energy_data(data) is False
    print("TEST 8 - NEGATIVE PRODUCTION: PASS")

    # TEST 9: Surplus là NaN
    data = valid_data.copy()
    data["surplus_kwh"] = float("nan")

    assert validate_energy_data(data) is False
    print("TEST 9 - NAN SURPLUS: PASS")

    # TEST 10: Thiếu house_id
    data = valid_data.copy()
    del data["house_id"]

    assert validate_energy_data(data) is False
    print("TEST 10 - MISSING HOUSE_ID: PASS")

    # Xác nhận dữ liệu không hợp lệ bị bỏ qua khi tạo lệnh
    invalid_data = [
        {
            "house_id": "A",
            "production_kwh": -1.0,
            "consumption_kwh": 2.0,
            "surplus_kwh": 3.0,
        },
        {
            "house_id": "B",
            "production_kwh": 5.0,
            "consumption_kwh": 2.0,
            "surplus_kwh": float("nan"),
        },
        {
            "production_kwh": 5.0,
            "consumption_kwh": 2.0,
            "surplus_kwh": 3.0,
        },
    ]

    sell_orders, buy_orders = create_orders(invalid_data)

    assert len(sell_orders) == 0
    assert len(buy_orders) == 0

    print("INVALID ORDERS REJECTED: PASS")


def test_surplus_consistency():
    print("\n" + "=" * 60)
    print("TEST 11 - SURPLUS CONSISTENCY")
    print("=" * 60)

    data = {
        "house_id": "A",
        "production_kwh": 5.0,
        "consumption_kwh": 2.0,
        "surplus_kwh": 10.0,
    }

    result = validate_energy_data(data)

    print("Production  : 5.0 kWh")
    print("Consumption : 2.0 kWh")
    print("Surplus     : 10.0 kWh")
    print(f"Validator result: {result}")


    assert result is False, (
        "Validator accepted inconsistent surplus data"
    )

    print("TEST 11: PASS")


def test_remaining_energy():
    print("\n" + "=" * 60)
    print("TEST 12 - REMAINING ENERGY AFTER MATCHING")
    print("=" * 60)

    # Seller A có 5 kWh, Buyer B cần 2 kWh
    seller = EnergyOrder(
        house_id="A",
        order_type="SELL",
        energy_kwh=5.0,
        price_per_kwh=2.0
    )

    buyer = EnergyOrder(
        house_id="B",
        order_type="BUY",
        energy_kwh=2.0,
        price_per_kwh=2.0
    )

    sell_orders = [seller]
    buy_orders = [buyer]

    transactions = match_orders(
        sell_orders,
        buy_orders
    )

    # Kiểm tra giao dịch
    assert len(transactions) == 1
    assert transactions[0].energy_kwh == 2.0

    # Kiểm tra lượng điện còn lại
    assert seller.energy_kwh == 3.0, (
        f"Expected seller remaining 3.0 kWh, "
        f"got {seller.energy_kwh}"
    )

    assert buyer.energy_kwh == 0.0, (
        f"Expected buyer remaining 0.0 kWh, "
        f"got {buyer.energy_kwh}"
    )

    print(f"Traded energy       : {transactions[0].energy_kwh:.2f} kWh")
    print(f"Seller remaining    : {seller.energy_kwh:.2f} kWh")
    print(f"Buyer remaining     : {buyer.energy_kwh:.2f} kWh")
    print("TEST 12: PASS")


def test_multiple_orders():
    print("\n" + "=" * 60)
    print("TEST 13 - MULTIPLE SELLERS AND BUYERS")
    print("=" * 60)

    sell_orders = [
        EnergyOrder("A", "SELL", 5.0, 2.0),
        EnergyOrder("C", "SELL", 3.0, 2.0),
    ]

    buy_orders = [
        EnergyOrder("B", "BUY", 4.0, 3.0),
        EnergyOrder("D", "BUY", 2.0, 2.0),
    ]

    transactions = match_orders(sell_orders, buy_orders)

    total_traded = round(
        sum(tx.energy_kwh for tx in transactions), 2
    )

    assert len(transactions) == 3, (
        f"Expected 3 transactions, got {len(transactions)}"
    )
    assert total_traded == 6.0, (
        f"Expected 6.0 kWh traded, got {total_traded}"
    )

    assert sell_orders[0].energy_kwh == 0.0
    assert sell_orders[1].energy_kwh == 2.0
    assert buy_orders[0].energy_kwh == 0.0
    assert buy_orders[1].energy_kwh == 0.0

    print(f"Transactions       : {len(transactions)}")
    print(f"Total traded       : {total_traded:.2f} kWh")
    print(f"Seller A remaining : {sell_orders[0].energy_kwh:.2f} kWh")
    print(f"Seller C remaining : {sell_orders[1].energy_kwh:.2f} kWh")
    print("TEST 13: PASS")


def main():
    # TEST 1: Chỉ có người bán
    run_test(
        "TEST 1 - SELLERS ONLY",
        [EnergyOrder("A", "SELL", 4.0, 2.0)],
        [],
        0,
    )

    # TEST 2: Chỉ có người mua
    run_test(
        "TEST 2 - BUYERS ONLY",
        [],
        [EnergyOrder("B", "BUY", 2.0, 2.0)],
        0,
    )

    # TEST 3: Thị trường trống
    run_test(
        "TEST 3 - EMPTY MARKET",
        [],
        [],
        0,
    )

    # TEST 4: Giá mua thấp hơn giá bán
    run_test(
        "TEST 4 - NO PRICE MATCH",
        [EnergyOrder("A", "SELL", 4.0, 3.0)],
        [EnergyOrder("B", "BUY", 2.0, 2.0)],
        0,
    )

    # TEST 5: Ghép lệnh bình thường
    run_test(
        "TEST 5 - NORMAL MATCH",
        [EnergyOrder("A", "SELL", 4.0, 2.0)],
        [EnergyOrder("B", "BUY", 3.0, 2.0)],
        1,
    )

    # TEST 6: Người mua mua một phần lượng điện của người bán
    run_test(
        "TEST 6 - PARTIAL SELLER FILL",
        [EnergyOrder("A", "SELL", 4.0, 2.0)],
        [EnergyOrder("B", "BUY", 2.0, 3.0)],
        1,
    )

    # TEST 7: Lượng bán lớn hơn lượng mua
    run_test(
        "TEST 7 - SELLER HAS REMAINING ENERGY",
        [EnergyOrder("A", "SELL", 5.0, 2.0)],
        [EnergyOrder("B", "BUY", 2.0, 2.0)],
        1,
    )
    test_invalid_energy_data()
    test_surplus_consistency()
    test_remaining_energy()
    test_multiple_orders()
    print("\nAll edge-case tests passed.")


if __name__ == "__main__":
    main()