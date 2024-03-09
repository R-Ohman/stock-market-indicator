from smi import StockMarketIndicator


def main():
    N = 1000
    smi = StockMarketIndicator('data/microsoft.csv')
    smi.plot(title="Microsoft", n=N)
    smi.plot_macd(n=N, title="Microsoft MACD")
    smi.plot_benefit(n=N)


if __name__ == '__main__':
    main()
