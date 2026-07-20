from decimal import Decimal
from pathlib import Path

import matplotlib.pyplot as plt

from src.portfolio_history import PortfolioSnapshot


def plot_portfolio_history(
    snapshots: list[PortfolioSnapshot],
    output_path: Path | None = None,
) -> None:
    if not snapshots:
        raise ValueError(
            "Cannot plot an empty portfolio history"
        )

    dates = [
        snapshot.snapshot_date
        for snapshot in snapshots
    ]

    portfolio_values = [
        float(snapshot.market_value)
        for snapshot in snapshots
    ]

    invested_capital = [
        float(snapshot.invested_capital)
        for snapshot in snapshots
    ]

    latest_snapshot = snapshots[-1]

    return_percentage = (
        latest_snapshot.profit_loss
        / latest_snapshot.invested_capital
        * 100
        if latest_snapshot.invested_capital != 0
        else Decimal("0")
    )

    line_color = (
        "green"
        if latest_snapshot.profit_loss >= 0
        else "red"
    )

    positive_mask = [
        value >= capital
        for value, capital in zip(
            portfolio_values,
            invested_capital,
        )
    ]

    negative_mask = [
        value < capital
        for value, capital in zip(
            portfolio_values,
            invested_capital,
        )
    ]

    plt.figure(figsize=(11, 6))

    plt.plot(
        dates,
        portfolio_values,
        linewidth=2.5,
        color=line_color,
        label="Portfolio value",
    )

    plt.plot(
        dates,
        invested_capital,
        linestyle="--",
        linewidth=2,
        color="gray",
        label="Invested capital",
    )

    plt.fill_between(
        dates,
        portfolio_values,
        invested_capital,
        where=positive_mask,
        color="green",
        alpha=0.25,
        interpolate=True,
    )

    plt.fill_between(
        dates,
        portfolio_values,
        invested_capital,
        where=negative_mask,
        color="red",
        alpha=0.25,
        interpolate=True,
    )

    plt.title(
        "Portfolio performance\n"
        f"Portfolio Value: "
        f"€{latest_snapshot.market_value:.2f} | "
        f"Unrealized P/L: €{latest_snapshot.profit_loss:.2f} "
        f"({return_percentage:.2f}%)"
    )

    plt.xlabel("Date")
    plt.ylabel("Value (€)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        plt.savefig(
            output_path,
            dpi=150,
            bbox_inches="tight",
        )

    plt.show()
    plt.close()