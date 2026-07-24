from decimal import Decimal

from src.portfolio import Portfolio


def calculate_market_values(
    portfolio: Portfolio,
    current_prices: dict[str, Decimal],
) -> dict[str, Decimal]:
    positions = portfolio.positions()

    return {
        ticker: current_prices[ticker] * quantity
        for ticker, quantity in positions.items()
    }


def calculate_unrealized_pnl(
    portfolio: Portfolio,
    current_prices: dict[str, Decimal],
) -> dict[str, Decimal]:
    positions = portfolio.positions()
    average_costs = portfolio.average_costs()

    return {
        ticker: (
            current_prices[ticker] - average_costs[ticker]
        ) * quantity
        for ticker, quantity in positions.items()
    }


def calculate_total_market_value(
    market_values: dict[str, Decimal],
) -> Decimal:
    return sum(
        market_values.values(),
        Decimal("0"),
    )


def calculate_total_invested_capital(
    portfolio: Portfolio,
) -> Decimal:
    positions = portfolio.positions()
    average_costs = portfolio.average_costs()

    return sum(
        (
            average_costs[ticker] * quantity
            for ticker, quantity in positions.items()
        ),
        Decimal("0"),
    )


def calculate_total_unrealized_pnl(
    unrealized_pnl: dict[str, Decimal],
) -> Decimal:
    return sum(
        unrealized_pnl.values(),
        Decimal("0"),
    )


def calculate_total_return_percentage(
    total_unrealized_pnl: Decimal,
    total_invested_capital: Decimal,
) -> Decimal:
    if total_invested_capital == Decimal("0"):
        return Decimal("0")

    return (
        total_unrealized_pnl
        / total_invested_capital
        * Decimal("100")
    )