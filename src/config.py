from pathlib import Path
import json
from pathlib import Path

TRANSACTIONS_PATH = Path("data/transactions.csv")

POSITIVE_COLOR = "#2E8B57"
NEGATIVE_COLOR = "#D62728"
NEUTRAL_COLOR = "#808080"
BACKGROUND_COLOR = "#FFFFFF"

TICKER_MAPPING = {
    "MTD": "MTD.PA",
    "ALLW": "ALLW.DE",
    "VWCE": "VWCE.DE",
    "XEON": "XEON.DE",
}

SETTINGS_PATH = Path("data/settings.json")

DEFAULT_SETTINGS = {
    "portfolio_goal": None,
}


def load_settings() -> dict:
    if not SETTINGS_PATH.exists():
        return DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:
            settings = json.load(file)

        return {
            **DEFAULT_SETTINGS,
            **settings,
        }

    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    SETTINGS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with SETTINGS_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            settings,
            file,
            indent=4,
        )


def get_portfolio_goal() -> float | None:
    settings = load_settings()

    goal = settings.get("portfolio_goal")

    if goal is None:
        return None

    return float(goal)


def save_portfolio_goal(goal: float) -> None:
    settings = load_settings()

    settings["portfolio_goal"] = goal

    save_settings(settings)


def clear_portfolio_goal() -> None:
    settings = load_settings()

    settings["portfolio_goal"] = None

    save_settings(settings)