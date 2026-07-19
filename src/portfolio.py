from collections import defaultdict
from decimal import Decimal

from src.providers.price_provider import PriceProvider
from src.transaction import Transaction


class Portfolio:
    def __init__(self, transactions: list[Transaction]) -> None:
        self._transactions = tuple(transactions)

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return self._transactions

    def positions(self) -> dict[str, Decimal]:
        positions: defaultdict[str, Decimal] = defaultdict(Decimal)

        for transaction in self._transactions:
            ticker = transaction.ticker
            quantity = transaction.quantity

            if transaction.transaction_type == "BUY":
                positions[ticker] += quantity

            elif transaction.transaction_type == "SELL":
                if quantity > positions[ticker]:
                    raise ValueError(
                        f"Cannot sell more {ticker} than currently owned"
                    )

                positions[ticker] -= quantity

            else:
                raise ValueError(
                    "Unsupported transaction type: "
                    f"{transaction.transaction_type}"
                )

        return {
            ticker: quantity
            for ticker, quantity in positions.items()
            if quantity != Decimal("0")
        }
    
    def market_values(self,price_provider: PriceProvider,) -> dict[str, Decimal]:
        return {
            ticker: quantity * price_provider.get_price(ticker)
            for ticker, quantity in self.positions().items()
        }