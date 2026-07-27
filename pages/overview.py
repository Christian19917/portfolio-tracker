from decimal import Decimal

import pandas as pd
import plotly.express as px
import streamlit as st

from src.app_services import (
    format_currency,
    load_portfolio,
    load_prices,
)
from src.asset_allocation import calculate_allocation
from src.asset_metadata import ASSET_METADATA
from src.portfolio import Portfolio
from src.portfolio_analytics import (
    calculate_market_values,
    calculate_total_invested_capital,
    calculate_total_market_value,
    calculate_total_return_percentage,
    calculate_total_unrealized_pnl,
    calculate_unrealized_pnl,
)


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

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

        metadata = ASSET_METADATA.get(ticker)

        rows.append(
            {
                "Ticker": ticker,
                "Name": (
                    metadata.name
                    if metadata
                    else ticker
                ),
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


def build_recent_transactions_dataframe(
    transactions,
) -> pd.DataFrame:
    recent_transactions = sorted(
        transactions,
        key=lambda transaction: transaction.transaction_date,
        reverse=True,
    )[:5]

    return pd.DataFrame(
        [
            {
                "Date": transaction.transaction_date,
                "Type": transaction.transaction_type,
                "Ticker": transaction.ticker,
                "Quantity": float(transaction.quantity),
                "Price": float(transaction.price),
                "Fees": float(transaction.fees),
            }
            for transaction in recent_transactions
        ]
    )


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "portfolio_goal" not in st.session_state:
    st.session_state.portfolio_goal = None


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📊 Portfolio Overview")

st.caption(
    "Your portfolio at a glance — value, performance, "
    "allocation and recent activity."
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:
    portfolio, transactions = load_portfolio()

    positions = portfolio.positions()

    current_prices = load_prices(
        tuple(positions.keys())
    )

except Exception as error:
    st.error(
        f"Unable to load portfolio: {error}"
    )
    st.stop()


# --------------------------------------------------
# CALCULATIONS
# --------------------------------------------------

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

ticker_allocation = calculate_allocation(
    market_values
)

positions_dataframe = build_positions_dataframe(
    portfolio,
    current_prices,
)


# --------------------------------------------------
# PORTFOLIO SUMMARY
# --------------------------------------------------

st.markdown("### Portfolio summary")

value_column, invested_column, pnl_column, return_column = (
    st.columns(4)
)

value_column.metric(
    label="Portfolio value",
    value=format_currency(
        total_market_value
    ),
    delta=(
        f"{float(total_unrealized_pnl):+,.2f} €"
    ),
    delta_color="normal",
)

invested_column.metric(
    label="Invested capital",
    value=format_currency(
        total_invested_capital
    ),
)

pnl_column.metric(
    label="Unrealized P/L",
    value=format_currency(
        total_unrealized_pnl
    ),
    delta=(
        f"{float(total_return_percentage):+.2f}%"
    ),
    delta_color="normal",
)

return_column.metric(
    label="Total return",
    value=(
        f"{float(total_return_percentage):+.2f}%"
    ),
)


# --------------------------------------------------
# GOAL TRACKER
# --------------------------------------------------

st.divider()

st.subheader("🎯 Portfolio goal")

goal_input_column, goal_display_column = st.columns(
    [1, 2],
    gap="large",
)


with goal_input_column:

    with st.container(border=True):

        st.markdown("#### Set your target")

        st.caption(
            "Choose the portfolio value you want "
            "to reach."
        )

        goal_input = st.number_input(
            "Target value (€)",
            min_value=0.0,
            step=1000.0,
            value=0.0,
            format="%.2f",
        )

        if st.button(
            "Set goal",
            type="primary",
            width="stretch",
        ):
            if goal_input <= 0:
                st.warning(
                    "Enter a target greater than zero."
                )

            elif Decimal(
                str(goal_input)
            ) <= total_market_value:
                st.warning(
                    "Your goal should be greater than "
                    "the current portfolio value."
                )

            else:
                st.session_state.portfolio_goal = (
                    float(goal_input)
                )

                st.rerun()


with goal_display_column:

    with st.container(border=True):

        if st.session_state.portfolio_goal is None:

            st.markdown("#### No goal set")

            st.info(
                "Set a target value to activate "
                "your portfolio goal tracker."
            )

            st.markdown(
                """
                Once activated, this section will show:

                **Progress toward your goal**

                **Amount still required**

                **Percentage completed**
                """
            )

        else:

            portfolio_goal = Decimal(
                str(
                    st.session_state.portfolio_goal
                )
            )

            goal_progress = (
                total_market_value
                / portfolio_goal
            )

            goal_percentage = (
                goal_progress
                * Decimal("100")
            )

            remaining_to_goal = max(
                portfolio_goal
                - total_market_value,
                Decimal("0"),
            )

            st.markdown("#### Goal progress")

            target_column, remaining_column = (
                st.columns(2)
            )

            target_column.metric(
                label="Target",
                value=format_currency(
                    portfolio_goal
                ),
            )

            remaining_column.metric(
                label="Remaining",
                value=format_currency(
                    remaining_to_goal
                ),
            )

            st.progress(
                min(
                    float(goal_progress),
                    1.0,
                )
            )

            st.markdown(
                f"### {float(goal_percentage):.1f}%"
            )

            st.caption(
                f"{format_currency(total_market_value)} "
                f"of "
                f"{format_currency(portfolio_goal)}"
            )

            if st.button(
                "Reset goal",
                width="stretch",
            ):
                st.session_state.portfolio_goal = None
                st.rerun()


# --------------------------------------------------
# PORTFOLIO SNAPSHOT
# --------------------------------------------------

st.divider()

st.subheader("Portfolio snapshot")

st.caption(
    "Current portfolio composition and "
    "largest positions."
)

allocation_column, positions_column = st.columns(
    [1, 1.7],
    gap="large",
)


# --------------------------------------------------
# DONUT
# --------------------------------------------------

with allocation_column:

    with st.container(border=True):

        st.markdown("#### Allocation")

        allocation_dataframe = pd.DataFrame(
            {
                "Ticker": ticker_allocation.keys(),
                "Allocation": [
                    float(value)
                    for value
                    in ticker_allocation.values()
                ],
            }
        )

        allocation_figure = px.pie(
            allocation_dataframe,
            names="Ticker",
            values="Allocation",
            hole=0.60,
        )

        allocation_figure.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Allocation: %{value:.2f}%"
                "<extra></extra>"
            ),
        )

        allocation_figure.update_layout(
            showlegend=False,
            height=350,
            margin=dict(
                l=5,
                r=5,
                t=10,
                b=5,
            ),
        )

        st.plotly_chart(
            allocation_figure,
            width="stretch",
            config={
                "displayModeBar": False,
            },
        )


# --------------------------------------------------
# LARGEST POSITIONS
# --------------------------------------------------

with positions_column:

    with st.container(border=True):

        st.markdown("#### Largest positions")

        largest_positions = (
            positions_dataframe
            .sort_values(
                by="Market value",
                ascending=False,
            )
            .head(5)
        )

        st.dataframe(
            largest_positions[
                [
                    "Ticker",
                    "Name",
                    "Market value",
                    "P/L",
                    "P/L %",
                ]
            ],
            width="stretch",
            hide_index=True,
            height=290,
            column_config={
                "Ticker": (
                    st.column_config.TextColumn(
                        "Ticker",
                        width="small",
                    )
                ),
                "Name": (
                    st.column_config.TextColumn(
                        "Asset",
                        width="large",
                    )
                ),
                "Market value": (
                    st.column_config.NumberColumn(
                        "Value",
                        format="€ %.2f",
                    )
                ),
                "P/L": (
                    st.column_config.NumberColumn(
                        "P/L",
                        format="€ %.2f",
                    )
                ),
                "P/L %": (
                    st.column_config.NumberColumn(
                        "Return",
                        format="%.2f %%",
                    )
                ),
            },
        )

        if not largest_positions.empty:

            largest_position = (
                largest_positions.iloc[0]
            )

            portfolio_weight = (
                largest_position["Market value"]
                / float(total_market_value)
                * 100
            )

            st.caption(
                f"Largest holding: "
                f"{largest_position['Ticker']} · "
                f"{portfolio_weight:.1f}% "
                f"of portfolio"
            )


# --------------------------------------------------
# CURRENT POSITIONS
# --------------------------------------------------

st.divider()

st.subheader("Current positions")

st.caption(
    "Current value, cost basis and unrealized "
    "performance for every holding."
)


st.dataframe(
    positions_dataframe,
    width="stretch",
    hide_index=True,
    column_config={
        "Ticker": st.column_config.TextColumn(
            "Ticker",
            width="small",
        ),
        "Name": st.column_config.TextColumn(
            "Asset",
            width="large",
        ),
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
        "Invested capital": (
            st.column_config.NumberColumn(
                "Invested",
                format="€ %.2f",
            )
        ),
        "Market value": (
            st.column_config.NumberColumn(
                "Market value",
                format="€ %.2f",
            )
        ),
        "P/L": st.column_config.NumberColumn(
            "P/L",
            format="€ %.2f",
        ),
        "P/L %": st.column_config.NumberColumn(
            "Return",
            format="%.2f %%",
        ),
    },
)


# --------------------------------------------------
# RECENT TRANSACTIONS
# --------------------------------------------------

st.divider()

title_column, counter_column = st.columns(
    [3, 1]
)

with title_column:
    st.subheader("Recent transactions")

with counter_column:
    st.caption(
        f"{len(transactions)} total transactions"
    )


recent_transactions_dataframe = (
    build_recent_transactions_dataframe(
        transactions
    )
)


st.dataframe(
    recent_transactions_dataframe,
    width="stretch",
    hide_index=True,
    column_config={
        "Date": st.column_config.DateColumn(
            "Date",
            format="DD/MM/YYYY",
        ),
        "Type": st.column_config.TextColumn(
            "Type",
            width="small",
        ),
        "Ticker": st.column_config.TextColumn(
            "Ticker",
            width="small",
        ),
        "Quantity": (
            st.column_config.NumberColumn(
                "Quantity",
                format="%.4f",
            )
        ),
        "Price": st.column_config.NumberColumn(
            "Price",
            format="€ %.2f",
        ),
        "Fees": st.column_config.NumberColumn(
            "Fees",
            format="€ %.2f",
        ),
    },
)