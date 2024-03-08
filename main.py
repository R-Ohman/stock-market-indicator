import csv
import matplotlib.pyplot as plt
from datetime import datetime


def process_data(path):
    data = []
    try:
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    date = datetime.strptime(row['Date'], '%Y-%m-%d')
                    value = float(row['Close'])
                    data.append((date, value))
                except ValueError:
                    print("Warning: Skipping row with invalid data:", row)

            data.sort(key=lambda x: x[0])
    except FileNotFoundError:
        print(f"Error: File '{path}' not found")

    return data


def create_plot(x, y, x_label, y_label, title):
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.plot(x, y)
    plt.show()


def create_double_plot(x, y1, y2, x_label, y_label, title, label1, label2, n=1000):
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.plot(x[-n:], y1[-n:], label=label1)
    plt.plot(x[-n:], y2[-n:], label=label2)
    plt.legend()
    plt.show()


def calculate_ema(values, n):
    if not values:
        return []
    if n <= 0 or n >= len(values):
        raise ValueError("Invalid period length")

    ema_values = []
    alpha = 2 / (n + 1)
    # initialize EMA with SMA of first 'n' values
    ema = sum(values[:n]) / n
    ema_values.append(ema)

    for i in range(n, len(values)):
        ema += (values[i] - ema) * alpha
        ema_values.append(ema)

    return ema_values


def calculate_macd(values, short_period, long_period, signal_period):
    if short_period >= long_period:
        raise ValueError("Short period must be less than long period")

    short_ema = calculate_ema(values, short_period)
    long_ema = calculate_ema(values, long_period)

    # ensure lengths of short_ema and long_ema are the same
    min_length = min(len(short_ema), len(long_ema))
    # keep only the last min_length elements
    short_ema = short_ema[-min_length:]
    long_ema = long_ema[-min_length:]

    macd = [short_ema[i] - long_ema[i] for i in range(min_length)]
    signal = calculate_ema(macd, signal_period)

    return macd[-len(signal):], signal


def main():
    dates, values = zip(*process_data('data/SnP500.csv'))
    create_plot(dates, values, 'Date', 'S&P 500', 'S&P 500 Closing Prices')

    macd, signal = calculate_macd(values, 12, 26, 9)
    samples_number = 250
    create_double_plot(dates[-len(macd):], macd, signal, 'Date', '', 'MACD and Signal Line', 'MACD', 'Signal Line', samples_number)


if __name__ == '__main__':
    main()
