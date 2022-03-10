import pandas as pd
import numpy as np
import json

from datetime import datetime as dt
from datetime import timedelta
import time
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import alpaca_trade_api as alpaca
from indicator import *
from config_params import *

# Files
key = json.loads(open('AUTH/authAlpaca.txt', 'r').read())
api = alpaca.REST(key['APCA-API-KEY-ID'], key['APCA-API-SECRET-KEY'], base_url= key['BASE-URL'], api_version = 'v2')
tickers = open('AUTH/Tickers.txt', 'r').read() # Tickers
tickers = tickers.split()
# auth = json.loads(open('AUTH/authBinance.txt', 'r').read()) # API-KEY and API-SECRET
# client = Client(auth["API-KEY"], auth["API-SECRET"])

# Function to fetch data
# Change get_data to fetch data from Alpaca
def get_data(ticker, timeframe= timeframe, start_date = int(start_date), exchanges = exchange):
    df = api.get_crypto_bars(ticker, timeframe, (dt.now() - timedelta(days = start_date)).strftime("%Y-%m-%d"), dt.now().strftime("%Y-%m-%d"), exchanges = exchange).df
    df.reset_index(inplace = True)
    df = df[['timestamp', 'open', 'high', 'low', 'close']]
    df.columns = ['Timestamp', 'Open', 'High', 'Low', 'Close']
    return df

