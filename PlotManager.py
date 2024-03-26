import numpy as np
from matplotlib import pyplot as plt

from smi import WILLIAMS_R_MIN, WILLIAMS_R_MAX


class PlotManager:
    def __init__(self, smi):
        self.smi = smi

    def plot(self, y=None, x_label="Date", y_label="Close, $", title=None, time_units: int = None):
        try:
            x = self.smi.dates[-time_units:] if time_units else self.smi.dates
            if y:
                y = y[-time_units:] if time_units else y
            else:
                y = self.smi.values[-time_units:] if time_units else self.smi.values

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
            williams_values = list(self.smi.williams_r.values())
            plt.plot(self.smi.dates[-len(williams_values):], williams_values)

            # Add horizontal lines
            plt.axhline(y=WILLIAMS_R_MIN, color='g', linestyle='--', label=f'Oversold')
            plt.axhline(y=WILLIAMS_R_MAX, color='r', linestyle='--', label=f'Overbought')

            for is_filtered in [False, True]:
                # Get buy and sell dates
                buy_dates, sell_dates = self.smi.get_buy_and_sell_dates(is_filtered=is_filtered)
                size = 150 if is_filtered else 20
                label_buy = 'Buy' if is_filtered else 'Buy (MACD)'
                label_sell = 'Sell' if is_filtered else 'Sell (MACD)'

                # Plot buy and sell points
                plt.scatter(buy_dates, [self.smi.williams_r[date] for date in buy_dates],
                            color='g', label=label_buy, s=size, marker='^')
                plt.scatter(sell_dates, [self.smi.williams_r[date] for date in sell_dates],
                            color='r', label=label_sell, s=size, marker='v')

            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.legend()
            plt.show()
        except ValueError:
            print(f"Error: Data length is less than {len(self.smi.williams_r)}")

    def plot_with_buy_and_sell(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.smi.dates, self.smi.values)
        buy_dates, sell_dates = self.smi.get_buy_and_sell_dates()
        plt.scatter(buy_dates, [self.smi.stock_history[date] for date in buy_dates],
                    color='g', label='Buy', s=150, marker='^')
        plt.scatter(sell_dates, [self.smi.stock_history[date] for date in sell_dates],
                    color='r', label='Sell', s=150, marker='v')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.legend()
        plt.show()

    def plot_benefit(self, time_units: int = None):
        plt.figure(figsize=(10, 6))
        buy_dates, sell_dates = self.smi.get_buy_and_sell_dates(time_units)

        # Add the first date when we already had some shares
        if sell_dates and buy_dates and sell_dates[0] < buy_dates[0]:
            buy_dates = [self.smi.dates[0]] + buy_dates

        # if sell_dates[0] < buy_dates[0]:
        #    sell_dates = sell_dates[1:]

        _, ax = plt.subplots(figsize=(10, 6))

        # Diagram of buy and sell actions
        for i, (buy_date, sell_date) in enumerate(zip(buy_dates, sell_dates)):
            buy_price = self.smi.stock_history[buy_date]
            sell_price = self.smi.stock_history[sell_date]

            color = 'g' if sell_price > buy_price else 'r'
            ax.bar(x=i, height=sell_price - buy_price, color=color, alpha=0.6)

        # Set X-axis ticks to be the buy_dates
        ax.set_xticks(np.arange(min(len(buy_dates), len(sell_dates))))
        ax.set_xticklabels([f"{buy.strftime('%d/%m/%Y')}-{sell.strftime('%d/%m/%Y')}"
                            for buy, sell in zip(buy_dates, sell_dates)], rotation=60, ha='right')
        # ax.set_yscale('symlog', base=2, linthresh=0.01)

        plt.xlabel('Date')
        plt.ylabel('Benefit from one share, $')
        plt.title('Benefits with Buy and Sell Actions')
        plt.tight_layout()
        plt.show()

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
            x = self.smi.dates[-n:]
            y1 = y1[-n:]
            y2 = y2[-n:]

            plt.plot(x, y1, label=label1)
            plt.plot(x, y2, label=label2)

            # Plot intersection points
            buy_points, sell_points = self.smi.get_intersection_points(x, y1, y2, n)
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
        self._double_plot_with_intersections(self.smi.macd, self.smi.signal, time_units, title=title)
