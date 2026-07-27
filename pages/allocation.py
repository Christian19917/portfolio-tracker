import pandas as pd
import plotly.express as px
import streamlit as st

from src.app_services import (
    format_currency,
    load_portfolio,
    load_prices,
)
from src.asset_allocation import (
    allocation_by_asset_class,
    calculate_allocation,
)
from src.asset_metadata import ASSET_METADATA
from src.portfolio_analytics import (
    calculate_market_values,
    calculate_total_market_value,
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🥧 Portfolio Allocation")

st.caption(
    "Understand how your portfolio is distributed "
    "across investments and asset classes."
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:
    portfolio, _ = load_portfolio()

    positions = portfolio.positions()

    current_prices = load_prices(
        tuple(positions.keys())
    )

except Exception as error:
    st.error(
        f"Unable to load portfolio allocation: {error}"
    )
    st.stop()


# --------------------------------------------------
# CALCULATIONS
# --------------------------------------------------

market_values = calculate_market_values(
    portfolio,
    current_prices,
)

total_market_value = calculate_total_market_value(
    market_values
)

ticker_allocation = calculate_allocation(
    market_values
)

asset_class_allocation = allocation_by_asset_class(
    market_values,
    ASSET_METADATA,
)


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

largest_ticker = max(
    ticker_allocation,
    key=ticker_allocation.get,
)

largest_weight = ticker_allocation[
    largest_ticker
]

asset_classes_count = len(
    asset_class_allocation
)


st.markdown("### Allocation summary")

value_column, holdings_column, classes_column, largest_column = (
    st.columns(4)
)

value_column.metric(
    label="Portfolio value",
    value=format_currency(
        total_market_value
    ),
)

holdings_column.metric(
    label="Holdings",
    value=str(len(market_values)),
)

classes_column.metric(
    label="Asset classes",
    value=str(asset_classes_count),
)

largest_column.metric(
    label="Largest position",
    value=largest_ticker,
    delta=(
        f"{float(largest_weight):.1f}%"
    ),
)


# --------------------------------------------------
# DATAFRAMES
# --------------------------------------------------

ticker_dataframe = pd.DataFrame(
    [
        {
            "Ticker": ticker,
            "Name": (
                ASSET_METADATA[ticker].name
                if ticker in ASSET_METADATA
                else ticker
            ),
            "Market value": float(
                market_values[ticker]
            ),
            "Allocation": float(
                ticker_allocation[ticker]
            ),
        }
        for ticker in ticker_allocation
    ]
)


ticker_dataframe = (
    ticker_dataframe.sort_values(
        by="Allocation",
        ascending=False,
    )
)


asset_class_dataframe = pd.DataFrame(
    [
        {
            "Asset class": asset_class,
            "Allocation": float(
                allocation
            ),
        }
        for asset_class, allocation
        in asset_class_allocation.items()
    ]
)


asset_class_dataframe = (
    asset_class_dataframe.sort_values(
        by="Allocation",
        ascending=False,
    )
)


# --------------------------------------------------
# DONUT CHARTS
# --------------------------------------------------

st.divider()

st.subheader("Portfolio composition")

allocation_column, asset_class_column = st.columns(
    2,
    gap="large",
)


with allocation_column:
    st.markdown("#### By ETF")

    ticker_figure = px.pie(
        ticker_dataframe,
        names="Ticker",
        values="Allocation",
        hole=0.58,
        custom_data=[
            "Name",
            "Market value",
        ],
    )

    ticker_figure.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "%{customdata[0]}<br><br>"
            "Allocation: %{value:.2f}%<br>"
            "Market value: €%{customdata[1]:,.2f}"
            "<extra></extra>"
        ),
    )

    ticker_figure.update_layout(
        showlegend=False,
        height=430,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
    )

    st.plotly_chart(
        ticker_figure,
        width="stretch",
        config={
            "displayModeBar": False,
        },
    )


with asset_class_column:
    st.markdown("#### By asset class")

    asset_class_figure = px.pie(
        asset_class_dataframe,
        names="Asset class",
        values="Allocation",
        hole=0.58,
    )

    asset_class_figure.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Allocation: %{value:.2f}%"
            "<extra></extra>"
        ),
    )

    asset_class_figure.update_layout(
        showlegend=False,
        height=430,
        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),
    )

    st.plotly_chart(
        asset_class_figure,
        width="stretch",
        config={
            "displayModeBar": False,
        },
    )


# --------------------------------------------------
# HOLDINGS BREAKDOWN
# --------------------------------------------------

st.divider()

st.subheader("Holdings breakdown")

st.caption(
    "Current portfolio weight and market value "
    "for each investment."
)


st.dataframe(
    ticker_dataframe,
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
        "Market value": st.column_config.NumberColumn(
            "Market value",
            format="€ %.2f",
        ),
        "Allocation": st.column_config.ProgressColumn(
            "Allocation",
            format="%.2f%%",
            min_value=0,
            max_value=100,
        ),
    },
)


# --------------------------------------------------
# ASSET CLASS BREAKDOWN
# --------------------------------------------------

st.divider()

st.subheader("Asset class breakdown")


st.dataframe(
    asset_class_dataframe,
    width="stretch",
    hide_index=True,
    column_config={
        "Asset class": st.column_config.TextColumn(
            "Asset class",
        ),
        "Allocation": st.column_config.ProgressColumn(
            "Allocation",
            format="%.2f%%",
            min_value=0,
            max_value=100,
        ),
    },
)