from datetime import date
from decimal import Decimal

import csv
import streamlit as st

from src.config import (
    TICKER_MAPPING,
    TRANSACTIONS_PATH,
)
from src.portfolio import Portfolio
from src.portfolio_history import (
    PortfolioHistory,
    PortfolioSnapshot,
)
from src.providers.yahoo_price_provider import YahooPriceProvider
from src.transaction import Transaction
from src.transaction_reader import read_transactions


@st.cache_data(ttl=300)
def load_transactions() -> list[Transaction]:
    return read_transactions(
        TRANSACTIONS_PATH
    )


@st.cache_data(ttl=300)
def load_prices(
    tickers: tuple[str, ...],
) -> dict[str, Decimal]:
    provider = YahooPriceProvider(
        TICKER_MAPPING
    )

    return {
        ticker: provider.get_price(ticker)
        for ticker in tickers
    }


@st.cache_data(ttl=3600)
def load_portfolio_history(
    transactions: list[Transaction],
) -> list[PortfolioSnapshot]:
    start_date = min(
        transaction.transaction_date
        for transaction in transactions
    )

    provider = YahooPriceProvider(
        TICKER_MAPPING
    )

    history_builder = PortfolioHistory(
        transactions=transactions,
        price_provider=provider,
    )

    return history_builder.build(
        start_date=start_date,
        end_date=date.today(),
    )


def load_portfolio() -> tuple[
    Portfolio,
    list[Transaction],
]:
    transactions = load_transactions()

    if not transactions:
        raise ValueError(
            "No transactions found."
        )

    portfolio = Portfolio(transactions)

    if not portfolio.positions():
        raise ValueError(
            "The portfolio is empty."
        )

    return portfolio, transactions


def format_currency(
    value: Decimal,
) -> str:
    amount = float(value)

    if amount < 0:
        return f"-€{abs(amount):,.2f}"

    return f"€{amount:,.2f}"


def save_transaction(
    transaction_date: date,
    transaction_type: str,
    ticker: str,
    quantity: Decimal,
    price: Decimal,
    fees: Decimal,
) -> None:
    file_exists = TRANSACTIONS_PATH.exists()

    if file_exists and TRANSACTIONS_PATH.stat().st_size > 0:
        with TRANSACTIONS_PATH.open(
            "rb+"
        ) as file:
            file.seek(-1, 2)

            if file.read(1) not in (
                b"\n",
                b"\r",
            ):
                file.write(b"\n")

    with TRANSACTIONS_PATH.open(
        "a",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(
                [
                    "date",
                    "type",
                    "ticker",
                    "quantity",
                    "price",
                    "fees",
                ]
            )

        writer.writerow(
            [
                transaction_date.isoformat(),
                transaction_type,
                ticker.upper(),
                quantity,
                price,
                fees,
            ]
        )