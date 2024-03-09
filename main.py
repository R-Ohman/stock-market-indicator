from smi import StockMarketIndicator


def main():
    N = 1000
    smi = StockMarketIndicator('data/microsoft.csv')
    smi.plot(title="Microsoft", time_units=N)
    smi.plot_macd(time_units=N, title="Microsoft MACD")
    smi.plot_benefit(time_units=N)
    smi.simulate_transactions(shares=10, cash=0, time_units=N)


if __name__ == '__main__':
    main()
