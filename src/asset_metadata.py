from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AssetMetadata:
    name: str
    asset_class: str


ASSET_METADATA: dict[str, AssetMetadata] = {
    "ALLW": AssetMetadata(
        name="Xtrackers FTSE All-World",
        asset_class="Equity",
    ),
    "MTD": AssetMetadata(
        name="Amundi Euro Government Bond 7-10Y",
        asset_class="Bonds",
    ),
    "VWCE": AssetMetadata(
        name="Vanguard FTSE All-World",
        asset_class="Equity",
    ),
    "XEON": AssetMetadata(
        name="Xtrackers II EUR Overnight Rate Swap",
        asset_class="Money market",
    ),
    "COMF": AssetMetadata(
    name="Example Commodities ETF",
    asset_class="Commodities",
    ),
}