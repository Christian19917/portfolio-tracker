from datetime import date
from decimal import Decimal

import pytest

from src.portfolio import Portfolio
from src.transaction import Transaction
from src.providers.dictionary_price_provider import (DictionaryPriceProvider)

def make_transaction(
    transaction_type: str,
    ticker: str = "VWCE",
    quantity: str = "1",
    price: str = "100.00",
    fees: str = "0.00",
    transaction_date: date = date(2026, 1, 1),
) -> Transaction:
    """Create a valid transaction with convenient default values."""
    return Transaction(
        transaction_date=transaction_date,
        transaction_type=transaction_type,
        ticker=ticker,
        quantity=Decimal(quantity),
        price=Decimal(price),
        fees=Decimal(fees),
    )


def test_empty_portfolio_has_no_positions() -> None:
    portfolio = Portfolio([])

    assert portfolio.positions() == {}


def test_single_buy_creates_position() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", quantity="2"),
    ])

    assert portfolio.positions() == {
        "VWCE": Decimal("2"),
    }


def test_multiple_buys_of_same_asset_are_aggregated() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", quantity="2"),
        make_transaction("BUY", quantity="3"),
        make_transaction("BUY", quantity="0.5"),
    ])

    assert portfolio.positions() == {
        "VWCE": Decimal("5.5"),
    }


def test_buy_and_partial_sell_calculate_remaining_position() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", quantity="10"),
        make_transaction("BUY", quantity="5"),
        make_transaction("SELL", quantity="8"),
    ])

    assert portfolio.positions() == {
        "VWCE": Decimal("7"),
    }


def test_different_assets_are_kept_separate() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", ticker="VWCE", quantity="7"),
        make_transaction("BUY", ticker="XEON", quantity="4"),
        make_transaction("BUY", ticker="SGLD", quantity="2"),
    ])

    assert portfolio.positions() == {
        "VWCE": Decimal("7"),
        "XEON": Decimal("4"),
        "SGLD": Decimal("2"),
    }


def test_transactions_are_processed_independently_by_ticker() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", ticker="VWCE", quantity="10"),
        make_transaction("BUY", ticker="XEON", quantity="5"),
        make_transaction("SELL", ticker="VWCE", quantity="3"),
        make_transaction("BUY", ticker="XEON", quantity="2"),
    ])

    assert portfolio.positions() == {
        "VWCE": Decimal("7"),
        "XEON": Decimal("7"),
    }


def test_fractional_quantities_are_supported() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", quantity="0.25"),
        make_transaction("BUY", quantity="0.50"),
        make_transaction("SELL", quantity="0.10"),
    ])

    assert portfolio.positions() == {
        "VWCE": Decimal("0.65"),
    }


def test_fully_sold_position_is_removed() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", quantity="10"),
        make_transaction("SELL", quantity="10"),
    ])

    assert portfolio.positions() == {}


def test_fully_sold_asset_does_not_remove_other_positions() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", ticker="VWCE", quantity="10"),
        make_transaction("BUY", ticker="XEON", quantity="4"),
        make_transaction("SELL", ticker="VWCE", quantity="10"),
    ])

    assert portfolio.positions() == {
        "XEON": Decimal("4"),
    }


def test_sell_more_than_available_raises_value_error() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", quantity="5"),
        make_transaction("SELL", quantity="8"),
    ])

    with pytest.raises(
        ValueError,
        match="Cannot sell more VWCE than currently owned",
    ):
        portfolio.positions()


def test_sell_without_previous_purchase_raises_value_error() -> None:
    portfolio = Portfolio([
        make_transaction("SELL", quantity="1"),
    ])

    with pytest.raises(
        ValueError,
        match="Cannot sell more VWCE than currently owned",
    ):
        portfolio.positions()


def test_overselling_one_asset_raises_error_even_when_another_is_available() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", ticker="VWCE", quantity="10"),
        make_transaction("BUY", ticker="XEON", quantity="2"),
        make_transaction("SELL", ticker="XEON", quantity="3"),
    ])

    with pytest.raises(
        ValueError,
        match="Cannot sell more XEON than currently owned",
    ):
        portfolio.positions()


@pytest.mark.parametrize(
    "invalid_type",
    [
        "DIVIDEND",
        "TRANSFER",
        "HELLO",
        "",
    ],
)
def test_unknown_transaction_type_raises_value_error(
    invalid_type: str,
) -> None:
    portfolio = Portfolio([
        make_transaction(invalid_type, quantity="1"),
    ])

    with pytest.raises(
        ValueError,
        match=f"Unsupported transaction type: {invalid_type}",
    ):
        portfolio.positions()


def test_input_transaction_list_is_copied_on_creation() -> None:
    transactions = [
        make_transaction("BUY", quantity="2"),
    ]

    portfolio = Portfolio(transactions)

    transactions.append(
        make_transaction("BUY", quantity="100"),
    )

    assert portfolio.positions() == {
        "VWCE": Decimal("2"),
    }


def test_transactions_property_returns_immutable_tuple() -> None:
    transaction = make_transaction("BUY", quantity="2")
    portfolio = Portfolio([transaction])

    assert portfolio.transactions == (transaction,)
    assert isinstance(portfolio.transactions, tuple)


def test_positions_returns_a_new_dictionary_each_time() -> None:
    portfolio = Portfolio([
        make_transaction("BUY", quantity="2"),
    ])

    first_result = portfolio.positions()
    first_result["VWCE"] = Decimal("999")

    second_result = portfolio.positions()

    assert second_result == {
        "VWCE": Decimal("2"),
    }


