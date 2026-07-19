from decimal import Decimal, InvalidOperation
from typing import Mapping

import yfinance as yf


class YahooPriceProvider:
    """Retrieve the latest available market price from Yahoo Finance."""

    def __init__(
        self,
        ticker_mapping: Mapping[str, str] | None = None,
    ) -> None:
        self._ticker_mapping = {
            ticker.strip().upper(): yahoo_ticker.strip().upper()
            for ticker, yahoo_ticker in (ticker_mapping or {}).items()
        }

    def get_price(self, ticker: str) -> Decimal:
        normalized_ticker = ticker.strip().upper()

        yahoo_ticker = self._ticker_mapping.get(
            normalized_ticker,
            normalized_ticker,
        )

        try:
            history = yf.Ticker(yahoo_ticker).history(
                period="5d",
                auto_adjust=False,
            )
        except Exception as error:
            raise ValueError(
                f"Could not retrieve price for ticker: "
                f"{normalized_ticker}"
            ) from error

        if history.empty or "Close" not in history:
            raise ValueError(
                f"Price not available for ticker: "
                f"{normalized_ticker}"
            )

        closing_prices = history["Close"].dropna()

        if closing_prices.empty:
            raise ValueError(
                f"Price not available for ticker: "
                f"{normalized_ticker}"
            )

        latest_price = closing_prices.iloc[-1]

        try:
            return Decimal(str(latest_price))
        except (InvalidOperation, TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid price received for ticker: "
                f"{normalized_ticker}"
            ) from error