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
    

    def average_costs(self) -> dict[str, Decimal]:
        quantities: defaultdict[str, Decimal] = defaultdict(Decimal)
        total_costs: defaultdict[str, Decimal] = defaultdict(Decimal)

        for transaction in self._transactions:
            ticker = transaction.ticker
            quantity = transaction.quantity

            if transaction.transaction_type == "BUY":
                quantities[ticker] += quantity
                total_costs[ticker] += transaction.total_amount()

            elif transaction.transaction_type == "SELL":
                if quantity > quantities[ticker]:
                    raise ValueError(
                        f"Cannot sell more {ticker} than currently owned"
                    )

                average_cost = total_costs[ticker] / quantities[ticker]

                quantities[ticker] -= quantity
                total_costs[ticker] -= average_cost * quantity

                if quantities[ticker] == Decimal("0"):
                    total_costs[ticker] = Decimal("0")

            else:
                raise ValueError(
                    "Unsupported transaction type: "
                    f"{transaction.transaction_type}"
                )

        return {
            ticker: total_costs[ticker] / quantity
            for ticker, quantity in quantities.items()
            if quantity != Decimal("0")
        }

    
    def market_values(self,price_provider: PriceProvider,) -> dict[str, Decimal]:
        return {
            ticker: quantity * price_provider.get_price(ticker)
            for ticker, quantity in self.positions().items()
        }