import pandas as pd
from pathlib import Path

from AI_model.predict import predict_energy


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKEND_DATA = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "energy_data.csv"
)

REQUIRED_COLUMNS = [
    "timestamp",
    "hour",
    "house_id",
    "temperature",
    "humidity",
    "solar_irradiance",
]

HOUSES = ["A", "B", "C"]


def load_iot_data(hour=None):
    """
    Đọc dữ liệu Backend và lấy bản ghi mới nhất
    của từng hộ. Nếu truyền hour, chỉ xét giờ đó.
    """

    if not BACKEND_DATA.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file dữ liệu: {BACKEND_DATA}"
        )

    df = pd.read_csv(BACKEND_DATA)

    if df.empty:
        raise ValueError(
            "File energy_data.csv chưa có dữ liệu."
        )

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"CSV thiếu các cột: {missing_columns}"
        )

    # Chuẩn hóa dữ liệu đầu vào
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    df["hour"] = pd.to_numeric(
        df["hour"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "timestamp",
            "hour",
            "house_id",
            "temperature",
            "humidity",
            "solar_irradiance",
        ]
    ).copy()

    if hour is not None:
        df = df[df["hour"] == hour].copy()

    if df.empty:
        raise ValueError(
            f"Không có dữ liệu hợp lệ cho hour={hour}."
        )

    # Sắp xếp theo thời gian để chọn bản ghi mới nhất
    df = df.sort_values("timestamp")

    # Mỗi hộ chỉ lấy bản ghi mới nhất
    latest_rows = (
        df.drop_duplicates(
            subset=["house_id"],
            keep="last"
        )
    )

    return latest_rows


def predict_all_houses(hour=12):
    """
    Dự đoán năng lượng cho A, B, C dựa trên
    dữ liệu thời tiết và giờ lấy từ Backend CSV.
    """

    df = load_iot_data(hour=hour)

    results = []

    for house_id in HOUSES:

        house_data = df[
            df["house_id"] == house_id
        ]

        if house_data.empty:
            raise ValueError(
                f"Không có dữ liệu phù hợp cho hộ {house_id}."
            )

        row = house_data.iloc[-1]

        result = predict_energy(
            house_id=house_id,
            hour=int(row["hour"]),
            temperature=float(row["temperature"]),
            humidity=float(row["humidity"]),
            solar_irradiance=float(
                row["solar_irradiance"]
            ),
        )

        # Gắn timestamp dữ liệu nguồn để dễ đối chiếu
        result["source_timestamp"] = (
            row["timestamp"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        results.append(result)

    return results


def display_predictions(results):

    print("\n" + "=" * 70)
    print("AI PREDICTION FROM BACKEND CSV")
    print("=" * 70)

    for result in results:

        print(
            f"House {result['house_id']} | "
            f"Source time: {result['source_timestamp']} | "
            f"Production: "
            f"{result['predicted_production']} kWh | "
            f"Consumption: "
            f"{result['predicted_consumption']} kWh | "
            f"Surplus: "
            f"{result['predicted_surplus']} kWh | "
            f"Status: {result['status']}"
        )


def main():

    results = predict_all_houses(hour=12)

    display_predictions(results)


if __name__ == "__main__":
    main()

