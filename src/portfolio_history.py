from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Protocol

import pandas as pd

from src.portfolio import Portfolio
from src.transaction import Transaction


class HistoricalPriceProvider(Protocol):
    def get_history(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> pd.Series:
        ...


@dataclass(frozen=True, slots=True)
class PortfolioSnapshot:
    snapshot_date: date
    market_value: Decimal
    cash: Decimal
    total_value: Decimal
    invested_capital: Decimal
    profit_loss: Decimal


class PortfolioHistory:
    def __init__(
        self,
        transactions: list[Transaction],
        price_provider: HistoricalPriceProvider,
        initial_capital: Decimal,
    ) -> None:
        self._transactions = sorted(
            transactions,
            key=lambda transaction: transaction.transaction_date,
        )
        self._price_provider = price_provider
        self._initial_capital = initial_capital

    def build(
        self,
        start_date: date,
        end_date: date,
    ) -> list[PortfolioSnapshot]:
        if start_date > end_date:
            raise ValueError(
                "start_date cannot be after end_date"
            )

        tickers = {
            transaction.ticker
            for transaction in self._transactions
        }

        price_histories = {
            ticker: self._prepare_history(
                self._price_provider.get_history(
                    ticker,
                    start_date,
                    end_date,
                ),
                start_date,
                end_date,
            )
            for ticker in tickers
        }

        snapshots: list[PortfolioSnapshot] = []

        current_date = start_date

        while current_date <= end_date:
            completed_transactions = [
                transaction
                for transaction in self._transactions
                if transaction.transaction_date <= current_date
            ]

            portfolio = Portfolio(completed_transactions)
            positions = portfolio.positions()

            market_value = Decimal("0")

            for ticker, quantity in positions.items():
                historical_price = price_histories[ticker].get(
                    pd.Timestamp(current_date)
                )

                if pd.isna(historical_price):
                    continue

                market_value += (
                    quantity
                    * Decimal(str(historical_price))
                )

            cash = self._calculate_cash(
                completed_transactions
            )

            total_value = market_value + cash
            profit_loss = total_value - self._initial_capital

            snapshots.append(
                PortfolioSnapshot(
                    snapshot_date=current_date,
                    market_value=market_value,
                    cash=cash,
                    total_value=total_value,
                    invested_capital=self._initial_capital,
                    profit_loss=profit_loss,
                )
            )

            current_date += timedelta(days=1)

        return snapshots

    def _calculate_cash(
        self,
        transactions: list[Transaction],
    ) -> Decimal:
        cash = self._initial_capital

        for transaction in transactions:
            gross_value = (
                transaction.quantity
                * transaction.price
            )

            if transaction.transaction_type == "BUY":
                cash -= gross_value + transaction.fees

            elif transaction.transaction_type == "SELL":
                cash += gross_value - transaction.fees

        return cash

    @staticmethod
    def _prepare_history(
        history: pd.Series,
        start_date: date,
        end_date: date,
    ) -> pd.Series:
        calendar = pd.date_range(
            start=start_date,
            end=end_date,
            freq="D",
        )

        normalized_history = history.copy()
        normalized_history.index = pd.to_datetime(
            normalized_history.index
        ).normalize()

        return normalized_history.reindex(
            calendar
        ).ffill()