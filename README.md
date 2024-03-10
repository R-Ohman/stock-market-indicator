# Stock Market Indicator

This project is a Python application for analyzing and simulating stock market data. It provides functionality to fetch historical stock data, calculate stock market indicators such as MACD (Moving Average Convergence Divergence), and simulate buying and selling actions to determine potential benefits.

## Features

- Fetch historical stock data from files or online sources.
- Calculate MACD and visualize it along with other indicators.
- Simulate buying and selling actions to analyze potential benefits.
- User-friendly command-line interface.

## Requirements

- Python 3.x
- `matplotlib` library for plotting graphs.
- `requests` library for making HTTP requests.
- An API key for [Alpha Vantage](https://www.alphavantage.co/) and [Yahoo Finance APIs](https://www.financeapi.net/).

## Installation

1. Clone the repository:

```bash
git clone https://github.com/R-Ohman/stock-market-indicator.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Obtain API keys for Alpha Vantage and Yahoo Finance APIs and update the configuration file `config.py` with your API keys.

## Usage

To run the application, execute the `main.py` script:

```bash
python main.py
```

Follow the instructions on the command line to interact with the application. You can choose to use a file containing historical stock data or specify a symbol or company name to fetch data online.

## Contributing

Contributions are welcome! If you have any suggestions, bug fixes, or new features to add, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