def check_params(tickers, run):
    """ETH BTC DOGE"""
    """BTC DOGE"""
    tickers_check = tickers

    # tickers_bought = []

    for ticker in tickers_check:
        print("Fetching Data for:", ticker)
        if run == False:
            break
        df = get_data(ticker)
        print(df.tail)

        if stoch == 'True' and stoch_rsi == 'False' and ema == 'False': # Stoch
            df = stochastic(df, TYPE = 'Stoch')
            print("Calculating Signals for Stoch")
            # df = implement_stoch_strategy(df, stoch_smoothk, stoch_smoothd)
            signal_list = list(df['Stoch Signal'].iloc[ -lookback_period : ])

            signal_count = 0
            for signal in signal_list:
                signal_count += 1
    #                             print(signal)
                if signal == 1:
                    mail_content = buy(ticker) # buy ticker
                    # tickers_bought.append(ticker)
                    mail_alert(mail_content, 0)
                    order_csv = pd.read_csv('ORDERS/Open Orders.csv')
                    open_positions = len(list(order_csv.index))
                    run = open_positions < max_trades
                    break
            if signal_count == lookback_period:
                print('No Buy Signal Found for Stoch')
            # print("signal != 1")        
                    
        elif stoch == 'False' and stoch_rsi == 'True' and ema == 'False': # StochRSI
            print("Calculating Signals for StochRSI")
            # df = stochRSI(df)
            # df = implement_stochRSI_strategy(df, stochRSI_length)
            df = rsi(df)
            df = stochastic(df, TYPE = 'StochRSI')

            signal_list = list(df['StochRSI Signal'].iloc[ -lookback_period : ])

            signal_count = 0
            for signal in signal_list:
                signal_count += 1
                # print(signal)
                if signal == 1:
    #                                 print('place buy order')
                    mail_content = buy(ticker)
                    # tickers_bought.append(ticker)
                    mail_alert(mail_content, 0)
                    order_csv = pd.read_csv('ORDERS/Open Orders.csv')
                    open_positions = len(list(order_csv.index))
                    run = open_positions < max_trades
                    break
            if signal_count == lookback_period:
                print('No Buy Signal Found for StochRSI')

        elif stoch == 'False' and stoch_rsi == 'False' and ema == 'True': # EMA
            ######
            print("Calculating Signals for EMA")
            df = implement_ema_strategy(df)

            signal_list = list(df['EMA Signal'].iloc[ -lookback_period : ])

            signal_count = 0

            for signal in signal_list:
                signal_count += 1
    #                             print(signal)
                if signal == 1:
                    # print('place buy order')
                    mail_content = buy(ticker)
                    # tickers_bought.append(ticker)
                    mail_alert(mail_content, 0)
                    order_csv = pd.read_csv('ORDERS/Open Orders.csv')
                    open_positions = len(list(order_csv.index))
                    run = open_positions < max_trades
                    break
            if signal_count == lookback_period:
                print('No Buy Signal found for EMA')

        elif stoch == 'True' and stoch_rsi == 'True' and ema == 'True': # All 3
            print("Calculating Signals for Stoch + StochRSI + EMA")
            df = stochastic(df, TYPE = 'Stochastic') 
            # df = implement_stoch_strategy(df, stoch_smoothk, stoch_smoothd)
            # df = stochRSI(df)
            
            df = rsi(df)
            df = stochastic(df, TYPE = 'StochRSI')
            # df = implement_stochRSI_strategy(df, stochRSI_length)
            # df = stochRSI(df)
            df = implement_ema_strategy(df)

            stoch_signal_list = list(df['Stoch Signal'].iloc[ -lookback_period : ])
            stochRSI_signal_list = list(df['StochRSI Signal'].iloc[ -lookback_period : ])
            ema_signal_list = list(df['EMA Signal'].iloc[ -lookback_period : ])

            trade_decision_list = []

            for signal in stoch_signal_list:
                if signal == 1:
                    trade_decision_list.append(signal)
                    break
            for signal in stochRSI_signal_list:
                if signal == 1:
                    trade_decision_list.append(signal)
                    break
            for signal in ema_signal_list:
                if signal == 1:
                    trade_decision_list.append(signal)
                    break

            if len(trade_decision_list) == 3:
                # buy ticker with amount %capital/trade  
                mail_content = buy(ticker)
                # tickers_bought.append(ticker)
                mail_alert(mail_content, 0)
                order_csv = pd.read_csv('ORDERS/Open Orders.csv')
                open_positions = len(list(order_csv.index))
                run = open_positions < max_trades
            # elif len(trade_decision_list) < 3:
            else:
                print('No Buy Signal Found for Stoch + StochRSI + EMA')
                continue


        elif stoch == 'True' and stoch_rsi == 'True' and ema == 'False': # Stoch + StochRSI
            print("Calculating Signals for Stoch + StochRSI")
            df = stochastic(df, TYPE = 'Stoch')
            # df = implement_stoch_strategy(df, stoch_smoothk, stoch_smoothd)

            # df = stochRSI(df)
            # df = implement_stochRSI_strategy(df, stochRSI_length)
            df = rsi(df)
            df = stochastic(df, TYPE = 'StochRSI')

            stoch_signal_list = list(df['Stoch Signal'].iloc[ -lookback_period : ])
            stochRSI_signal_list = list(df['StochRSI Signal'].iloc[ -lookback_period : ])

            trade_decision_list = []

            for signal in stoch_signal_list:
                if signal == 1:
                    trade_decision_list.append(signal)
                    break
            for signal in stochRSI_signal_list:
                if signal == 1:
                    trade_decision_list.append(signal)
                    break

            if len(trade_decision_list) == 2:
                mail_content = buy(ticker)
                # tickers_bought.append(ticker)
                mail_alert(mail_content, 0)
                order_csv = pd.read_csv('ORDERS/Open Orders.csv')
                open_positions = len(list(order_csv.index))
                run = open_positions < max_trades
            # elif len(trade_decision_list) < 3:
            else:
                print("No Buy Signal Found for Stoch + StochRSI")
                continue


        elif stoch_rsi == 'True' and ema == 'True' and stoch == 'False': # StochRSI + EMA
            print("Calculating Signals for StochRSI + EMA")
            # df = stochRSI(df)
            # df = implement_stochRSI_strategy(df, stochRSI_length)
            df = rsi(df)
            df = stochastic(df, TYPE = 'StochRSI')

            # df = stochRSI(df)
            df = implement_ema_strategy(df)

            stochRSI_signal_list = list(df['StochRSI Signal'].iloc[ -lookback_period : ])
            ema_signal_list = list(df['EMA Signal'].iloc[ -lookback_period : ])

            trade_decision_list = []

            for signal in stochRSI_signal_list:
                if signal == 1:
                    trade_decision_list.append(signal)
                    break
            for signal in ema_signal_list:
                if signal == 1:
                    trade_decision_list.append(signal)
                    break

            if len(trade_decision_list) == 2:
                mail_content = buy(ticker)
                # tickers_bought.append(ticker)
                mail_alert(mail_content, 0)
                order_csv = pd.read_csv('ORDERS/Open Orders.csv')
                open_positions = len(list(order_csv.index))
                run = open_positions < max_trades
            else:
                print('No Buy Signal Found for StochRSI + EMA')
                continue

                
        elif stoch_rsi == 'False' and ema == 'True' and stoch == 'True': # EMA + Stoch
            print("Calculating Signals for EMA + Stoch")
            df = stochastic(df, TYPE = "Stochastic")
            # df = implement_stoch_strategy(df, stoch_smoothk, stoch_smoothd)

            df = implement_ema_strategy(df)

            stoch_signal_list = list(df['Stoch Signal'].iloc[ -lookback_period : ])
            ema_signal_list = list(df['EMA Signal'].iloc[ -lookback_period : ])

            trade_decision_list = []

            for signal in stoch_signal_list:
                if signal == 1:
                    trade_decision_list.append(signal)
                    break
            for signal in ema_signal_list:
                if signal == 1:
                    trade_decision_list.append(signal)
                    break

            if len(trade_decision_list) == 2:
                mail_content = buy(ticker)
                # tickers_bought.append(ticker)
                mail_alert(mail_content, 0)
                order_csv = pd.read_csv('ORDERS/Open Orders.csv')
                open_positions = len(list(order_csv.index))
                run = open_positions < max_trades
            else:
                print('No Buy Signal Found for EMA + Stoch')
                continue

        else:
            print('Please select any 1 indicator by changing indicator setting to "True"')

