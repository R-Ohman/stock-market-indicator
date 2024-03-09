import csv
from datetime import datetime
import matplotlib.pyplot as plt


class StockMarketIndicator:

    def __init__(self, path_to_data):
        self._dates, self._values = zip(*self._process_data(path_to_data))
        self._stock_history = dict(zip(self._dates, self._values))
        self._macd, self._signal = self._calculate_macd(12, 26, 9)

    def _process_data(self, path):
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

    def _calculate_ema(self, n, values=None):
        if not values:
            values = self.values

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

    def _calculate_macd(self, short_period, long_period, signal_period):
        if short_period >= long_period:
            raise ValueError("Short period must be less than long period")

        short_ema = self._calculate_ema(short_period)
        long_ema = self._calculate_ema(long_period)

        # ensure lengths of short_ema and long_ema are the same
        min_length = min(len(short_ema), len(long_ema))
        # keep only the last min_length elements
        short_ema = short_ema[-min_length:]
        long_ema = long_ema[-min_length:]

        macd = [short_ema[i] - long_ema[i] for i in range(min_length)]
        signal = self._calculate_ema(signal_period, values=macd)

        return macd[-len(signal):], signal

    def plot(self, x_label="Date", y_label="Close, $", title=None, n=None):
        try:
            x = self.dates[-n:] if n else self.dates
            y = self.values[-n:] if n else self.values

            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(title)
            plt.plot(x, y)
            plt.show()
        except ValueError:
            print(f"Error: Data length is less than {n}")

    def _get_intersection_points(self, x, y1, y2, n=None):
        n = n if n else len(y1)
        x = x[-len(y1):]
        asc = []
        desc = []
        for i in range(len(y1) - n, len(y1) - 1):
            if y1[i] > y2[i] and y1[i + 1] < y2[i + 1]:
                desc.append((x[i], y1[i]))
            elif y1[i] < y2[i] and y1[i + 1] > y2[i + 1]:
                asc.append((x[i], y1[i]))
        return asc, desc

    def _double_plot_with_intersections(self, y1:list, y2:list, n:int=None, title:str=None, label1:str=None, label2:str=None,
                                        x_label:str="Date", y_label:str=None, point_label1:str="Buy", point_label2:str="Sell"):
        try:
            n = n if n else min(len(y1), len(y2))
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(title)

            # Get last 'n' elements
            x = self.dates[-n:]
            y1 = y1[-n:]
            y2 = y2[-n:]

            plt.plot(x, y1, label=label1)
            plt.plot(x, y2, label=label2)

            # Find intersection points
            buy_points, sell_points = self._get_intersection_points(x, y1, y2, n)
            plot_x, plot_y = zip(*buy_points)
            plt.scatter(plot_x, plot_y, color='g', label=point_label1)
            plot_x, plot_y = zip(*sell_points)
            plt.scatter(plot_x, plot_y, color='r', label=point_label2)

            plt.legend()
            plt.show()
        except ValueError:
            print(f"Error: Data length is less than {n}")

    def plot_macd(self, n=None, title="MACD"):
        self._double_plot_with_intersections(self.macd, self.signal, n, title=title, label1="MACD", label2="Signal")

    def plot_benefit(self, n=None):
        n = n if n else min(len(self.macd), len(self.signal))
        buy_points, sell_points = self._get_intersection_points(self.dates[-len(self.macd):], self.macd, self.signal, n)
        plt.figure(figsize=(10, 6))

        # Plot stock prices
        #plt.plot(x, y, label='Stock Prices')
        buy_dates, _ = zip(*buy_points)
        sell_dates, _ = zip(*sell_points)

        benefit_positive = 0
        benefit_negative = 0

        # Plot buy and sell rectangles
        for buy_date, sell_date in zip(buy_dates, sell_dates):
            buy_price = self.stock_history[buy_date]
            sell_price = self.stock_history[sell_date]

            if sell_price > buy_price:
                benefit_positive += sell_price - buy_price
            else:
                benefit_negative += sell_price - buy_price

            color = 'g' if sell_price > buy_price else 'r'
            width = sell_date - buy_date
            plt.bar(x=buy_date + width/2, height=sell_price - buy_price, width=width, color=color, alpha=0.5)

        plt.xlabel('Date')
        plt.ylabel('Benefit, $')
        plt.title('Benefits with Buy and Sell Actions')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        print(benefit_positive, "$")
        print(benefit_negative, "$")
        print("Total:", benefit_positive + benefit_negative, "$")

    def simulate_transactions(self, shares=1, cash=0, weeks=None):
        pass

    @property
    def dates(self):
        return self._dates

    @property
    def values(self):
        return self._values

    @property
    def macd(self):
        return self._macd

    @property
    def signal(self):
        return self._signal

    @property
    def stock_history(self):
        return self._stock_history