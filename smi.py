from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


WILLIAMS_R_MIN = -70
WILLIAMS_R_MAX = -3


class StockMarketIndicator:
    def __init__(self, data: list[tuple[datetime, float, float, float]]):
        date, close, high, low = zip(*data)
        self._stock_history = dict(zip(date, close))
        self._macd, self._signal = self._calculate_macd(12, 26, 9)
        self._williams_r = self._calculate_williams_r(high, low)

    def _calculate_ema(self, n: int, values: list[float] = None) -> list[float]:
        if not values:
            values = self.values

        if n <= 0 or n >= len(values):
            raise ValueError("Invalid period length")

        # Initialize EMA with SMA of first 'n' values
        ema_values = [sum(values[:n]) / n]
        alpha = 2 / (n + 1)

        for i in range(n, len(values)):
            nominator = 0
            denominator = 0
            for j in range(n):
                nominator += (1 - alpha) ** j * values[i - j]
                denominator += (1 - alpha) ** j
            ema_values.append(nominator / denominator)

        return ema_values

    def _calculate_williams_r(self, high: list[float], low: list[float], n: int = 14) -> dict[datetime, float]:
        if n <= 0 or n >= len(high):
            raise ValueError("Invalid period length")

        williams_r = dict()
        for i in range(n, len(high)):
            highest_high = max(high[i - n:i + 1])
            lowest_low = min(low[i - n:i + 1])
            close = self.values[i]
            value = -100 * (highest_high - close) / (highest_high - lowest_low)
            williams_r[self.dates[i]] = value

        return williams_r

    def _calculate_macd(self, short_period: int, long_period: int, signal_period: int) -> tuple[list[float], list[float]]:
        if short_period >= long_period:
            raise ValueError("Short period must be less than long period")

        short_ema = self._calculate_ema(short_period)
        long_ema = self._calculate_ema(long_period)

        # Align EMA values, keeping only the last 'min_length' elements
        min_length = min(len(short_ema), len(long_ema))
        short_ema = short_ema[-min_length:]
        long_ema = long_ema[-min_length:]

        macd = [short_ema[i] - long_ema[i] for i in range(min_length)]
        signal = self._calculate_ema(signal_period, values=macd)

        # Align size of MACD
        return macd[-len(signal):], signal

    def plot(self, y=None, x_label="Date", y_label="Close, $", title=None, time_units: int = None):
        try:
            x = self.dates[-time_units:] if time_units else self.dates
            if y:
                y = y[-time_units:] if time_units else y
            else:
                y = self.values[-time_units:] if time_units else self.values

            plt.figure(figsize=(10, 6))
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(title)
            plt.plot(x, y)
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except ValueError:
            print(f"Error: Data length is less than {time_units}")

    def plot_williams(self, x_label="Date", y_label="Williams %R", title=None):
        try:
            plt.figure(figsize=(10, 6))
            plt.xlabel(x_label)
            plt.ylabel(y_label)
            plt.title(title)

            # Plot Williams %R values
            williams_values = list(self.williams_r.values())
            plt.plot(self.dates[-len(williams_values):], williams_values)

            # Add horizontal lines
            plt.axhline(y=WILLIAMS_R_MIN, color='g', linestyle='--', label=f'Y={WILLIAMS_R_MIN}')
            plt.axhline(y=WILLIAMS_R_MAX, color='r', linestyle='--', label=f'Y={WILLIAMS_R_MAX}')

            for filter in [False, True]:
                # Get buy and sell dates
                buy_dates, sell_dates = self.__get_buy_and_sell_dates(filter=filter)
                size = 150 if filter else 20
                # Plot buy and sell points
                plt.scatter(buy_dates, [self.williams_r[date] for date in buy_dates], color='g', label='Buy', s=size, marker='^')
                plt.scatter(sell_dates, [self.williams_r[date] for date in sell_dates], color='r', label='Sell', s=size, marker='v')

            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        except ValueError:
            print(f"Error: Data length is less than {len(williams_values)}")

    def plot_with_buy_and_sell(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.dates, self.values)
        buy_dates, sell_dates = self.__get_buy_and_sell_dates()
        plt.scatter(buy_dates, [self.stock_history[date] for date in buy_dates],
                    color='g', label='Buy', s=150, marker='^')
        plt.scatter(sell_dates, [self.stock_history[date] for date in sell_dates],
                    color='r', label='Sell', s=150, marker='v')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    @staticmethod
    def get_intersection_points(x, y1, y2, time_units: int = None)\
            -> tuple[list[tuple[datetime, float]], list[tuple[datetime, float]]]:
        # intersection points are found between the last 'n' elements
        time_units = time_units if time_units else len(y1)
        x = x[-len(y1):]
        asc = []
        desc = []
        for i in range(len(y1) - time_units + 1, len(y1)):
            above_before = y1[i - 1] > y2[i - 1]
            above_after = y1[i] > y2[i]
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
            plt.figure(figsize=(10, 6))
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

    def __get_buy_and_sell_dates(self, n: int = None, filter=True):
        n = n if n else min(len(self.macd), len(self.signal))
        dates = self.dates[-len(self.macd):]
        buy_points, sell_points = self.get_intersection_points(dates, self.macd, self.signal, n)
        buy_dates, _ = zip(*buy_points)
        sell_dates, _ = zip(*sell_points)

        if not filter:
            return buy_dates, sell_dates

        # remove buy and sell actions that are not in Williams %R range
        buy_dates = [date for date in buy_dates if self.williams_r[date] < WILLIAMS_R_MIN]
        sell_dates = [date for date in sell_dates if self.williams_r[date] > WILLIAMS_R_MAX]

        # remove redundant dates (buy - buy - buy - sell - sell - sell => buy - sell - buy - sell)
        all_dates = sorted(buy_dates + sell_dates)
        buy = []
        sell = []
        last_date = datetime.min
        type = None
        for date in all_dates:
            if date in buy_dates and type in ['buy', None] and date > last_date:
                buy.append(date)
                last_date = date
                type = 'sell'
            elif date in sell_dates and type in ['sell', None] and date > last_date:
                sell.append(date)
                last_date = date
                type = 'buy'

        return buy, sell

    def plot_benefit(self, time_units: int = None):
        plt.figure(figsize=(10, 6))
        buy_dates, sell_dates = self.__get_buy_and_sell_dates(time_units)

        # Add the first date when we already had some shares
        if sell_dates[0] < buy_dates[0]:
            buy_dates = [self.dates[0]] + buy_dates

        # if sell_dates[0] < buy_dates[0]:
        #    sell_dates = sell_dates[1:]

        _, ax = plt.subplots(figsize=(10, 6))

        # Diagram of buy and sell actions
        for i, (buy_date, sell_date) in enumerate(zip(buy_dates, sell_dates)):
            buy_price = self.stock_history[buy_date]
            sell_price = self.stock_history[sell_date]

            color = 'g' if sell_price > buy_price else 'r'
            ax.bar(x=i, height=sell_price - buy_price, color=color, alpha=0.6)

        # Set X-axis ticks to be the buy_dates
        ax.set_xticks(np.arange(min(len(buy_dates), len(sell_dates))))
        ax.set_xticklabels([f"{buy.strftime('%d/%m')}-{sell.strftime('%d/%m/%Y')}" for buy, sell in zip(buy_dates, sell_dates)], rotation=60, ha='right')
        #ax.set_yscale('symlog', base=2, linthresh=0.01)

        plt.xlabel('Date')
        plt.ylabel('Benefit from one share, $')
        plt.title('Benefits with Buy and Sell Actions')
        plt.tight_layout()
        plt.show()

    def _print_state(self, shares: int, cash: float, date: datetime, title="Simulation"):
        print(title)
        print("Date:", date.date())
        print(f"Cash: {cash:.2f} $")
        print("Shares:", shares, " shares")
        print(f"Total: {cash + shares * self.stock_history[date]:.2f} $\n")

    def simulate_transactions(self, shares: int = 1, cash: float = 0, time_units: int = None, commission=0):
        if not time_units:
            time_units = len(self.dates)

        self._print_state(shares, cash, self.dates[-time_units])

        self._print_state(shares, cash, self.dates[-1], title="State without any actions")

        buy_dates, sell_dates = self.__get_buy_and_sell_dates(time_units)
        for date in sorted(buy_dates + sell_dates):
            price = self.stock_history[date]
            if date in buy_dates:
                shares_number = cash // (price * (1 + commission))
                cash -= shares_number * price * (1 + commission)
                shares += shares_number
            else:
                cash += shares * price * (1 - commission)
                shares = 0

        print("Number of actions:", len(buy_dates) + len(sell_dates))
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

    @property
    def williams_r(self):
        return self._williams_r