def order_files(coin_to_buy, price_coin, highest_price, targetPositionSize, target_price, stop_loss_price, ActivateTrailingStopAt):
    # filesDone = 0
    # files = ['Orders', 'Open Orders', 'Time and Coins']
    
    if os.path.isfile('ORDERS/Orders.csv'):
#         print('Orders IFFF')
        df = pd.read_csv('ORDERS/Orders.csv')
#         df.drop(columns= 'Unnamed: 0', inplace = True)
        # df.loc[len(df.index)] = [dt.now().strftime("%Y-%m-%d %H:%M:%S"), coin_to_buy, 'buy',
        #                          price_coin, highest_price, targetPositionSize, targetPositionSize*price_coin, api.get_account().cash, target_price, stop_loss_price, ActivateTrailingStopAt] 
        df.loc[len(df.index)] = [dt.now().strftime("%Y-%m-%d %H:%M:%S"), coin_to_buy, 'buy',
                                 price_coin, '-', highest_price, targetPositionSize, targetPositionSize*price_coin, api.get_account().cash, target_price, stop_loss_price, ActivateTrailingStopAt]
        df.to_csv('ORDERS/Orders.csv', index = False)
        # filesDone += 1
        # files.remove('Orders')
    else:    
        # print('Orders ELSEEE')
        df = pd.DataFrame()
        df[['Time', 'Ticker', 'Type', 'Buy Price', 'Sell Price', 'Highest Price', 'Quantity', 'Total', 'Acc Balance', 'Target Price', 'Stop Loss Price', 'ActivateTrailingStopAt']] = ''
        df.loc[len(df.index)] = [dt.now().strftime("%Y-%m-%d %H:%M:%S"), coin_to_buy, 'buy',
                                 price_coin, '-', highest_price, targetPositionSize, targetPositionSize*price_coin, api.get_account().cash, target_price, stop_loss_price, ActivateTrailingStopAt]
        df.to_csv('ORDERS/Orders.csv', index = False)
        # filesDone += 1
        # files.remove('Orders')
        
        
    if os.path.isfile('ORDERS/Time and Coins.csv'):
        # print('Time AND COINS IFFF')
        df1 = pd.read_csv('ORDERS/Time and Coins.csv')
#         df.drop(columns= 'Unnamed: 0', inplace = True)
        df1.loc[len(df.index)] = [dt.now().strftime("%Y-%m-%d %H:%M:%S"), coin_to_buy]
        df1.to_csv('ORDERS/Time and Coins.csv', index = False)
        # filesDone += 1
        # files.remove('Time and Coins')
        
    else:    
        # print('Time AND COINS ELSEEE')
        df1 = pd.DataFrame()
        df1[['Time', 'Ticker']] = ''
        df1.loc[len(df.index)] = [dt.now().strftime("%Y-%m-%d %H:%M:%S"), coin_to_buy]
        df1.to_csv('ORDERS/Time and Coins.csv', index = False)
        # filesDone += 1
        # files.remove('Time and Coins')
        
    if os.path.isfile('ORDERS/Open Orders.csv'):
        # print('Open Orders IFFF')
        df2 = pd.read_csv('ORDERS/Open Orders.csv')
