import os
import schedule

import numpy as np
import pandas as pd
pd.set_option('display.max_rows', None)

import warnings
warnings.filterwarnings('ignore')

import datetime
from datetime import timedelta
import time

import os, sys

# accommodate test loop using each indicator separate from database and the project's directory/import structure, look to the if __name__ == '__main__' conditional below
basepath = os.path.dirname(os.path.abspath(__file__))

try:
    from indicators.utils.indicaids import crossover, crossunder, plot, color, shape, play_enter, play_exit
    from indicators.utils.beep import buy, sell, say

except:
    if __name__ != "__main__":
        print(sys.path)
    else:
        print(basepath)
        print(__file__)
        print(__name__)
        from utils.indicaids import crossover, crossunder, plot, color, shape, play_enter, play_exit


def supertrend(df, period=7, atr_multiplier=3):
    df['upperband'] = df['hl2'] + (atr_multiplier * df['atr'])
    df['lowerband'] = df['hl2'] - (atr_multiplier * df['atr'])
    df['in_uptrend'] = True

    for current in range(1, len(df.index)):
        previous = current - 1

        if df['close'][current] > df['upperband'][previous]:
            df['in_uptrend'][current] = True
        elif df['close'][current] < df['lowerband'][previous]:
            df['in_uptrend'][current] = False
        else:
            df['in_uptrend'][current] = df['in_uptrend'][previous]

            if df['in_uptrend'][current] and df['lowerband'][current] < df['lowerband'][previous]:
                df['lowerband'][current] = df['lowerband'][previous]

            if not df['in_uptrend'][current] and df['upperband'][current] > df['upperband'][previous]:
                df['upperband'][current] = df['upperband'][previous]

    return df




# # TODO: Stack re. in_position, Buy, Sell, Account, Balances, etc
# we need to ask orders if the position is in... but we need the symbol name, just as the test loop when run as __main__ requires to obtain a df
in_position = False

def check_buy_sell_signals(df): #, ticker):
    global in_position # TODO: ???context???
    # ticker = ticker['cxt']
    print("checking for buy and sell signals")

    last_row_index = len(df.index) - 1
    previous_row_index = last_row_index - 1

    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        print(color.green, " changed to uptrend, buy")
        buy()
        # print('\a')
        play_enter()
        if not in_position:
            # order = ticker
            # order = exchange.create_market_buy_order(ticker, 0.05)
            # print(order)
            in_position = True
            df['in_pos'] = color.green
        else:
            print("already in position, nothing to do")

    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        print(color.red, " changed to downtrend, sell")
        sell()
        # print('\a')
        play_exit()
        if in_position:
            # order = ticker
            # order = exchange.create_market_sell_order(ticker, 0.05)
            # print(order)
            in_position = False
            df['in_pos'] = color.red
        else:
            print("You aren't in position, nothing to sell")
    
    # df['in_pos'] = color.red if not in_position else color.green


def run(df): #ticker=None):
    in_position = False
    # TODO: get run params
    # o = df.copy().tail(2)
    df['in_pos'] = color.red if not in_position else color.green
    supertrend_data = supertrend(df)
    check_buy_sell_signals(supertrend_data)#, ticker)
    # print("available data series: \n" , supertrend_data.columns.tolist())
    #  ['date', 'open', 'high', 'low', 'close', 'hl2', 'hlc3', 'ohlc4', 'volume', 'previous_close', 'high-low', 'high-pc', 'low-pc', 'tr', 'atr', 'in_pos', 'upperband', 'lowerband', 'in_uptrend']

    # print(supertrend_data.tail(5))
    # df.iloc[:, [0] + list(range(2,5))]
    # df.iloc[:, np.r_[1:10, 15, 17, 50:100]] #15  
    
    # print(supertrend_data.loc[:,'in_pos': 'in_uptrend'].tail(5))
    #TODO: return actionable data
    # print("original df:")
    # print(o)

    # print(supertrend_data.iloc[:, np.r_[0, 4, 9, 18]].tail(5))
    return supertrend_data

if __name__ == "__main__":
    # https://stackoverflow.com/questions/714063/importing-modules-from-parent-folder
    import os, sys
    from pathlib import Path


    # for i, p in enumerate(Path(__file__).parents):
    #     print(i, " ", p)

    p = os.path.join(Path(__file__).parents[1])
    sys.path.insert(1, p)
    print("New Path: ", p)

    print(sys.path)
    from database import sql_to_df, list_tables
    from utils.atr import atr
    from macdraw import run as macdraw

    tables = list_tables()

    for table in tables:
        # print(table)
        if "link" in table[1]:
            testsymbol = table[1]
            print(testsymbol)

    # get a dataframe
    # testsymbol = 'LINKBULL/USDT' #TODO: remember, looking up a symbol doesn't work, you need the table name, which is one of today's jobs... you're slacking --- req's a table structure... so, the thought to look again at sqlite schema_table, and whether it has or can be made to have the necessary metadata describing the timeseries tables such that a join can be made... otherwise, given the naming convention, the name of the table could be parsed... or a dictionary could be made and tabled at the right moment, capturing the table name, linking it to exchange.symbol.interval and each of their names and ids via said lookup table...
    df = sql_to_df(testsymbol)
    df = df.filter(['date', 'open', 'high', 'low', 'close', 'hl2', 'hlc3', 'ohlc4', 'volume'])
    frame = atr(df, period=7, atr_multiplier=3)
    frame = macdraw(frame)
    # print(df)
    run(frame)

    # will not run 
    # schedule.every(1).minutes.do(run)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

