# Technical-Trading-Bot
Trading Bot built using the Alpaca API in Python. Indicators used for Signal Generation: EMA, StochRSI, and Stochastic Oscillator

## AUTH

1. configFile.txt: To enable/disable the indicators for which the bot will check and generate buy/sell signals. Other parameters such as:
- Trade Params: % Capital to be used / trade, Stop Loss, Trailing Stop, Limit Price, etc can be changed.
- Data Params: Timeframe, Start Date, End Date
- Indicator Params: Indicator parameters can also be changed in the ConfigFile.txt. 
    1. StochRSI: Lower Band, Upper Band, K, D, RSI Length, etc)
    2. Stoch: Lower Band, Upper Band, K Smoothing, D Smoothing
    3. EMA: Period, Smoothing

2. prjve
