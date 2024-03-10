import csv
from datetime import datetime

from smi import StockMarketIndicator
import requests
from config import ALPHAVANTAGE_API_KEY, YFINANCE_API_KEY


def process_file(path, points_number=1000) -> list[tuple[datetime, float, float, float]]:
    data = []
    try:
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    date = datetime.strptime(row['Date'], '%Y-%m-%d')
                    close = float(row['Close'])
                    high = float(row['High'])
                    low = float(row['Low'])
                    data.append((date, close, high, low))
                except ValueError:
                    print("Warning: Skipping row with invalid data:", row)
    except FileNotFoundError:
        print(f"Error: File '{path}' not found")

    data.sort(key=lambda x: x[0])
    return data[-points_number:]


def process_symbol(symbol: str, time_series: str, interval: int = 60, points_number=1000) -> list[tuple[datetime, float, float, float]]:
    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_{time_series}&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}&outputsize=full'
        if interval:
            url += f'&interval={interval}min'

        r = requests.get(url)
        stock = r.json()
        data = []
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

    try:
        if time_series == 'intraday':
            data_title = f'Time Series ({interval}min)'
        elif time_series == 'daily':
            data_title = f'Time Series (Daily)'
        elif time_series == 'weekly':
            data_title = f'Weekly Time Series'
        elif time_series == 'monthly':
            data_title = f'Monthly Time Series'

        for date in list(stock[data_title].keys())[:points_number]:
            close = float(stock[data_title][date]['4. close'])
            high = float(stock[data_title][date]['2. high'])
            low = float(stock[data_title][date]['3. low'])
            if time_series == 'intraday':
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            else:
                date = datetime.strptime(date, '%Y-%m-%d')
            data.append((date, close, high, low))
    except KeyError as e:
        print(f"Error: {e}\nCheck the time series and the interval")
        return []

    data.sort(key=lambda x: x[0])
    return data


def get_symbol(search_term):
    try:
        url = f'https://yfapi.net/v6/finance/autocomplete?region=IN&lang=en&query={search_term}'
        headers = {
            'accept': 'application/json',
            'X-API-KEY': YFINANCE_API_KEY
        }
        query = requests.get(url, headers=headers)
        response = query.json()
        for i in response['ResultSet']['Result']:
            final = i['symbol']
            return final
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def user_interface():
    print("Welcome to Stock Market Indicator")
    print("1. Use a file")
    print("2. Use a symbol or company name")
    choice = input("Enter your choice: ")

    if choice == '1':
        path = input("Enter the path of the file: ")
        points_number = int(input("Enter the number of points to consider: "))
        return process_file(path=path, points_number=points_number)

    symbol = input("Enter a symbol or company name: ")
    symbol = get_symbol(symbol)
    time_series = int(input("Enter the time series (1: intraday, 2: daily, 3: weekly,4: monthly): "))
    if time_series == 1:
        time_series = 'intraday'
    elif time_series == 2:
        time_series = 'daily'
    elif time_series == 4:
        time_series = 'monthly'
    else:
        time_series = 'weekly'

    interval = None
    if time_series == 'intraday':
        interval = int(input("Enter the interval (in minutes): "))
    points_number = int(input("Enter the number of time points: "))

    return process_symbol(symbol=symbol, time_series=time_series, interval=interval, points_number=points_number)


def main():
    data = user_interface()
    smi = StockMarketIndicator(data)
    smi.plot(title='Historical Stock Data')
    smi.plot_macd(title=f"MACD")
    smi.plot_benefit()

    print("\nSimulation:\n")
    shares = int(input("Enter the number of shares: "))
    cash = float(input("Enter the amount of cash: "))
    smi.simulate_transactions(shares=shares, cash=cash)

    # N = 100
    # data = process_file('data/apple.csv', points_number=N)
    # smi = StockMarketIndicator(data)
    # smi.plot(title="Apple", time_units=N)
    # smi.plot_macd(time_units=N, title="Apple MACD")
    # smi.plot_benefit(time_units=N)
    # smi.simulate_transactions(shares=10, cash=0, time_units=N)


if __name__ == '__main__':
    main()