#         df.drop(columns= 'Unnamed: 0', inplace = True)
        df2.loc[len(df.index)] = [dt.now().strftime("%Y-%m-%d %H:%M:%S"), coin_to_buy, 'buy',
                                 price_coin, '-', highest_price, targetPositionSize, targetPositionSize*price_coin, api.get_account().cash, target_price, stop_loss_price, ActivateTrailingStopAt] 
        df2.to_csv('ORDERS/Open Orders.csv', index = False)
        # filesDone += 1
        # files.remove('Open Orders')
        
    else:    
        # print("Open Orders ELSEEE")
        df2 = pd.DataFrame()
        df2[['Time', 'Ticker', 'Type', 'Buy Price', 'Sell Price', 'Highest Price', 'Quantity', 'Total', 'Acc Balance', 'Target Price', 'Stop Loss Price', 'ActivateTrailingStopAt']] = ''
        df2.loc[len(df.index)] = [dt.now().strftime("%Y-%m-%d %H:%M:%S"), coin_to_buy, 'buy',
                                 price_coin, '-', highest_price, targetPositionSize, targetPositionSize*price_coin, api.get_account().cash, target_price, stop_loss_price, ActivateTrailingStopAt]
        df2.to_csv('ORDERS/Open Orders.csv', index = False)
        # filesDone += 1
        # files.remove('Open Orders')
        
    # if filesDone == 3:
    #     return "All Order Files Done"
    # else: 
    #     return 'File(s) not Done: {}'.format(files)

def buy(coin_to_buy: str, trade_cap_percent = trade_capital_percent):
#     cashBalance = api.get_account().cash
    cashToUse = investment_amount
    buy_amount = cashToUse * (trade_cap_percent * 0.01)
    price_coin = api.get_latest_crypto_trade(coin_to_buy, exchange= 'CBSE').p
    targetPositionSize = ((float(buy_amount)) / (price_coin)) # Calculates required position size
    print(coin_to_buy, targetPositionSize)
    api.submit_order(str(coin_to_buy), targetPositionSize, "buy", "market", "day") # Market order to open position    
    mail_content = '''TRADE ALERT: BUY Order Placed for {} {} at ${}'''.format(targetPositionSize, coin_to_buy, price_coin)
    stop_loss_price = price_coin * (1- (stop_loss*0.01))
    ActivateTrailingStopAt = price_coin * (1+ (activate_trailing_stop_loss_at * 0.01))
    target_price = price_coin * (1 + (limit_price * 0.01))
    highest_price = price_coin
    print(mail_content)
    
    order_files(coin_to_buy, price_coin, highest_price, targetPositionSize, target_price, stop_loss_price, ActivateTrailingStopAt)

    return mail_content

def sell(current_coin, quantity, buy_price, highest_price):
    # sells current_stock
#     quantity = float(api.get_position(str(current_coin)).qty)    
    sell_price = api.get_latest_crypto_trade(str(current_coin), 'CBSE').price
#     api.cancel_all_orders() # cancels all pending (to be filled) orders 
    
    api.submit_order(current_coin, quantity, 'sell', 'market', 'day')
    mail_content = '''TRADE ALERT: SELL Order Placed for {} {} at ${}'''.format(quantity, current_coin, sell_price)
    df = pd.read_csv('ORDERS/Orders.csv')
# ['Time', 'Ticker', 'Type', 'Buy Price', 'Sell Price', 'Highest Price', 'Quantity', 'Total', 'Acc Balance', 'Target Price', 'Stop Loss Price', 'ActivateTrailingStopAt']
    df.loc[len(df.index)] = [dt.now().strftime("%Y-%m-%d %H:%M:%S"), current_coin, 'sell',
                             buy_price, sell_price, highest_price, quantity, quantity*sell_price, api.get_account().cash, '-', '-', '-']
        
    df.to_csv('ORDERS/Orders.csv', index = False)    
    return mail_content


def mail_alert(mail_content, sleep_time):
    # The mail addresses and password
    sender_address = 'sender_address'
    sender_pass = 'sender_pass'
    receiver_address = 'tejas.linge101@gmail.com'

    # Setup MIME
    message = MIMEMultipart()
    message['From'] = 'Trading Bot'
    message['To'] = receiver_address
    message['Subject'] = 'Technical Trading Bot'
    
    # The body and the attachments for the mail
    message.attach(MIMEText(mail_content, 'plain'))

    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security

    # login with mail_id and password
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    time.sleep(sleep_time)

# global open_positions
open_positions = len(api.list_positions())

