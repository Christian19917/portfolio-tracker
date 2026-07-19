from decimal import Decimal

import pytest

from src.providers.dictionary_price_provider import (
    DictionaryPriceProvider,
)


def test_get_price_returns_available_price() -> None:
    provider = DictionaryPriceProvider({
        "VWCE": Decimal("145.32"),
    })

    assert provider.get_price("VWCE") == Decimal("145.32")


def test_get_price_normalizes_ticker() -> None:
    provider = DictionaryPriceProvider({
        "VWCE": Decimal("145.32"),
    })

    assert provider.get_price(" vwce ") == Decimal("145.32")


def test_constructor_normalizes_tickers() -> None:
    provider = DictionaryPriceProvider({
        " vwce ": Decimal("145.32"),
    })

    assert provider.get_price("VWCE") == Decimal("145.32")


def test_missing_price_raises_value_error() -> None:
    provider = DictionaryPriceProvider({})

    with pytest.raises(
        ValueError,
        match="Price not available for ticker: VWCE",
    ):
        provider.get_price("VWCE")