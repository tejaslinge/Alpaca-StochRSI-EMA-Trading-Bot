### Signals 

import numpy as np
from config_params import *

def implement_stoch_strategy(ticker, upper_band = stoch_upper_band, lower_band = stoch_lower_band):    
    buy_price = []
    sell_price = []
    stoch_signal = []
    signal = 0

    prices = ticker['Close']
    k = ticker['Stoch %K']
    d = ticker['Stoch %D']

    for i in range(len(prices)):
        if k[i] < lower_band and d[i] < lower_band and k[i] < d[i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                stoch_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                stoch_signal.append(0)
        elif k[i] > upper_band and d[i] > upper_band and k[i] > d[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                stoch_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                stoch_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            stoch_signal.append(0)

    ticker['Stoch Signal'] = stoch_signal
#     print(stoch_signal)
    return ticker

def implement_ema_strategy(prices, period = ema_period):
    cols = list(prices.columns)
    ema = prices['Close'].ewm(span = period, adjust = False).mean()
    prices["EMA"] = ema
    prices['Signal_EMA'] = np.where(prices['EMA'] < prices['Close'], 1.0, 0.0)
    # prices['EMA Signal'] = prices['Signal_EMA'].diff()    
    prices['EMA Signal'] = prices['Signal_EMA']
    cols += ["EMA Signal"]
    return prices[cols]

def implement_stochRSI_strategy(ticker, upper_band = stochRSI_upper_band, lower_band = stochRSI_lower_band):
    buy_price = []
    sell_price = []
    stoch_signal = []
    signal = 0

    prices = ticker['Close']
    k = ticker['StochRSI_K']
    d = ticker['StochRSI_D']

    for i in range(len(prices)):
        if k[i] < lower_band and d[i] < lower_band and k[i] < d[i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                stoch_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                stoch_signal.append(0)
        elif k[i] > upper_band and d[i] > upper_band and k[i] > d[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                stoch_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                stoch_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            stoch_signal.append(0)

    ticker['Stoch RSI Signal'] = stoch_signal
    return ticker