import csv
from datetime import datetime
import matplotlib.pyplot as plt


class StockMarketIndicator:
    def __init__(self, data: list[tuple[datetime, float, float, float]]):
        date, close, high, low = zip(*data)
        self._stock_history = dict(zip(date, close))
        self._macd, self._signal = self._calculate_macd(12, 26, 9)

    def _calculate_ema(self, n: int, values: list[float] = None) -> list[float]:
        if not values:
            values = self.values

        if n <= 0 or n >= len(values):
            raise ValueError("Invalid period length")

        # initialize EMA with SMA of first 'n' values
        ema = sum(values[:n]) / n
        ema_values = [ema]
        alpha = 2 / (n + 1)

        for i in range(n, len(values)):
            ema += (values[i] - ema) * alpha
            ema_values.append(ema)

        return ema_values

    def _calculate_macd(self, short_period: int, long_period: int, signal_period: int) -> tuple[list[float], list[float]]:
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

    def plot(self, y=None, x_label="Date", y_label="Close, $", title=None, time_units: int = None):
        try:
            x = self.dates[-time_units:] if time_units else self.dates
            if y:
                y = y[-time_units:] if time_units else y
            else:
                y = self.values[-time_units:] if time_units else self.values

            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(title)
            plt.plot(x, y)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except ValueError:
            print(f"Error: Data length is less than {time_units}")

    @staticmethod
    def get_intersection_points(x, y1, y2, time_units: int = None) -> tuple[list[tuple[datetime, float]], list[tuple[datetime, float]]]:
        # intersection points are found between the last 'n' elements
        time_units = time_units if time_units else len(y1)
        x = x[-len(y1):]
        asc = []
        desc = []
        for i in range(len(y1) - time_units, len(y1) - 1):
            above_before = y1[i] > y2[i]
            above_after = y1[i + 1] > y2[i + 1]
            if above_before and not above_after:
                desc.append((x[i], y1[i]))
            elif not above_before and above_after:
                asc.append((x[i], y1[i]))
        return asc, desc

    def _double_plot_with_intersections(self, y1: list, y2: list, n: int = None, title: str = None,
                                        label1: str = "MACD", label2: str = "Signal",
                                        x_label: str = "Date", y_label: str = None,
                                        point_label1: str = "Buy", point_label2: str = "Sell"):
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

            # Plot intersection points
            buy_points, sell_points = self.get_intersection_points(x, y1, y2, n)
            plot_x, plot_y = zip(*buy_points)
            plt.scatter(plot_x, plot_y, color='g', label=point_label1)
            plot_x, plot_y = zip(*sell_points)
            plt.scatter(plot_x, plot_y, color='r', label=point_label2)

            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except ValueError:
            print(f"Error: Data length is less than {n}")

    def plot_macd(self, time_units: int = None, title="MACD"):
        self._double_plot_with_intersections(self.macd, self.signal, time_units, title=title)

    def __get_buy_and_sell_dates(self, n:int = None):
        n = n if n else min(len(self.macd), len(self.signal))
        dates = self.dates[-len(self.macd):]
        buy_points, sell_points = self.get_intersection_points(dates, self.macd, self.signal, n)
        buy_dates, _ = zip(*buy_points)
        sell_dates, _ = zip(*sell_points)
        return buy_dates, sell_dates

    def plot_benefit(self, time_units: int = None):
        plt.figure(figsize=(10, 6))
        buy_dates, sell_dates = self.__get_buy_and_sell_dates(time_units)
        if sell_dates[0] < buy_dates[0]:
            sell_dates = sell_dates[1:]

        # diagram of buy and sell actions
        for buy_date, sell_date in zip(buy_dates, sell_dates):
            buy_price = self.stock_history[buy_date]
            sell_price = self.stock_history[sell_date]

            color = 'g' if sell_price > buy_price else 'r'
            width = sell_date - buy_date
            plt.bar(x=buy_date + width / 2, height=sell_price - buy_price, width=width, color=color, alpha=0.5)

        plt.xlabel('Date')
        plt.ylabel('Benefit, $')
        plt.title('Benefits with Buy and Sell Actions')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def _print_state(self, shares: int, cash: float, date: datetime, title="Simulation"):
        print(title)
        print("Date:", date.date())
        print(f"Cash: {cash:.2f} $")
        print("Shares:", shares, " shares")
        print(f"Total: {cash + shares * self.stock_history[date]:.2f} $\n")

    def simulate_transactions(self, shares: int = 1, cash: float = 0, time_units: int = None):
        if not time_units:
            time_units = len(self.dates)

        self._print_state(shares, cash, self.dates[-time_units])

        self._print_state(shares, cash, self.dates[-1], title="State without any actions")

        buy_dates, sell_dates = self.__get_buy_and_sell_dates(time_units)
        for date in sorted(buy_dates + sell_dates):
            price = self.stock_history[date]
            if date in buy_dates:
                shares_number = cash // price
                cash -= shares_number * price
                shares += shares_number
            else:
                cash += shares * price
                shares = 0

        self._print_state(shares, cash, self.dates[-1], title="State after simulation")

    @property
    def dates(self):
        return list(self._stock_history.keys())

    @property
    def values(self):
        return list(self._stock_history.values())

    @property
    def macd(self):
        return self._macd

    @property
    def signal(self):
        return self._signal

    @property
    def stock_history(self):
        return self._stock_history
