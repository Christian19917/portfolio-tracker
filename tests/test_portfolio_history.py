from datetime import date
from decimal import Decimal

import pandas as pd

from src.portfolio_history import PortfolioHistory

from tests.test_portfolio import make_transaction


class FakeHistoricalPriceProvider:
    def __init__(
        self,
        histories: dict[str, pd.Series],
    ) -> None:
        self._histories = histories

    def get_history(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> pd.Series:
        return self._histories[ticker]
    

def test_builds_daily_portfolio_history() -> None:
    transactions = [
        make_transaction(
            "BUY",
            ticker="VWCE",
            quantity="10",
            price="100",
            fees="2",
            transaction_date=date(2026, 7, 8),
        ),
    ]

    prices = pd.Series(
        [
            Decimal("100"),
            Decimal("102"),
            Decimal("101"),
        ],
        index=pd.to_datetime([
            "2026-07-08",
            "2026-07-09",
            "2026-07-10",
        ]),
    )

    provider = FakeHistoricalPriceProvider({
        "VWCE": prices,
    })

    history = PortfolioHistory(
        transactions=transactions,
        price_provider=provider,
    )

    snapshots = history.build(
        start_date=date(2026, 7, 8),
        end_date=date(2026, 7, 10),
    )

    assert len(snapshots) == 3

    assert snapshots[0].market_value == Decimal("1000")
    assert snapshots[0].profit_loss == Decimal("-2")

    assert snapshots[1].market_value == Decimal("1020")
    assert snapshots[1].profit_loss == Decimal("18")