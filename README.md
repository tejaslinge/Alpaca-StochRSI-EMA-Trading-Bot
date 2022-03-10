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

2. Tickers.txt: Add ticker symbols (seperated by space) to check the critera for
3. authAlpaca.txt: Add Alpaca API Key and Secret Key for the bot to start trading. Change *"BASE-URL"* to *"api.alpaca.markets"* to trade in real-time markets.

## Root Dir

1. config_params.py: Initializes all the params set by the user in ConfigFile.txt
2. indicator.py: Calculates values and generates signals for all the indicators enabled by the user
