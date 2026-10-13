from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from web3 import Web3

from market.market import create_orders
from market.matching import match_orders


# =====================================================
# CONFIGURATION
# =====================================================

ROOT = Path(__file__).resolve().parent
CSV_FILE = ROOT / "backend" / "data" / "energy_data.csv"

RPC_URL = "http://127.0.0.1:8545"

st.set_page_config(
    page_title="P2P Energy Trading",
    page_icon="⚡",
    layout="wide",
)

st.title("⚡ P2P Solar Energy Trading")
st.caption(
    "IoT Monitoring | AI Prediction | P2P Market | Blockchain"
)


# =====================================================
# AI MODEL
# =====================================================

@st.cache_resource
def load_ai_model():
    try:
        from AI_model.predict import predict_energy
        return predict_energy, None
    except Exception as first_error:
        try:
            from ai_model.predict import predict_energy
            return predict_energy, None
        except Exception as second_error:
            return None, (
                f"Không tải được AI model. "
                f"Chi tiết: {first_error}; {second_error}"
            )


def solar_irradiance_by_hour(hour):
    profile = [
        0, 0, 0, 0, 0, 0,
        50, 150, 300, 450, 600, 750,
        850, 900, 850, 700, 500, 250,
        50, 0, 0, 0, 0, 0
    ]
    return profile[int(hour) % 24]


def get_prediction(row, predict_energy):
    house_id = str(row["house_id"])
    timestamp = pd.to_datetime(row["timestamp"], errors="coerce")

    if pd.isna(timestamp):
        timestamp = pd.Timestamp.now()

    hour = (
    int(row["hour"])
    if "hour" in row.index and pd.notna(row["hour"])
    else int(timestamp.hour)
)

    # Dùng giá trị thực trong CSV nếu có.
    # Nếu thiếu dữ liệu môi trường, dùng giá trị mô phỏng.
    temperature = (
        float(row["temperature"])
        if "temperature" in row.index
        and pd.notna(row["temperature"])
        else 30.0
    )

    humidity = (
        float(row["humidity"])
        if "humidity" in row.index
        and pd.notna(row["humidity"])
        else 70.0
    )

    irradiance = (
        float(row["solar_irradiance"])
        if "solar_irradiance" in row.index
        and pd.notna(row["solar_irradiance"])
        else solar_irradiance_by_hour(hour)
    )

    result = predict_energy(
        house_id=house_id,
        hour=hour,
        temperature=temperature,
        humidity=humidity,
        solar_irradiance=irradiance,
    )

    return {
        "house_id": house_id,
        "timestamp": timestamp,
        "production_kwh": float(
            result["predicted_production"]
        ),
        "consumption_kwh": float(
            result["predicted_consumption"]
        ),
        "surplus_kwh": float(
            result["predicted_surplus"]
        ),
        "status": result["status"],
        "temperature": temperature,
        "humidity": humidity,
        "solar_irradiance": irradiance,
    }


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Điều khiển")

