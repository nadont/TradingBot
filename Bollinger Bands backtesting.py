import pandas as pd
from plots_f import plot_results

df = pd.read_csv('BTC_Jan2721_July0122_5min.csv')


def sma(data, window):
    return (data.rolling(window=window).mean())


def bollinger_band(data, sma, window, nstd):
    std = data.rolling(window=window).std()
    upper_band = sma + std * nstd
    lower_band = sma - std * nstd

    return upper_band, lower_band


symbols = ['BTC']

nstd = 3

#windows amd nstd can be adjust
for symbol in symbols:
    df[f'{symbol}_sma'] = sma(df[f'{symbol}-GBP_Open'], 20)
    df[f'{symbol}_upper_band'], df[f'{symbol}_lower_band'] = bollinger_band(df[f'{symbol}-GBP_Open'],
                                                                            df[f'{symbol}_sma'], 20, nstd)

df.dropna(inplace=True)


class TradingEnv:
    def __init__(self, balance_amount, balance_unit, trading_fee_multiplier):
        self.balance_amount = balance_amount
        self.balance_unit = balance_unit
        self.buys = []
        self.sells = []
        self.trading_fee_multiplier = trading_fee_multiplier

    def buy(self, symbol, buy_price, time):
        self.balance_amount = (self.balance_amount / buy_price) * self.trading_fee_multiplier
        self.balance_unit = symbol
        self.buys.append([symbol, time, buy_price])

    def sell(self, sell_price, time):
        self.balance_amount = self.balance_amount * sell_price * self.trading_fee_multiplier
        self.sells.append([self.balance_unit, time, sell_price])
        self.balance_unit = 'GBP'


# VIP level 0, paying fees with BNB = 0.075%
# Balance amount can be adjust
env = TradingEnv(balance_amount=100, balance_unit='GBP', trading_fee_multiplier=0.99925)

for i in range(len(df)):
    if env.balance_unit == 'GBP':
        for symbol in symbols:
            if df[f'{symbol}-GBP_Low'].iloc[i] < df[f'{symbol}_lower_band'].iloc[i]:  # buy signal
                env.buy(symbol, df[f'{symbol}_lower_band'].iloc[i], df['OpenTime'].iloc[i])
                break

    if env.balance_unit != 'GBP':
        if df[f'{env.balance_unit}-GBP_High'].iloc[i] > df[f'{env.balance_unit}_upper_band'].iloc[i]:  # sell signal
            env.sell(df[f'{env.balance_unit}_upper_band'].iloc[i], df['OpenTime'].iloc[i])

if env.balance_unit != 'GBP':
    env.sell(df[f'{env.balance_unit}-GBP_Close'].iloc[-1], df['OpenTime'].iloc[-1])

print(f'num buys: {len(env.buys)}')
print(f'num sells: {len(env.sells)}')
print(f'ending balance: {env.balance_amount} {env.balance_unit}')

plot_results(df, 'BTC', env.buys, env.sells)