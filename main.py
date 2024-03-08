import csv
import matplotlib.pyplot as plt
from datetime import datetime


def process_data():
    with open('data/SnP500.csv', 'r') as file:
        reader = csv.DictReader(file)
        data = []
        for row in reader:
            date = datetime.strptime(row['Date'], '%Y-%m-%d')
            value = float(row['Closing'])
            data.append((date, value))

        # Sort the data by date
        data.sort(key=lambda x: x[0])
    return data


def create_plot(x, y, x_label, y_label, title):
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.plot(x, y)
    plt.show()


def main():
    dates, values = zip(*process_data())
    create_plot(dates, values, 'Date', 'S&P 500', 'S&P 500 Closing Prices')


if __name__ == '__main__':
    main()