if st.sidebar.button("🔄 Làm mới dữ liệu", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(
    "Dashboard không tự gửi giao dịch Blockchain."
)


# =====================================================
# LOAD IOT DATA
# =====================================================

@st.cache_data(ttl=10)
def load_csv(path, modified_time):
    return pd.read_csv(path)


if not CSV_FILE.exists():
    st.error(f"Không tìm thấy file dữ liệu: {CSV_FILE}")
    st.info(
        "Hãy kiểm tra Backend đã ghi dữ liệu vào "
        "backend/data/energy_data.csv chưa."
    )
    st.stop()

try:
    raw_df = load_csv(
        str(CSV_FILE),
        CSV_FILE.stat().st_mtime,
    )
except Exception as exc:
    st.error(f"Không đọc được CSV: {exc}")
    st.stop()

required_columns = {
    "timestamp",
    "house_id",
    "production_kwh",
    "consumption_kwh",
}

missing = required_columns - set(raw_df.columns)

if missing:
    st.error(f"CSV thiếu các cột: {', '.join(sorted(missing))}")
    st.stop()

raw_df["timestamp"] = pd.to_datetime(
    raw_df["timestamp"],
    errors="coerce",
)

raw_df = raw_df.dropna(
    subset=["timestamp", "house_id"]
)

if raw_df.empty:
    st.warning("CSV chưa có dữ liệu hợp lệ.")
    st.stop()

# Lấy bản ghi mới nhất của mỗi hộ.
latest_df = (
    raw_df.sort_values("timestamp")
    .groupby("house_id", as_index=False)
    .tail(1)
    .copy()
    .reset_index(drop=True)
)


# =====================================================
# IOT SECTION
# =====================================================

st.header("1. IoT Monitoring")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Số hộ có dữ liệu", len(latest_df))
col2.metric(
    "Tổng sản lượng ghi nhận",
    f"{latest_df['production_kwh'].sum():.2f} kWh",
)
col3.metric(
    "Tổng tiêu thụ ghi nhận",
    f"{latest_df['consumption_kwh'].sum():.2f} kWh",
)
col4.metric(
    "Thời điểm dữ liệu mới nhất",
    latest_df["timestamp"].max().strftime("%H:%M:%S"),
)

st.dataframe(
    latest_df,
    use_container_width=True,
    hide_index=True,
)


# =====================================================
# AI SECTION
# =====================================================

st.header("2. AI Energy Prediction")

predict_energy, ai_error = load_ai_model()

prediction_df = None

if predict_energy is None:
    st.error(ai_error)
    st.warning(
        "Kiểm tra tên thư mục AI_model/ai_model "
        "và file predict.py."
    )
else:
    try:
        predictions = [
            get_prediction(row, predict_energy)
            for _, row in latest_df.iterrows()
        ]

        prediction_df = pd.DataFrame(predictions)

        st.caption(
            "Nếu CSV thiếu temperature, humidity hoặc "
            "solar_irradiance, Dashboard sử dụng giá trị "
            "mô phỏng; các giá trị này không phải dữ liệu "
            "cảm biến thực."
        )

        ai_col1, ai_col2, ai_col3 = st.columns(3)

        ai_col1.metric(
            "Dự đoán sản lượng",
            f"{prediction_df['production_kwh'].sum():.2f} kWh",
        )

        ai_col2.metric(
            "Dự đoán tiêu thụ",
            f"{prediction_df['consumption_kwh'].sum():.2f} kWh",
        )

        ai_col3.metric(
            "Tổng điện dư/thiếu",
            f"{prediction_df['surplus_kwh'].sum():.2f} kWh",
        )

        st.dataframe(
            prediction_df[
                [
                    "house_id",
                    "production_kwh",
                    "consumption_kwh",
                    "surplus_kwh",
                    "status",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        chart_df = prediction_df.melt(
            id_vars="house_id",
            value_vars=[
                "production_kwh",
                "consumption_kwh",
            ],
            var_name="Loại năng lượng",
            value_name="kWh",
        )

        fig = px.bar(
            chart_df,
            x="house_id",
            y="kWh",
            color="Loại năng lượng",
            barmode="group",
            title="AI: Sản lượng dự đoán và tiêu thụ dự đoán",
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as exc:
        st.error(f"Lỗi khi dự đoán AI: {exc}")


# =====================================================
# P2P MARKET SECTION
# =====================================================

st.header("3. P2P Energy Market")

if prediction_df is not None:
    try:
        market_data = prediction_df[
            [
                "house_id",
                "production_kwh",
                "consumption_kwh",
                "surplus_kwh",
            ]
        ].to_dict("records")

        sell_orders, buy_orders = create_orders(market_data)

        st.subheader("Lệnh bán")
        if sell_orders:
            st.dataframe(
                pd.DataFrame([
                    {
                        "House": order.house_id,
                        "Energy (kWh)": order.energy_kwh,
                        "Price (Token/kWh)": order.price_per_kwh,
                    }
                    for order in sell_orders
                ]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Không có lệnh bán.")

        st.subheader("Lệnh mua")
        if buy_orders:
            st.dataframe(
                pd.DataFrame([
                    {
                        "House": order.house_id,
                        "Energy (kWh)": order.energy_kwh,
                        "Price (Token/kWh)": order.price_per_kwh,
                    }
                    for order in buy_orders
                ]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Không có lệnh mua.")

        # Tạo lệnh và khớp trong bộ nhớ; không ghi Blockchain.
        transactions = match_orders(sell_orders, buy_orders)

        total_energy = round(
            sum(tx.energy_kwh for tx in transactions), 2
        )

        total_value = round(
            sum(tx.total_price() for tx in transactions), 2
        )

        market_col1, market_col2, market_col3 = st.columns(3)

        market_col1.metric(
            "Số giao dịch khớp",
            len(transactions),
        )

        market_col2.metric(
            "Năng lượng giao dịch",
            f"{total_energy:.2f} kWh",
        )

        market_col3.metric(
            "Tổng giá trị",
            f"{total_value:.2f} Token",
        )

        if transactions:
            tx_df = pd.DataFrame([
                {
                    "Seller": tx.seller,
                    "Buyer": tx.buyer,
                    "Energy (kWh)": tx.energy_kwh,
                    "Price (Token/kWh)": tx.price_per_kwh,
                    "Total (Token)": tx.total_price(),
                    "Timestamp": tx.timestamp,
                }
                for tx in transactions
            ])

            st.subheader("Kết quả khớp lệnh")
            st.dataframe(
                tx_df,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "Chưa có giao dịch khớp. Có thể thị trường "
                "chưa có cả bên mua và bên bán."
            )

    except Exception as exc:
        st.error(f"Lỗi khi chạy P2P Market: {exc}")
else:
    st.info("Cần AI chạy thành công trước khi mô phỏng Market.")


# =====================================================
# BLOCKCHAIN SECTION - READ ONLY
# =====================================================

st.header("4. Blockchain Status")

try:
    # Dùng các hàm đã có trong dự án.
    from blockchain.web3.contract import (
        connect_blockchain,
        get_trading_contract,
        get_trade,
    )

    w3 = connect_blockchain()
    trading_contract = get_trading_contract(w3)

    chain_id = w3.eth.chain_id
    block_number = w3.eth.block_number

    # Đọc số lượng giao dịch đã ghi trên Smart Contract.
    trade_count = trading_contract.functions.tradeCount().call()

    bc_col1, bc_col2, bc_col3, bc_col4 = st.columns(4)

    bc_col1.metric("Kết nối RPC", "Connected")
    bc_col2.metric("Chain ID", chain_id)
    bc_col3.metric("Block hiện tại", block_number)
    bc_col4.metric("Số giao dịch on-chain", trade_count)

    if trade_count > 0:
        st.subheader("Giao dịch Blockchain gần nhất")

        # Trade ID bắt đầu từ 0, nên giao dịch cuối cùng là count - 1.
        latest_trade_id = trade_count - 1
        trade = get_trade(w3, latest_trade_id)

        energy_kwh = trade["energyWh"] / 1000

        # Web3 trả về số nguyên theo đơn vị token nhỏ nhất.
        # EnergyToken sử dụng 18 decimals theo cấu hình hiện tại.
        total_token = trade["totalPrice"] / (10 ** 18)

        # Đơn vị pricePerKwh phụ thuộc cách Smart Contract lưu giá.
        # Không tự quy đổi khi chưa xác nhận đơn vị trong contract.
        latest_trade_df = pd.DataFrame([{
            "Trade ID": latest_trade_id,
            "Seller": trade["seller"],
            "Buyer": trade["buyer"],
            "Energy (kWh)": round(energy_kwh, 3),
            "Total (Token)": round(total_token, 6),
            "Timestamp": datetime.fromtimestamp(
                trade["timestamp"]
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }])

        st.dataframe(
            latest_trade_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Smart Contract chưa ghi nhận giao dịch nào.")

    st.caption(
        "Chế độ chỉ đọc: Dashboard không gửi transaction."
    )

except Exception as exc:
    st.warning(
        f"Không đọc được dữ liệu Smart Contract: {exc}"
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()
st.caption(
    f"CSV: {CSV_FILE} | Dashboard cập nhật khi bạn làm mới trang. "
    f"Thời gian hiển thị: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)   

