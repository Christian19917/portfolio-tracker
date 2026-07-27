import pandas as pd
import plotly.express as px
import streamlit as st

from src.app_services import (
    format_currency,
    load_portfolio,
    load_portfolio_history,
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📈 Portfolio Performance")

st.caption(
    "Track portfolio value, invested capital "
    "and profit/loss over time."
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

try:
    portfolio, transactions = load_portfolio()

    snapshots = load_portfolio_history(
        transactions
    )

except Exception as error:
    st.error(
        f"Unable to load portfolio history: {error}"
    )
    st.stop()


if not snapshots:
    st.info("No historical data available.")
    st.stop()


# --------------------------------------------------
# DATAFRAME
# --------------------------------------------------

history_dataframe = pd.DataFrame(
    {
        "Date": [
            snapshot.snapshot_date
            for snapshot in snapshots
        ],
        "Portfolio value": [
            float(snapshot.market_value)
            for snapshot in snapshots
        ],
        "Invested capital": [
            float(snapshot.invested_capital)
            for snapshot in snapshots
        ],
        "P/L": [
            float(snapshot.profit_loss)
            for snapshot in snapshots
        ],
    }
)


latest_snapshot = snapshots[-1]

first_snapshot = snapshots[0]

portfolio_change = (
    latest_snapshot.market_value
    - first_snapshot.market_value
)


# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------

st.markdown("### Performance summary")

value_column, invested_column, pnl_column, days_column = (
    st.columns(4)
)

value_column.metric(
    label="Current value",
    value=format_currency(
        latest_snapshot.market_value
    ),
)

invested_column.metric(
    label="Invested capital",
    value=format_currency(
        latest_snapshot.invested_capital
    ),
)

pnl_column.metric(
    label="Current P/L",
    value=format_currency(
        latest_snapshot.profit_loss
    ),
)

days_column.metric(
    label="Tracking period",
    value=f"{len(snapshots)} days",
)


# --------------------------------------------------
# PORTFOLIO VALUE
# --------------------------------------------------

st.divider()

st.subheader("Portfolio growth")

st.caption(
    "Portfolio market value compared with total "
    "invested capital."
)


performance_chart_dataframe = (
    history_dataframe.melt(
        id_vars="Date",
        value_vars=[
            "Portfolio value",
            "Invested capital",
        ],
        var_name="Series",
        value_name="Value",
    )
)


performance_figure = px.line(
    performance_chart_dataframe,
    x="Date",
    y="Value",
    color="Series",
)

performance_figure.update_traces(
    hovertemplate=(
        "<b>%{fullData.name}</b><br>"
        "Date: %{x|%d/%m/%Y}<br>"
        "Value: €%{y:,.2f}"
        "<extra></extra>"
    )
)

performance_figure.update_layout(
    height=460,
    hovermode="x unified",
    legend_title_text="",
    xaxis_title="",
    yaxis_title="Value (€)",
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=10,
    ),
)

performance_figure.update_xaxes(
    showgrid=False,
)

performance_figure.update_yaxes(
    gridcolor="rgba(128,128,128,0.15)",
)

st.plotly_chart(
    performance_figure,
    width="stretch",
    config={
        "displayModeBar": False,
    },
)


# --------------------------------------------------
# PROFIT / LOSS
# --------------------------------------------------

st.divider()

st.subheader("Profit / Loss")

st.caption(
    "Historical difference between portfolio "
    "market value and invested capital."
)


pnl_figure = px.area(
    history_dataframe,
    x="Date",
    y="P/L",
)

pnl_figure.update_traces(
    hovertemplate=(
        "Date: %{x|%d/%m/%Y}<br>"
        "P/L: €%{y:,.2f}"
        "<extra></extra>"
    )
)

pnl_figure.update_layout(
    height=330,
    xaxis_title="",
    yaxis_title="P/L (€)",
    margin=dict(
        l=10,
        r=10,
        t=20,
        b=10,
    ),
)

pnl_figure.update_xaxes(
    showgrid=False,
)

pnl_figure.update_yaxes(
    gridcolor="rgba(128,128,128,0.15)",
    zeroline=True,
    zerolinewidth=1,
)

st.plotly_chart(
    pnl_figure,
    width="stretch",
    config={
        "displayModeBar": False,
    },
)


# --------------------------------------------------
# HISTORY TABLE
# --------------------------------------------------

st.divider()

st.subheader("Historical data")

st.caption(
    "Most recent portfolio snapshots."
)


recent_history = (
    history_dataframe
    .sort_values(
        by="Date",
        ascending=False,
    )
    .head(10)
)


st.dataframe(
    recent_history,
    width="stretch",
    hide_index=True,
    column_config={
        "Date": st.column_config.DateColumn(
            "Date",
            format="DD/MM/YYYY",
        ),
        "Portfolio value": st.column_config.NumberColumn(
            "Portfolio value",
            format="€ %.2f",
        ),
        "Invested capital": st.column_config.NumberColumn(
            "Invested capital",
            format="€ %.2f",
        ),
        "P/L": st.column_config.NumberColumn(
            "P/L",
            format="€ %.2f",
        ),
    },
)