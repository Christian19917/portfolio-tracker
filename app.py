from decimal import Decimal
from pathlib import Path

import pandas as pd
import streamlit as st

from src.portfolio import Portfolio
from src.providers.yahoo_price_provider import YahooPriceProvider
from src.transaction_reader import read_transactions

from src.portfolio_analytics import (
    calculate_market_values,
    calculate_total_invested_capital,
    calculate_total_market_value,
    calculate_total_return_percentage,
    calculate_total_unrealized_pnl,
    calculate_unrealized_pnl,
)

TRANSACTIONS_PATH = Path("data/transactions.csv")

TICKER_MAPPING = {
    "MTD": "MTD.PA",
    "ALLW": "ALLW.DE",
    "VWCE": "VWCE.DE",
    "XEON": "XEON.DE",
}


@st.cache_data(ttl=300)
def load_transactions():
    return read_transactions(TRANSACTIONS_PATH)


@st.cache_data(ttl=300)
def load_prices(
    tickers: tuple[str, ...],
) -> dict[str, Decimal]:
    provider = YahooPriceProvider(TICKER_MAPPING)

    return {
        ticker: provider.get_price(ticker)
        for ticker in tickers
    }


def format_currency(value: Decimal) -> str:
    return f"€{float(value):,.2f}"


def load_portfolio() -> Portfolio:
    transactions = load_transactions()

    if not transactions:
        raise ValueError("No transactions found.")

    portfolio = Portfolio(transactions)

    if not portfolio.positions():
        raise ValueError("The portfolio is empty.")

    return portfolio


def build_positions_dataframe(
    portfolio: Portfolio,
    current_prices: dict[str, Decimal],
) -> pd.DataFrame:
    positions = portfolio.positions()
    average_costs = portfolio.average_costs()

    rows = []

    for ticker, quantity in positions.items():
        average_cost = average_costs[ticker]
        current_price = current_prices[ticker]

        invested_capital = average_cost * quantity
        market_value = current_price * quantity
        pnl = market_value - invested_capital

        pnl_percentage = (
            pnl / invested_capital * Decimal("100")
            if invested_capital != Decimal("0")
            else Decimal("0")
        )

        rows.append(
            {
                "Ticker": ticker,
                "Quantity": float(quantity),
                "Average cost": float(average_cost),
                "Current price": float(current_price),
                "Invested capital": float(invested_capital),
                "Market value": float(market_value),
                "P/L": float(pnl),
                "P/L %": float(pnl_percentage),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    st.set_page_config(
        page_title="Portfolio Tracker",
        page_icon="📈",
        layout="wide",
    )

    st.title("📈 Portfolio Tracker")
    st.caption("Portfolio overview and investment performance")

    try:
        portfolio = load_portfolio()

        positions = portfolio.positions()
        average_costs = portfolio.average_costs()

        current_prices = load_prices(
            tuple(positions.keys())
        )

    except FileNotFoundError:
        st.error(
            f"Transaction file not found: {TRANSACTIONS_PATH}"
        )
        st.stop()

    except ValueError as error:
        st.warning(str(error))
        st.stop()

    except Exception as error:
        st.error(f"Unable to load portfolio: {error}")
        st.stop()

    market_values = calculate_market_values(
        portfolio,
        current_prices,
    )

    unrealized_pnl = calculate_unrealized_pnl(
        portfolio,
        current_prices,
    )

    total_market_value = calculate_total_market_value(
        market_values
    )

    total_unrealized_pnl = calculate_total_unrealized_pnl(
        unrealized_pnl
    )

    total_invested_capital = calculate_total_invested_capital(
        portfolio
    )

    total_return_percentage = calculate_total_return_percentage(
        total_unrealized_pnl,
        total_invested_capital,
    )

    value_column, pnl_column, return_column = st.columns(3)

    value_column.metric(
        label="Portfolio value",
        value=format_currency(total_market_value),
    )

    pnl_column.metric(
        label="Unrealized P/L",
        value=format_currency(total_unrealized_pnl),
    )

    return_column.metric(
        label="Return",
        value=f"{float(total_return_percentage):.2f}%",
    )

    st.divider()

    st.subheader("Positions")

    positions_dataframe = build_positions_dataframe(
        portfolio,
        current_prices,
    )

    st.dataframe(
        positions_dataframe,
        width="stretch",
        hide_index=True,
        column_config={
            "Quantity": st.column_config.NumberColumn(
                "Quantity",
                format="%.4f",
            ),
            "Average cost": st.column_config.NumberColumn(
                "Average cost",
                format="€ %.2f",
            ),
            "Current price": st.column_config.NumberColumn(
                "Current price",
                format="€ %.2f",
            ),
            "Invested capital": st.column_config.NumberColumn(
                "Invested capital",
                format="€ %.2f",
            ),
            "Market value": st.column_config.NumberColumn(
                "Market value",
                format="€ %.2f",
            ),
            "P/L": st.column_config.NumberColumn(
                "P/L",
                format="€ %.2f",
            ),
            "P/L %": st.column_config.NumberColumn(
                "P/L %",
                format="%.2f %%",
            ),
        },
    )


if __name__ == "__main__":
    main()