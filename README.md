# Portfolio Tracker

A Python and Streamlit application for tracking, analyzing, and visualizing a long-term investment portfolio.

The project provides a simple dashboard where users can monitor portfolio value, investment performance, asset allocation, transaction history, fees, and progress toward a financial goal.

## Features

### Portfolio Overview

* Current portfolio value
* Total invested capital
* Unrealized profit and loss
* Portfolio return
* Progress toward a user-defined investment goal

### Performance Analysis

* Historical portfolio value
* Invested capital over time
* Profit and loss tracking
* Performance visualization

### Asset Allocation

* Allocation by individual asset
* Allocation by asset class
* Percentage-based portfolio composition

Supported asset classes can include:

* Equity
* Bonds
* Commodities
* Other investment categories

### Transaction Tracking

The application reads portfolio transactions from CSV files and provides a structured transaction history including:

* Buy transactions
* Quantity
* Purchase price
* Transaction fees
* Total transaction value

Fees are tracked separately so their impact on the portfolio remains visible.

### Goal Tracker

Users can define their own portfolio target directly from the application.

The dashboard then displays the current progress toward that goal through a visual progress indicator.

## Project Structure

```text
portfolio-tracker/
│
├── app.py
├── main.py
│
├── pages/
│   ├── overview.py
│   ├── performance.py
│   ├── allocation.py
│   └── transactions.py
│
├── src/
│   ├── portfolio.py
│   ├── portfolio_history.py
│   ├── transaction.py
│   ├── transaction_reader.py
│   │
│   ├── providers/
│   │   └── yahoo_price_provider.py
│   │
│   └── charts/
│
├── tests/
│
├── data/
│
├── output/
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Technologies

The project is built primarily with:

* Python
* Streamlit
* Pandas
* Matplotlib
* Yahoo Finance market data
* Pytest

## Installation

Clone the repository:

```bash
git clone https://github.com/Christian19917/portfolio-tracker.git
```

Move into the project directory:

```bash
cd portfolio-tracker
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Start the Streamlit application with:

```bash
streamlit run app.py
```

Streamlit will open the portfolio dashboard in your browser.

## Transaction Data

Portfolio transactions are imported from CSV files.

Example:

```csv
date,type,ticker,quantity,price,fee
2026-01-01,BUY,VWCE,10,160,2
2026-02-01,BUY,XEON,5,140,1
2026-03-01,BUY,VWCE,2,155,1
```

Real personal transaction files should not be committed to the repository.

## Testing

The project includes automated tests for core portfolio functionality.

Run the test suite with:

```bash
pytest
```

Tests cover areas such as:

* Portfolio calculations
* Average cost calculation
* Portfolio history
* Price provider behavior

## Architecture

The project separates the user interface from the underlying portfolio logic.

The Streamlit application is responsible for presentation and interaction, while the modules inside `src/` handle portfolio calculations, transaction processing, historical data, market prices, and visualization.

This separation makes the financial logic easier to test and maintain independently from the UI.

## Motivation

I built this project to combine my background in finance with my growing experience in Python and data analysis.

The goal was to develop a practical tool capable of turning raw investment transactions and market data into useful portfolio information while applying software development concepts such as modular design, testing, data processing, and visualization.

## Future Improvements

Possible future developments include:

* Benchmark comparison
* Advanced portfolio performance metrics
* Dividend tracking
* Multi-currency support
* Broker transaction imports
* Additional risk metrics

The current version focuses on maintaining a simple and understandable long-term portfolio tracking workflow.

## Author

**Christian Onetti**

Background in Economics and Finance with an interest in Python, financial analysis, and data-driven applications.
