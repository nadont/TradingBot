import pandas as pd
from binance.client import Client
from api_keys import api_key, secret_key
import time
from datetime import datetime
import plotly.graph_objects as go

client = Client(api_key, secret_key)

coins = ['BTC']

merge = False
for coin in coins:
    print(f'gathering {coin}...')
    start_str = 'Jan 27, 2021'
    end_str = 'July 01. 2022'

    klines = client.get_historical_klines(symbol = f'{coin}GBP',
                                          interval = client.KLINE_INTERVAL_15MINUTE,
                                          start_str = start_str,
                                          end_str = end_str)
    cols = ['OpenTime',
            f'{coin}-GBP_Open',
            f'{coin}-GBP_High',
            f'{coin}-GBP_Low',
            f'{coin}-GBP_Close',
            f'{coin}-GBP_volume',
            'CloseTime',
            f'{coin}-QuoteAssetVolume',
            f'{coin}-NumberOfTrades',
            f'{coin}-TBBAV',
            f'{coin}-TBQAV',
            f'{coin}-ignore']
    coin_df = pd.DataFrame(klines, columns = cols)
    if merge == True:
        all_coins_df = pd.merge(coin_df, all_coins_df, how = 'inner', on = ['OpenTime', 'CloseTime'])
    else:
        all_coins_df = coin_df
        merge = True

    time.sleep(60)
print('gathering completed')

all_coins_df['OpenTime'] = [datetime.fromtimestamp(ts / 1000) for ts in all_coins_df['OpenTime']]
all_coins_df['CloseTime'] = [datetime.fromtimestamp(ts / 1000) for ts in all_coins_df['CloseTime']]
print('Time stamp amended')

for j in all_coins_df.columns:
    if not 'Time' in j:
        all_coins_df[j] = all_coins_df[j].astype(float)
print('Data type amended to float')

fig = go.Figure(data = [go.Candlestick(x = all_coins_df['OpenTime'],
                open = all_coins_df['BTC-GBP_Open'],
                high = all_coins_df['BTC-GBP_High'],
                low = all_coins_df['BTC-GBP_Low'],
                close = all_coins_df['BTC-GBP_Close'])])

fig.update_layout(xaxis_rangeslider_visible = False)
fig.show()

all_coins_df.to_csv('BTC_Jan2721_July0122_15min.csv',index = False)