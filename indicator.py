#### indicator.py

import numpy as np
from config_params import *
import pandas as pd

############################################################
#TECHNICAL INDICATORS

# calculating Stoch RSI (gives the same values as TradingView)
# https://www.tradingview.com/wiki/Stochastic_RSI_(STOCH_RSI) 
# def stochRSI(data, k_window = stochRSI_k, d_window = stochRSI_d, window = stochRSI_length, rsi_window = stochRSI_rsi_length):
        
#     def computeRSI (data, rsi_window = rsi_window):
#         diff = data.diff(1).dropna()        # diff in one field(one day)
#         #this preservers dimensions off diff values
#         up_chg = 0 * diff
#         down_chg = 0 * diff
#         # up change is equal to the positive difference, otherwise equal to zero
#         up_chg[diff > 0] = diff[ diff>0 ]
#         # down change is equal to negative deifference, otherwise equal to zero
#         down_chg[diff < 0] = diff[ diff < 0 ]
#         # check pandas documentation for ewm
#         # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
#         # values are related to exponential decay
#         # we set com=time_window-1 so we get decay alpha=1/time_window
#         up_chg_avg   = up_chg.ewm(com=rsi_window-1 , min_periods=rsi_window).mean()
#         down_chg_avg = down_chg.ewm(com=rsi_window-1 , min_periods=rsi_window).mean()
#         rs = abs(up_chg_avg/down_chg_avg)
#         rsi = 100 - 100/(1+rs)
#         return rsi
    
#     data_temp = data['Close']
#     data_temp = computeRSI(data_temp, rsi_window)
    
#     # input to function is one column from df
#     # containing closing price or whatever value we want to extract K and D from
#     min_val  = data_temp.rolling(window=window, center=False).min()
#     max_val = data_temp.rolling(window=window, center=False).max()
#     stoch = ( (data_temp - min_val) / (max_val - min_val) ) * 100
#     K = stoch.rolling(window=k_window, center=False).mean() 
#     #K = stoch
#     D = K.rolling(window=d_window, center=False).mean() 
    
#     data['StochRSI_K'] = K
#     data['StochRSI_D'] = D
    
#     return data



# def stochastic(ticker, period = stoch_klength, smoothK = stoch_smoothk, smoothD = stoch_smoothd): ## verified
#     cols = list(ticker.columns)[1:]
#     ticker['14-high'] = ticker['High'].rolling(period).max()
#     ticker['14-low'] = ticker['Low'].rolling(period).min()
#     ticker['Stoch %K'] = ((ticker['Close'] - ticker['14-low'])*100/(ticker['14-high'] - ticker['14-low'])).rolling(smoothK).mean()
#     ticker['Stoch %D'] = ticker['Stoch %K'].rolling(smoothD).mean()
#     ticker.drop(columns = ['14-low', '14-high'], inplace = True)
#     return ticker

def stochastic(df, period = stoch_klength, smoothK = stoch_smoothk, smoothD = stoch_smoothd, stoch_lower_band = stoch_lower_band, stoch_upper_band = stoch_upper_band, TYPE = 'Stoch', period_stochRSI = stochRSI_length, stochRSI_lower_band = stochRSI_lower_band, stochRSI_upper_band = stochRSI_upper_band):
    if TYPE == 'Stoch':
        df_temp = df.copy()
        df_temp['n-High'] = df_temp['Close'].rolling(period).max()
        df_temp['n-Low'] = df_temp['Close'].rolling(period).min()
        df_temp['Stoch %K'] = (((df_temp['Close'] - df_temp['n-Low'])/(df_temp['n-High'] - df_temp['n-Low']))*100).rolling(smoothK).mean()
        df_temp['Stoch %D'] = df_temp['Stoch %K'].rolling(smoothD).mean()
        k = df_temp['Stoch %K']
        d = df_temp['Stoch %D']
        signals = []
        for i in range(len(k)):
            if k[i] > d[i] and k[i] > stoch_lower_band and k[i - 1] < stoch_lower_band:
                signals.append(1)
            else: signals.append(0)
        df_temp['Stoch Signal'] = signals
        df['Stoch Signal'] = df_temp['Stoch Signal'].diff()
        return df
    
    elif TYPE == 'StochRSI':
        period = period_stochRSI
        df_temp = df.copy()
        df_temp['n-High'] = df_temp['RSI'].rolling(period).max()
        df_temp['n-Low'] = df_temp['RSI'].rolling(period).min()
        df_temp['Stoch %K'] = (((df_temp['RSI'] - df_temp['n-Low'])/(df_temp['n-High'] - df_temp['n-Low']))*100).rolling(smoothK).mean()
        df_temp['Stoch %D'] = df_temp['Stoch %K'].rolling(smoothD).mean()
        k = df_temp['Stoch %K']
        d = df_temp['Stoch %D']
        signals = []
        for i in range(len(k)):
            # if k[i] > d[i] and k[i] > lower_band and k[i - 1] < lower_band:
            # if d[i] > lower_band and d[i] < upper_band:
            if k[i] > d[i] and k[i] < stochRSI_lower_band:
                signals.append(1)
    #         elif k[i] < d[i] and k[i] < lower_band:
            else: signals.append(0)
        df_temp['StochRSI Signal'] = signals
        df['StochRSI Signal'] = df_temp['StochRSI Signal']
        return df

