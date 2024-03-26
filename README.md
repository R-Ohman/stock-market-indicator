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

## Example

<div align="center">
  <img src="https://github.com/R-Ohman/stock-market-indicator/assets/113181317/424b4861-195c-41a0-b398-0da538ddbf13" style="width: 75%;">
  <img src="https://github.com/R-Ohman/stock-market-indicator/assets/113181317/91009901-9e57-4a97-86be-e94d6ba20aff" style="width: 49%;">
  <img src="https://github.com/R-Ohman/stock-market-indicator/assets/113181317/e3d18ecd-b696-4117-9018-c745cc3e71e5" style="width: 49%;">
  <img src="https://github.com/R-Ohman/stock-market-indicator/assets/113181317/273a17b7-512b-4f29-9547-276e26052fd6" style="width: 49%;">
  <img src="https://github.com/R-Ohman/stock-market-indicator/assets/113181317/a45d8a32-057f-4dd2-9746-7b0c222180f7" style="width: 49%;">
</div>


## Contributing

Contributions are welcome! If you have any suggestions, bug fixes, or new features to add, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
