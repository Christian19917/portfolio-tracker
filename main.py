from decimal import Decimal
from pathlib import Path

from src.portfolio import Portfolio
from src.providers.dictionary_price_provider import (
    DictionaryPriceProvider,
)
from src.transaction_reader import read_transactions


def main() -> None:
    transactions = read_transactions(
        Path("data/transactions.csv")
    )
    portfolio = Portfolio(transactions)

    price_provider = DictionaryPriceProvider({
        "VWCE": Decimal("145.32"),
        "XEON": Decimal("143.58"),
    })

    print("Positions:")
    for ticker, quantity in portfolio.positions().items():
        print(f"{ticker}: {quantity}")

    print("\nMarket values:")
    for ticker, value in portfolio.market_values(
        price_provider
    ).items():
        print(f"{ticker}: €{value:.2f}")


if __name__ == "__main__":
    main()