def rsi(ohlc: pd.DataFrame, period: int = stochRSI_rsi_length) -> pd.Series:
    """See source https://github.com/peerchemist/finta
    and fix https://www.tradingview.com/wiki/Talk:Relative_Strength_Index_(RSI)
    Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements.
    RSI oscillates between zero and 100. Traditionally, and according to Wilder, RSI is considered overbought when above 70 and oversold when below 30.
    Signals can also be generated by looking for divergences, failure swings and centerline crossovers.
    RSI can also be used to identify the general trend."""
    delta = ohlc["Close"].diff()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    _gain = up.ewm(com=(period - 1), min_periods=period).mean()
    _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()
    RS = _gain / _loss
    RSI = 100 - (100 / (1 + RS))
    ohlc['RSI'] = RSI
    return ohlc

# def RSI(series, period=14): # ✔︎✔︎ RSI_EWM
#     delta = series.diff().dropna()
#     ups = delta * 0
#     downs = ups.copy()
#     ups[delta > 0] = delta[delta > 0]
#     downs[delta < 0] = -delta[delta < 0]
#     ups[ups.index[period-1]] = np.mean( ups[:period] ) #first value is sum of avg gains
#     ups = ups.drop(ups.index[:(period-1)])
#     downs[downs.index[period-1]] = np.mean( downs[:period] ) #first value is sum of avg losses
#     downs = downs.drop(downs.index[:(period-1)])
#     rs = ups.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() / \
#          downs.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() 
#     return 100 - 100 / (1 + rs)


# calculating Stoch RSI 
#  -- Same as the above function but uses EMA, not SMA
def StochRSI_EMA(series, period=14, smoothK=3, smoothD=3):
    # Calculate RSI 
    delta = series.diff().dropna()
    ups = delta * 0
    downs = ups.copy()
    ups[delta > 0] = delta[delta > 0]
    downs[delta < 0] = -delta[delta < 0]
    ups[ups.index[period-1]] = np.mean( ups[:period] ) #first value is sum of avg gains
    ups = ups.drop(ups.index[:(period-1)])
    downs[downs.index[period-1]] = np.mean( downs[:period] ) #first value is sum of avg losses
    downs = downs.drop(downs.index[:(period-1)])
    rs = ups.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() / \
         downs.ewm(com=period-1,min_periods=0,adjust=False,ignore_na=False).mean() 
    rsi = 100 - 100 / (1 + rs)

    # Calculate StochRSI 
    stochrsi  = (rsi - rsi.rolling(period).min()) / (rsi.rolling(period).max() - rsi.rolling(period).min())
    stochrsi_K = stochrsi.ewm(span=smoothK).mean()
    stochrsi_D = stochrsi_K.ewm(span=smoothD).mean()

    return stochrsi, stochrsi_K, stochrsi_D

# EMA Signal Generation
def implement_ema_strategy(prices, period = ema_period):
    cols = list(prices.columns)
    ema = prices['Close'].ewm(span = period, adjust = False).mean()
    prices["EMA"] = ema
    prices['Signal_EMA'] = np.where(prices['EMA'] < prices['Close'], 1.0, 0.0)
    # prices['EMA Signal'] = prices['Signal_EMA'].diff()    
    prices['EMA Signal'] = prices['Signal_EMA']
    cols += ["EMA Signal"]
    return prices[cols]

############################################################