def mainNEW(open_positions):

        tickers_bought = []
        mail_alert("The Bot Started Running on {} at {}".format(dt.now().strftime("%Y-%m-%d"), dt.now().strftime("%H:%M:%S")), 0)
        try:
            while True:

                # Checking Returns every time loop runs
                if os.path.isfile('ORDERS/Open Orders.csv'):
                    print('Checking Returns')
                    df = pd.read_csv('ORDERS/Open Orders.csv')
                    for i in list(df.index):
                        ticker = df.loc[i, 'Ticker']
                        quantity = df.loc[i, 'Quantity']
    #                     stop_loss_price_temp = df.loc[i, 'Stop Loss Price']
                        curr_price = api.get_latest_crypto_trade(ticker, exchange).p
                        trailingStopActivatePrice = df.loc[i, 'ActivateTrailingStopAt']
                        target_price = df.loc[i, 'Target Price']
                        highest_price_since_buy = df.loc[i, 'Highest Price']
                        buy_price = df.loc[i, 'Buy Price']

                        if (curr_price >= trailingStopActivatePrice) and (curr_price > highest_price_since_buy):
                            new_stop_loss = curr_price*(1- (trailing_stop * 0.01))
                            df.loc[i, 'Stop Loss Price'] = new_stop_loss
                            df.loc[i, 'Highest Price'] = curr_price

                        lower_limit_price = df.loc[i, 'Stop Loss Price']

                        # print('''Checking Returns For: {}
                        # Quantity: {}, Target: {}, Current: {}, Stop: {}, HighestSinceBuy: {}

                        # '''.format(ticker, quantity, target_price, curr_price, highest_price_since_buy, lower_limit_price))                        

                        if (curr_price <= lower_limit_price) or (curr_price >= target_price):
                            mail_content = sell(ticker, quantity, buy_price, highest_price_since_buy)
                            mail_alert(mail_content, 0)
                            df.drop(index = i, inplace = True)
                        else:
                            continue

                    df.to_csv('ORDERS/Open Orders.csv', index = False)

                    print("Returns Checked")

                else: print("No Open Positions, Generating Signals")

                if len(api.list_positions()) > 0:
                    if os.path.isfile('ORDERS/Open Orders.csv'):
                        order_csv = pd.read_csv('ORDERS/Open Orders.csv')
                        open_positions = len(list(order_csv.index))
                    else:
                        open_positions = 0
                else: open_positions = 0

                print("Open_Positions < Max_Trades", open_positions < max_trades)
                print("Open Positions:", open_positions)
                print("Max Trades:", max_trades) 

                if open_positions < max_trades:
                    run = True

                    tickers_check = [ticker for ticker in tickers if ticker not in tickers_bought]

                    ### keep this line??? Necessary to return tickers_bought from check_params??
                    # tickers_bought = check_params(tickers_check, run)
                    print("Checking Params for {}".format(tickers_check))
                    check_params(tickers_check, run)

                    # if len(tickers_bought) == 0:
                    #     time.sleep(20)
                    if os.path.isfile('ORDERS/Time and Coins.csv'):
                        coin_bought_df = pd.read_csv('ORDERS/Time and Coins.csv')
                        # checking if time since order placed < wait_time 
                        tickers_bought = list(coin_bought_df['Ticker'])
                        if len(tickers_bought) != 0:
                            for index in range(len(tickers_bought)):
                                # coin = coin_bought_df['Ticker'][index]
                                prev_time = coin_bought_df['Time'][index]

                                if (dt.now() - dt.strptime(prev_time, "%Y-%m-%d %H:%M:%S")).seconds < sleep_time:
                                    pass
                                else:
                                    try:
                                        # print(tickers_bought)
                                        tickers_bought.pop(index)
                                        coin_bought_df.drop(index = index, inplace = True)
                                    except Exception as e:
                                        print(e)
                            coin_bought_df.to_csv('ORDERS/Time and Coins.csv', index = False)
                        else:
                            # Sleep if len(tickers_bought) (inside wait_time_betn_trades) = 0
                            print("Sleeping bcause No Tickers Bought inside wait_time_betn_trades")
                            time.sleep(20)

                    else: 
                        print("Sleeping bcause No Time and Coins File")
                        time.sleep(20)

                                # remove coin index from coin_bough_df
                        # pass


                    """
                    read time_at_which_ticker_was_bought_file: TICKER, TIME
                    prev_time =
                    curr_time = dt.now()
                    if currr_time - prev_time <= time_betn_trades:
                        tickers_check.pop(file index (ticker columns))
                    """


    #             [['Time', 'Ticker', 'Type', 'Price', 'Quantity', 'Total', 'Acc Balance', '', '', '']] 
                    # time.sleep(30)

                    # else: time.sleep(30)
                # print("Exited Returns Check")
                # print("Sleeping for {} secs".format(sleep_time))
                # time.sleep(10)
        except Exception as e:
            print(e)
            mail_alert("The Bot Stopped Running on {} at {}".format(dt.now().strftime("%Y-%m-%d"), dt.now().strftime("%H:%M:%S")), 0)
            
if __name__ == "__main__":
    mainNEW(open_positions)
