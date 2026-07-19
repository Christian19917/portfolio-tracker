from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Transaction:
    transaction_date: date
    transaction_type: str
    ticker: str
    quantity: Decimal
    price: Decimal
    fees: Decimal = Decimal("0")

    def gross_amount(self) -> Decimal:
        return self.quantity * self.price

    def total_amount(self) -> Decimal:
        if self.transaction_type == "BUY":
            return self.gross_amount() + self.fees
        
        if self.transaction_type == "SELL":
            return self.gross_amount() - self.fees
        
        raise ValueError(
            f"Unsupported transaction type: {self.transaction_type}"
        )