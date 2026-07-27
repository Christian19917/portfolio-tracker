from decimal import Decimal

import pandas as pd
import plotly.express as px
import streamlit as st

from src.app_services import (
    format_currency,
    load_transactions,
    save_transaction,
)
from src.asset_metadata import ASSET_METADATA


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("💳 Transactions")

st.caption(
    "Manage purchases, sales and portfolio activity."
)


# --------------------------------------------------
# LOAD TRANSACTIONS
# --------------------------------------------------

try:
    transactions = load_transactions()

except Exception as error:
    st.error(
        f"Unable to load transactions: {error}"
    )
    st.stop()


# --------------------------------------------------
# SUMMARY CALCULATIONS
# --------------------------------------------------

total_transactions = len(transactions)

buy_transactions = [
    transaction
    for transaction in transactions
    if transaction.transaction_type == "BUY"
]

sell_transactions = [
    transaction
    for transaction in transactions
    if transaction.transaction_type == "SELL"
]

total_fees = sum(
    (
        transaction.fees
        for transaction in transactions
    ),
    Decimal("0"),
)

total_buy_value = sum(
    (
        transaction.quantity * transaction.price
        for transaction in buy_transactions
    ),
    Decimal("0"),
)

total_sell_value = sum(
    (
        transaction.quantity * transaction.price
        for transaction in sell_transactions
    ),
    Decimal("0"),
)

total_traded_value = (
    total_buy_value
    + total_sell_value
)

fees_percentage = (
    total_fees
    / total_traded_value
    * Decimal("100")
    if total_traded_value != Decimal("0")
    else Decimal("0")
)


# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------

st.markdown("### Activity summary")

transactions_column, buys_column, sells_column = st.columns(3)

transactions_column.metric(
    label="Transactions",
    value=str(total_transactions),
)

buys_column.metric(
    label="Buy orders",
    value=str(len(buy_transactions)),
)

sells_column.metric(
    label="Sell orders",
    value=str(len(sell_transactions)),
)


# --------------------------------------------------
# FEES HIGHLIGHT
# --------------------------------------------------

st.markdown("### 💸 Trading costs")

fees_column, fee_rate_column, traded_value_column = st.columns(3)

fees_column.metric(
    label="Total fees paid",
    value=format_currency(total_fees),
)

fee_rate_column.metric(
    label="Fees / traded value",
    value=f"{float(fees_percentage):.3f}%",
)

traded_value_column.metric(
    label="Total traded value",
    value=format_currency(total_traded_value),
)

st.caption(
    "Fees are cumulative transaction costs paid across "
    "all recorded purchases and sales."
)


# --------------------------------------------------
# ADD TRANSACTION
# --------------------------------------------------

st.divider()

with st.expander(
    "➕ Add transaction",
    expanded=False,
):

    st.caption(
        "Record a new purchase or sale. "
        "The portfolio will refresh automatically."
    )

    with st.form(
        "add_transaction_form",
        clear_on_submit=True,
    ):

        first_column, second_column = st.columns(2)

        with first_column:

            transaction_date = st.date_input(
                "Date"
            )

            transaction_type = st.selectbox(
                "Transaction type",
                options=[
                    "BUY",
                    "SELL",
                ],
            )

            ticker = st.selectbox(
                "Ticker",
                options=sorted(
                    ASSET_METADATA.keys()
                ),
            )

        with second_column:

            quantity = st.number_input(
                "Quantity",
                min_value=0.0,
                step=0.01,
                format="%.4f",
            )

            price = st.number_input(
                "Price per unit",
                min_value=0.0,
                step=0.01,
                format="%.2f",
            )

            fees = st.number_input(
                "Fees",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                help="Broker commissions and transaction costs.",
            )

        submitted = st.form_submit_button(
            "Save transaction",
            type="primary",
            width="stretch",
        )

    if submitted:

        if quantity <= 0:
            st.error(
                "Quantity must be greater than zero."
            )

        elif price <= 0:
            st.error(
                "Price must be greater than zero."
            )

        else:

            try:
                save_transaction(
                    transaction_date=transaction_date,
                    transaction_type=transaction_type,
                    ticker=ticker,
                    quantity=Decimal(
                        str(quantity)
                    ),
                    price=Decimal(
                        str(price)
                    ),
                    fees=Decimal(
                        str(fees)
                    ),
                )

                st.cache_data.clear()

                st.success(
                    "Transaction saved successfully."
                )

                st.rerun()

            except Exception as error:
                st.error(
                    f"Unable to save transaction: {error}"
                )


# --------------------------------------------------
# EMPTY STATE
# --------------------------------------------------

if not transactions:

    st.divider()

    st.info(
        "No transactions found. "
        "Add your first transaction above."
    )

    st.stop()


# --------------------------------------------------
# TRANSACTIONS DATAFRAME
# --------------------------------------------------

