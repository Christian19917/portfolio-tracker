from decimal import Decimal
from typing import Protocol


class PriceProvider(Protocol):
    def get_price(self,ticker: str) -> Decimal:
        """Return the current price for the requested ticker"""
        ...