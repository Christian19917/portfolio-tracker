from decimal import Decimal, InvalidOperation
from typing import Mapping

from datetime import date, timedelta

import pandas as pd

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
    

    def get_history(self,ticker: str,start_date: date,end_date: date,) -> pd.Series:
        normalized_ticker = ticker.strip().upper()

        yahoo_ticker = self._ticker_mapping.get(
            normalized_ticker,
            normalized_ticker,
        )

        # yfinance interpreta end come data esclusiva.
        exclusive_end = end_date + timedelta(days=1)

        try:
            history = yf.download(
                yahoo_ticker,
                start=start_date.isoformat(),
                end=exclusive_end.isoformat(),
                auto_adjust=False,
                progress=False,
                threads=False,
            )
        except Exception as error:
            raise ValueError(
                f"Could not retrieve history for ticker: "
                f"{normalized_ticker}"
            ) from error

        if history.empty or "Close" not in history:
            raise ValueError(
                f"Historical prices not available for ticker: "
                f"{normalized_ticker}"
            )

        closing_prices = history["Close"].dropna()

        # Con un singolo ticker, alcune versioni di yfinance
        # restituiscono comunque un DataFrame.
        if isinstance(closing_prices, pd.DataFrame):
            closing_prices = closing_prices.iloc[:, 0]

        closing_prices.index = pd.to_datetime(
            closing_prices.index
        ).normalize()

        return closing_prices