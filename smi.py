import csv
from datetime import datetime


WILLIAMS_R_MIN = -70
WILLIAMS_R_MAX = -30


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

    def get_buy_and_sell_dates(self, n: int = None, is_filtered=True):
        n = n if n else min(len(self.macd), len(self.signal))
        dates = self.dates[-len(self.macd):]
        buy_points, sell_points = self.get_intersection_points(dates, self.macd, self.signal, n)
        buy_dates, _ = zip(*buy_points)
        sell_dates, _ = zip(*sell_points)

        if not is_filtered:
            return buy_dates, sell_dates

        # remove buy and sell actions that are not in Williams %R range
        buy_dates = [date for date in buy_dates if self.williams_r[date] < WILLIAMS_R_MIN]
        sell_dates = [date for date in sell_dates if self.williams_r[date] > WILLIAMS_R_MAX]

        # remove redundant dates (buy - buy - buy - sell - sell - sell => buy - sell - buy - sell)
        all_dates = sorted(buy_dates + sell_dates)
        buy = []
        sell = []
        last_date = datetime.min
        action_type = None
        for date in all_dates:
            if date in buy_dates and action_type in ['buy', None] and date > last_date:
                buy.append(date)
                last_date = date
                action_type = 'sell'
            elif date in sell_dates and action_type in ['sell', None] and date > last_date:
                sell.append(date)
                last_date = date
                action_type = 'buy'

        return buy, sell

    def _print_state(self, shares: int, cash: float, date: datetime, title="Simulation"):
        print(title)
        print("Date:", date.date())
        print(f"Cash: {cash:.2f} $")
        print("Shares:", shares, " shares")
        print(f"Total: {cash + shares * self.stock_history[date]:.2f} $\n")

    def simulate_transactions(self, shares: int = 1, cash: float = 0, time_units: int = None, commission=0, csv_file=None):
        if not time_units:
            time_units = len(self.dates)

        self._print_state(shares, cash, self.dates[-time_units])

        self._print_state(shares, cash, self.dates[-1], title="State without any actions")

        operations = []
        buy_dates, sell_dates = self.get_buy_and_sell_dates(time_units)
        for date in sorted(buy_dates + sell_dates):
            price = self.stock_history[date]
            if date in buy_dates:
                shares_number = cash // (price * (1 + commission))
                cash -= shares_number * price * (1 + commission)
                shares += shares_number
                operation = 'buy'
            else:
                shares_number = shares
                cash += shares * price * (1 - commission)
                shares = 0
                operation = 'sell'

            if csv_file and shares_number:
                operations.append({
                    'Date': date.date(),
                    'Operation': operation,
                    'SharesNumber': int(shares_number),
                    'Price': f"{price:.2f}",
                    'TotalCash': f"{cash:.2f}",
                    'TotalShares': int(shares),
                })

        print("Number of actions:", len(buy_dates) + len(sell_dates))
        self._print_state(shares, cash, self.dates[-1], title="State after simulation")

        if csv_file and operations:
            self.save_to_csv(csv_file, operations)

    @staticmethod
    def save_to_csv(path: str, data: list[dict[str, any]]):
        field_names = data[0].keys()
        with open(path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

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
