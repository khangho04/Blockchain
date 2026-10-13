from dataclasses import dataclass


@dataclass
class EnergyOrder:

    house_id: str
    order_type: str
    energy_kwh: float
    price_per_kwh: float

    def __post_init__(self):
        self.order_type = self.order_type.upper()

        if self.order_type not in ["SELL", "BUY"]:
            raise ValueError(
                "order_type must be SELL or BUY"
            )

        if self.energy_kwh <= 0:
            raise ValueError(
                "energy_kwh must be greater than 0"
            )

        if self.price_per_kwh <= 0:
            raise ValueError(
                "price_per_kwh must be greater than 0"
            )

        self.energy_kwh = round(
            float(self.energy_kwh), 2
        )

        self.price_per_kwh = round(
            float(self.price_per_kwh), 2
        )

    def total_value(self):
        return round(
            self.energy_kwh * self.price_per_kwh,
            2
        )

    def display(self):
        print(
            f"{self.house_id} | "
            f"{self.order_type} | "
            f"{self.energy_kwh:.2f} kWh | "
            f"{self.price_per_kwh:.2f} Token/kWh"
        )

