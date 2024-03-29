import csv
from datetime import datetime

from PlotManager import PlotManager
from smi import StockMarketIndicator
import requests
from config import ALPHAVANTAGE_API_KEY, YFINANCE_API_KEY


def process_file(path, points_number=1000,
                 from_date=datetime.min,
                 to_date=datetime.max) -> list[tuple[datetime, float, float, float]]:
    data = []
    try:
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    date = datetime.strptime(row['Date'], '%Y-%m-%d')
                    if date < from_date or date > to_date:
                        continue

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


def process_symbol(symbol: str, time_series: str, interval: int = 60, points_number=1000)\
        -> list[tuple[datetime, float, float, float]]:
    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_{time_series}' + \
                f'&symbol={symbol}&apikey={ALPHAVANTAGE_API_KEY}&outputsize=full'
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
            data_title = 'Time Series (Daily)'
        elif time_series == 'weekly':
            data_title = 'Weekly Time Series'
        else:
            data_title = 'Monthly Time Series'

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


def get_symbol(search_term: str) -> str:
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


def ui_get_data() -> list[tuple[datetime, float, float, float]]:
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


def user_interface():
    print("Welcome to Stock Market Indicator")
    data = ui_get_data()
    smi = StockMarketIndicator(data)

    pm = PlotManager(smi)
    pm.plot(title='Historical Stock Data')
    pm.plot_macd(title='MACD')
    pm.plot_williams(title='Williams %R')
    pm.plot_with_buy_and_sell()
    pm.plot_benefit()

    print("\nSimulation:\n")
    shares = int(input("Enter the number of shares: "))
    cash = float(input("Enter the amount of cash: "))
    smi.simulate_transactions(shares=shares, cash=cash)


def main():
    user_interface()

    # notations_number = 1000
    # instrument_name = 'Apple Inc.'
    # data = process_file('data/apple_d.csv', points_number=notations_number)
    # smi = StockMarketIndicator(data)
    # smi.simulate_transactions(shares=1000, cash=0, csv_file=f"simulation/{instrument_name}.csv")
    #
    # pm = PlotManager(smi)
    # pm.plot(title=instrument_name)
    # pm.plot_macd(title=f"{instrument_name} MACD")
    # pm.plot_williams(title=f"{instrument_name} Williams %R")
    # pm.plot_with_buy_and_sell()
    # pm.plot_benefit()


if __name__ == '__main__':
    main()
