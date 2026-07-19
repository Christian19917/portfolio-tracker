import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.transaction import Transaction


def read_transactions(file_path: Path) -> list[Transaction]:
    transactions = []

    with file_path.open(mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            transaction = Transaction(
                transaction_date=date.fromisoformat(row["date"]),
                transaction_type=row["type"].strip().upper(),
                ticker=row["ticker"].strip().upper(),
                quantity=Decimal(row["quantity"]),
                price=Decimal(row["price"]),
                fees=Decimal(row["fees"]),
            )

            transactions.append(transaction)

    return transactions