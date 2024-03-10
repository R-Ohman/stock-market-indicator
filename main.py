from smi import StockMarketIndicator


def main():
    N = 1000
    smi = StockMarketIndicator('data/apple_d.csv')
    smi.plot(title="Apple", time_units=N)
    smi.plot_macd(time_units=N, title="Apple MACD")
    smi.plot(time_units=N, y=list(smi.williams_r.values()), y_label="Williams %R", title="Apple Williams %R")
    smi.plot_benefit(time_units=N)
    smi.simulate_transactions(shares=10, cash=0, time_units=N)


if __name__ == '__main__':
    main()
