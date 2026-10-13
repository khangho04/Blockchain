from dataclasses import dataclass


@dataclass
class EnergyTransaction:

    seller: str
    buyer: str
    energy_kwh: float
    price_per_kwh: float
    timestamp: str

    def __post_init__(self):
        self.energy_kwh = round(
            float(self.energy_kwh), 2
        )

        self.price_per_kwh = round(
            float(self.price_per_kwh), 2
        )

    def total_price(self):
        return round(
            self.energy_kwh * self.price_per_kwh,
            2
        )

    def to_dict(self):
        return {
            "seller": self.seller,
            "buyer": self.buyer,
            "energy_kwh": self.energy_kwh,
            "price_per_kwh": self.price_per_kwh,
            "total_price": self.total_price(),
            "timestamp": self.timestamp
        }

    def display(self, transaction_id):
        print(f"Transaction {transaction_id}")
        print(f"Seller       : {self.seller}")
        print(f"Buyer        : {self.buyer}")
        print(
            f"Energy       : "
            f"{self.energy_kwh:.2f} kWh"
        )
        print(
            f"Price        : "
            f"{self.price_per_kwh:.2f} Token/kWh"
        )
        print(
            f"Total        : "
            f"{self.total_price():.2f} Token"
        )
        print(f"Timestamp    : {self.timestamp}")

