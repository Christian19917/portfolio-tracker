from decimal import Decimal
from typing import Mapping


class DictionaryPriceProvider:
    def __init__(self, prices: Mapping[str, Decimal]) -> None:
        self._prices = {
            ticker.strip().upper(): price
            for ticker, price in prices.items()
        }

    def get_price(self, ticker: str) -> Decimal:
        normalized_ticker = ticker.strip().upper()

        try:
            return self._prices[normalized_ticker]
        except KeyError as error:
            raise ValueError(
                f"Price not available for ticker: {normalized_ticker}"
            ) from error