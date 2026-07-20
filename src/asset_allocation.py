from decimal import Decimal

from src.asset_metadata import AssetMetadata


def calculate_allocation(
    values: dict[str, Decimal],
) -> dict[str, Decimal]:
    total_value = sum(
        values.values(),
        start=Decimal("0"),
    )

    if total_value == 0:
        return {}

    return {
        name: value / total_value * Decimal("100")
        for name, value in values.items()
    }


def allocation_by_asset_class(
    market_values: dict[str, Decimal],
    metadata: dict[str, AssetMetadata],
) -> dict[str, Decimal]:
    values_by_class: dict[str, Decimal] = {}

    for ticker, market_value in market_values.items():
        try:
            asset_class = metadata[ticker].asset_class
        except KeyError as error:
            raise ValueError(
                f"Missing metadata for ticker: {ticker}"
            ) from error

        values_by_class[asset_class] = (
            values_by_class.get(
                asset_class,
                Decimal("0"),
            )
            + market_value
        )

    return calculate_allocation(values_by_class)