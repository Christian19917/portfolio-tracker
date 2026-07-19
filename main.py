from pathlib import Path

from src.transaction_reader import read_transactions


def main() -> None:
    file_path = Path("data/transactions.csv")
    transactions = read_transactions(file_path)

    for transaction in transactions:
        print(transaction)


if __name__ == "__main__":
    main()