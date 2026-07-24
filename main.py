from datetime import date
from decimal import Decimal
from pathlib import Path

from src.asset_allocation import (
    allocation_by_asset_class,
    calculate_allocation,
)
from src.asset_metadata import ASSET_METADATA
from src.charts.allocation_chart import plot_allocation
from src.charts.portfolio_chart import plot_portfolio_history
from src.portfolio import Portfolio
from src.portfolio_analytics import (
    calculate_market_values,
    calculate_total_market_value,
    calculate_total_unrealized_pnl,
    calculate_unrealized_pnl,
)
from src.portfolio_history import PortfolioHistory
from src.providers.yahoo_price_provider import YahooPriceProvider
from src.transaction_reader import read_transactions


TRANSACTIONS_PATH = Path("data/transactions.csv")

TICKER_MAPPING = {
    "MTD": "MTD.PA",
    "ALLW": "ALLW.DE",
    "VWCE": "VWCE.DE",
    "XEON": "XEON.DE",
}


def main() -> None:
    transactions = read_transactions(
        TRANSACTIONS_PATH
    )

    if not transactions:
        print("No transactions found.")
        return

    portfolio = Portfolio(transactions)

    positions = portfolio.positions()

    if not positions:
        print("The portfolio is empty.")
        return

    price_provider = YahooPriceProvider(
        TICKER_MAPPING
    )

    current_prices = {
        ticker: price_provider.get_price(ticker)
        for ticker in positions
    }

    average_costs = portfolio.average_costs()

    market_values = calculate_market_values(
        portfolio,
        current_prices,
    )

    unrealized_pnl = calculate_unrealized_pnl(
        portfolio,
        current_prices,
    )

    ticker_allocation = calculate_allocation(
        market_values
    )

    asset_class_allocation = allocation_by_asset_class(
        market_values,
        ASSET_METADATA,
    )

    total_market_value = calculate_total_market_value(
        market_values
    )

    total_unrealized_pnl = calculate_total_unrealized_pnl(
        unrealized_pnl
    )

    print("\nPORTFOLIO SUMMARY")
    print("-" * 90)

    print(
        f"{'Ticker':<10}"
        f"{'Quantity':>12}"
        f"{'Avg cost':>14}"
        f"{'Price':>14}"
        f"{'Value':>18}"
        f"{'P/L':>18}"
    )

    print("-" * 90)

    for ticker, quantity in positions.items():
        current_price = current_prices[ticker]
        average_cost = average_costs[ticker]
        market_value = market_values[ticker]
        pnl = unrealized_pnl[ticker]

        print(
            f"{ticker:<10}"
            f"{quantity:>12}"
            f"{average_cost:>14.2f}"
            f"{current_price:>14.2f}"
            f"{market_value:>18.2f}"
            f"{pnl:>18.2f}"
        )

    print("-" * 90)

    print(
        f"{'TOTAL':<50}"
        f"{total_market_value:>18.2f}"
        f"{total_unrealized_pnl:>18.2f}"
    )

    start_date = min(
        transaction.transaction_date
        for transaction in transactions
    )

    history_builder = PortfolioHistory(
        transactions=transactions,
        price_provider=price_provider,
    )

    snapshots = history_builder.build(
        start_date=start_date,
        end_date=date.today(),
    )

    print("\nPORTFOLIO HISTORY")
    print("-" * 85)

    for snapshot in snapshots:
        print(
            f"{snapshot.snapshot_date} | "
            f"Assets: €{snapshot.market_value:.2f} | "
            f"P/L: €{snapshot.profit_loss:.2f}"
        )

    plot_portfolio_history(
        snapshots,
        output_path=Path(
            "output/portfolio_history.png"
        ),
    )

    plot_allocation(
        {
            ticker: float(percentage)
            for ticker, percentage
            in ticker_allocation.items()
        },
        title="Allocation by ETF",
        output_path=Path(
            "output/allocation_by_etf.png"
        ),
    )

    plot_allocation(
        {
            asset_class: float(percentage)
            for asset_class, percentage
            in asset_class_allocation.items()
        },
        title="Allocation by asset class",
        output_path=Path(
            "output/allocation_by_asset_class.png"
        ),
    )


if __name__ == "__main__":
    main()