def test_market_values_calculate_value_for_each_position() -> None:
    portfolio = Portfolio([
        make_transaction(
            "BUY",
            ticker="VWCE",
            quantity="7",
        ),
        make_transaction(
            "BUY",
            ticker="XEON",
            quantity="4",
        ),
    ])

    price_provider = DictionaryPriceProvider({
        "VWCE": Decimal("145.32"),
        "XEON": Decimal("143.58"),
    })

    assert portfolio.market_values(price_provider) == {
        "VWCE": Decimal("1017.24"),
        "XEON": Decimal("574.32"),
    }


def test_market_values_of_empty_portfolio_are_empty() -> None:
    portfolio = Portfolio([])
    price_provider = DictionaryPriceProvider({})

    assert portfolio.market_values(price_provider) == {}


def test_market_values_fail_when_price_is_missing() -> None:
    portfolio = Portfolio([
        make_transaction(
            "BUY",
            ticker="VWCE",
            quantity="2",
        ),
    ])

    price_provider = DictionaryPriceProvider({})

    with pytest.raises(
        ValueError,
        match="Price not available for ticker: VWCE",
    ):
        portfolio.market_values(price_provider)

    
def test_average_cost_of_single_purchase_includes_fees() -> None:
    portfolio = Portfolio([
        make_transaction(
            "BUY",
            ticker="VWCE",
            quantity="10",
            price="100",
            fees="2",
        ),
    ])

    assert portfolio.average_costs() == {
        "VWCE": Decimal("100.2"),
    }


def test_average_cost_of_multiple_purchases() -> None:
    portfolio = Portfolio([
        make_transaction(
            "BUY",
            ticker="VWCE",
            quantity="10",
            price="100",
            fees="2",
        ),
        make_transaction(
            "BUY",
            ticker="VWCE",
            quantity="5",
            price="130",
            fees="1",
        ),
    ])

    assert portfolio.average_costs() == {
        "VWCE": Decimal("110.2"),
    }


def test_partial_sell_does_not_change_average_cost() -> None:
    portfolio = Portfolio([
        make_transaction(
            "BUY",
            quantity="10",
            price="100",
        ),
        make_transaction(
            "BUY",
            quantity="10",
            price="120",
        ),
        make_transaction(
            "SELL",
            quantity="5",
            price="150",
        ),
    ])

    assert portfolio.average_costs() == {
        "VWCE": Decimal("110"),
    }


def test_full_sell_removes_average_cost() -> None:
    portfolio = Portfolio([
        make_transaction(
            "BUY",
            quantity="10",
            price="100",
            fees="2",
        ),
        make_transaction(
            "SELL",
            quantity="10",
            price="120",
            fees="1",
        ),
    ])

    assert portfolio.average_costs() == {}


def test_new_purchase_after_full_sell_starts_new_average_cost() -> None:
    portfolio = Portfolio([
        make_transaction(
            "BUY",
            quantity="10",
            price="100",
        ),
        make_transaction(
            "SELL",
            quantity="10",
            price="120",
        ),
        make_transaction(
            "BUY",
            quantity="5",
            price="130",
            fees="1",
        ),
    ])

    assert portfolio.average_costs() == {
        "VWCE": Decimal("130.2"),
    }


def test_average_costs_are_calculated_separately_by_ticker() -> None:
    portfolio = Portfolio([
        make_transaction(
            "BUY",
            ticker="VWCE",
            quantity="10",
            price="100",
        ),
        make_transaction(
            "BUY",
            ticker="XEON",
            quantity="5",
            price="140",
        ),
        make_transaction(
            "BUY",
            ticker="VWCE",
            quantity="10",
            price="120",
        ),
    ])

    assert portfolio.average_costs() == {
        "VWCE": Decimal("110"),
        "XEON": Decimal("140"),
    }


def test_unrealized_pnl_calculates_profit_for_each_position() -> None:
    portfolio = Portfolio([
        make_transaction(
            "BUY",
            ticker="VWCE",
            quantity="10",
            price="100",
        ),
        make_transaction(
            "BUY",
            ticker="VWCE",
            quantity="10",
            price="120",
        ),
        make_transaction(
            "BUY",
            ticker="XEON",
            quantity="5",
            price="140",
        ),
    ])

    price_provider = DictionaryPriceProvider({
        "VWCE": Decimal("125"),
        "XEON": Decimal("138"),
    })

    assert portfolio.unrealized_pnl(price_provider) == {
        "VWCE": Decimal("300"),
        "XEON": Decimal("-10"),
    }


def test_unrealized_pnl_of_empty_portfolio_is_empty() -> None:
    portfolio = Portfolio([])
    price_provider = DictionaryPriceProvider({})

    assert portfolio.unrealized_pnl(price_provider) == {}


def test_unrealized_pnl_uses_remaining_quantity_after_sell() -> None:
    portfolio = Portfolio([
        make_transaction(
            "BUY",
            quantity="10",
            price="100",
        ),
        make_transaction(
            "SELL",
            quantity="4",
            price="130",
        ),
    ])

    price_provider = DictionaryPriceProvider({
        "VWCE": Decimal("120"),
    })

    assert portfolio.unrealized_pnl(price_provider) == {
        "VWCE": Decimal("120"),
    }