transactions_dataframe = pd.DataFrame(
    [
        {
            "Date": transaction.transaction_date,
            "Type": transaction.transaction_type,
            "Ticker": transaction.ticker,
            "Asset": (
                ASSET_METADATA[
                    transaction.ticker
                ].name
                if transaction.ticker in ASSET_METADATA
                else transaction.ticker
            ),
            "Quantity": float(
                transaction.quantity
            ),
            "Price": float(
                transaction.price
            ),
            "Gross value": float(
                transaction.quantity
                * transaction.price
            ),
            "Fees": float(
                transaction.fees
            ),
            "Net cash": float(
                (
                    transaction.quantity
                    * transaction.price
                    + transaction.fees
                )
                if transaction.transaction_type == "BUY"
                else (
                    transaction.quantity
                    * transaction.price
                    - transaction.fees
                )
            ),
        }
        for transaction in transactions
    ]
)

transactions_dataframe = (
    transactions_dataframe.sort_values(
        by="Date",
        ascending=False,
    )
)


# --------------------------------------------------
# TRANSACTION ACTIVITY
# --------------------------------------------------

st.divider()

st.subheader("Transaction activity")

activity_dataframe = (
    transactions_dataframe
    .groupby(
        "Type",
        as_index=False,
    )
    .agg(
        Transactions=("Type", "size"),
        Value=("Gross value", "sum"),
    )
)


activity_column, values_column = st.columns(
    [1, 1.5],
    gap="large",
)


with activity_column:

    activity_figure = px.pie(
        activity_dataframe,
        names="Type",
        values="Transactions",
        hole=0.58,
    )

    activity_figure.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Transactions: %{value}"
            "<extra></extra>"
        ),
    )

    activity_figure.update_layout(
        showlegend=False,
        height=330,
        margin=dict(
            l=10,
            r=10,
            t=10,
            b=10,
        ),
    )

    st.plotly_chart(
        activity_figure,
        width="stretch",
        config={
            "displayModeBar": False,
        },
    )


with values_column:

    st.markdown("#### Cash activity")

    purchase_column, sales_column = st.columns(2)

    purchase_column.metric(
        label="Purchases",
        value=format_currency(
            total_buy_value
        ),
    )

    sales_column.metric(
        label="Sales",
        value=format_currency(
            total_sell_value
        ),
    )

    st.markdown("#### 💸 Transaction costs")

    fee_total_column, fee_ratio_column = st.columns(2)

    fee_total_column.metric(
        label="Fees paid",
        value=format_currency(
            total_fees
        ),
    )

    fee_ratio_column.metric(
        label="Cost ratio",
        value=f"{float(fees_percentage):.3f}%",
    )

    if transactions:

        latest_transaction = max(
            transactions,
            key=lambda transaction:
                transaction.transaction_date,
        )

        st.caption(
            "Latest transaction: "
            f"{latest_transaction.transaction_type} "
            f"{latest_transaction.ticker} on "
            f"{latest_transaction.transaction_date.strftime('%d/%m/%Y')}"
        )


# --------------------------------------------------
# FEES BREAKDOWN
# --------------------------------------------------

st.divider()

st.subheader("💸 Fees breakdown")

st.caption(
    "Transaction costs paid for each operation."
)


fees_dataframe = (
    transactions_dataframe[
        [
            "Date",
            "Ticker",
            "Type",
            "Gross value",
            "Fees",
        ]
    ]
    .sort_values(
        by="Fees",
        ascending=False,
    )
)


st.dataframe(
    fees_dataframe,
    width="stretch",
    hide_index=True,
    column_config={
        "Date": st.column_config.DateColumn(
            "Date",
            format="DD/MM/YYYY",
        ),
        "Ticker": st.column_config.TextColumn(
            "Ticker",
            width="small",
        ),
        "Type": st.column_config.TextColumn(
            "Type",
            width="small",
        ),
        "Gross value": st.column_config.NumberColumn(
            "Transaction value",
            format="€ %.2f",
        ),
        "Fees": st.column_config.NumberColumn(
            "💸 Fees",
            format="€ %.2f",
        ),
    },
)


# --------------------------------------------------
# TRANSACTION HISTORY
# --------------------------------------------------

st.divider()

st.subheader("Transaction history")

st.caption(
    "Complete portfolio transaction history, "
    "from the most recent operation."
)


st.dataframe(
    transactions_dataframe,
    width="stretch",
    hide_index=True,
    column_config={
        "Date": st.column_config.DateColumn(
            "Date",
            format="DD/MM/YYYY",
            width="small",
        ),
        "Type": st.column_config.TextColumn(
            "Type",
            width="small",
        ),
        "Ticker": st.column_config.TextColumn(
            "Ticker",
            width="small",
        ),
        "Asset": st.column_config.TextColumn(
            "Asset",
            width="large",
        ),
        "Quantity": st.column_config.NumberColumn(
            "Quantity",
            format="%.4f",
        ),
        "Price": st.column_config.NumberColumn(
            "Price",
            format="€ %.2f",
        ),
        "Gross value": st.column_config.NumberColumn(
            "Gross value",
            format="€ %.2f",
        ),
        "Fees": st.column_config.NumberColumn(
            "💸 Fees",
            format="€ %.2f",
        ),
        "Net cash": st.column_config.NumberColumn(
            "Net cash",
            format="€ %.2f",
        ),
    },
)