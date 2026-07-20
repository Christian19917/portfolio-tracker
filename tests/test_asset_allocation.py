from decimal import Decimal

import pytest

from src.asset_allocation import (
    allocation_by_asset_class,
    calculate_allocation,
)
from src.asset_metadata import AssetMetadata


def test_calculates_allocation_percentage() -> None:
    values = {
        "ALLW": Decimal("8000"),
        "MTD": Decimal("2000"),
    }

    assert calculate_allocation(values) == {
        "ALLW": Decimal("80"),
        "MTD": Decimal("20"),
    }


def test_empty_allocation_returns_empty_dictionary() -> None:
    assert calculate_allocation({}) == {}


def test_groups_allocation_by_asset_class() -> None:
    market_values = {
        "ALLW": Decimal("6000"),
        "VWCE": Decimal("2000"),
        "MTD": Decimal("2000"),
    }

    metadata = {
        "ALLW": AssetMetadata(
            name="All World 1",
            asset_class="Equity",
        ),
        "VWCE": AssetMetadata(
            name="All World 2",
            asset_class="Equity",
        ),
        "MTD": AssetMetadata(
            name="Government Bonds",
            asset_class="Bonds",
        ),
    }

    assert allocation_by_asset_class(
        market_values,
        metadata,
    ) == {
        "Equity": Decimal("80"),
        "Bonds": Decimal("20"),
    }


def test_missing_metadata_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match="Missing metadata for ticker: UNKNOWN",
    ):
        allocation_by_asset_class(
            {"UNKNOWN": Decimal("100")},
            {},
        )