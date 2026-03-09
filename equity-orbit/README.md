# Equity Orbit

Equity Orbit is a Python-based data analysis tool designed to generate comprehensive investment reports from financial transaction data. It processes CSV transaction logs, calculates key performance metrics, and generates detailed markdown reports with breakdowns by category, instrument, and year.

## Features

- **Transaction Parsing:** Reads CSV files containing financial transaction data.
- **Metric Calculation:** Computes key metrics including:
  - Total Invested Amount
  - Total Buy Amounts
  - Dividend Income
  - Lending Income (SLIP)
  - Number of Trades
  - Unique Instruments
- **Performance Analysis:**
  - **XIRR Calculation:** Optional annualized return (XIRR) calculation if the current portfolio value is provided.
  - **Category Breakdown:** Splits portfolio into categories like Company, ETF, and Gold.
  - **Yearly Analysis:** precise breakdown of investments and returns for each year.
- **Reporting:** Generates clean, readable Markdown reports (`.md`) suitable for documentation or sharing.
- **Logging:** Detailed logging of each run for auditing and debugging.

## Prerequisites

- **Python 3.10+**
- **uv** (recommended for dependency management) or `pip`

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd equity-orbit
   ```

2. **Install dependencies:**
   Using `uv` (Recommended):
   ```bash
   uv sync
   ```
## Usage

### Basic Run
Run the analysis with default settings (uses `data/data.csv` and `data/config.yaml`):

```bash
uv run main.py
```
Or with python directly:
```bash
python main.py
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--data` | Path to input CSV data file. | `data/data.csv` |
| `--config` | Path to configuration YAML file. | `data/config.yaml` |
| `--current-value` | (Optional) Current total value of the portfolio for XIRR calculation. | None |

### Examples

**Specify custom data file:**
```bash
uv run main.py --data my_transactions.csv
```

**Calculate [XIRR](https://www.youtube.com/watch?v=2IqISNe9lks) by providing current portfolio value:**
```bash
uv run main.py --current-value 18740.40
```

## How to Get Data

### Official Export (CSV)
Robinhood provides a self-service tool on their web platform:
1. Log in to [robinhood.com](https://robinhood.com).
2. Navigate to **Account** > **Reports and statements**.
3. Use the **"Customize your report"** feature to select your account and date range.
4. Download the generated report as a **CSV**.

## Input Data Format

The input CSV should typically contain columns for:
- **Settle Date:** Date of the transaction.
- **Trans Code:** Type of transaction (e.g., `Buy`, `CDIV`, `RTP`, `SLIP`).
- **Amount:** Transaction amount (negative for outflows/buys, positive for inflows/dividends).
- **Description:** Details about the transaction (instrument name, etc.).
- **Price:** Price per share (optional but useful).
- **Quantity:** Number of shares (optional but useful).

*(Column mapping is configurable via `data/config.yaml`)*

## Output

- **Reports:** Markdown reports are saved in the `output/` directory (e.g., `output/report_20250101_120000.md`).
- **Logs:** Run logs are stored in `logs/` directory, organized by timestamp.
- **Intermediate Data:** CSVs of processed dataframes are saved within the specific log directory for each run.

## Project Structure

```
equity-orbit/
├── data/               # Input data and configuration
│   ├── config.yaml
│   └── data.csv
├── logs/               # Execution logs and intermediate CSVs
├── output/             # Generated Markdown reports
├── src/                # Source code
│   ├── data_processing.py
│   ├── logger.py
│   ├── report.py
│   └── utils.py
├── main.py             # Entry point script
├── pyproject.toml      # Project configuration and dependencies
└── README.md           # Project documentation
```
