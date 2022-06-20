import os, sys
import numpy as np
import pandas as pd
import datetime

import math
from math import fmod

import ccxt
from poloniex import Poloniex

import pprint

from indicators.utils.sincer_checkpoint import sincemaker, slices,valid_interval_list

from database import check_table_exists, get_conn

basepath = os.path.dirname(os.path.abspath(__file__))
pp = pprint.pprint

# https://pandas.pydata.org/pandas-docs/stable/user_guide/options.html
pd.set_option("display.max_rows", 125)
pd.set_option("precision", 10)
# pd.set_option(io.excel.xls.writer, 'xlwt')


def symbol_standardize(symbol):
    try:
        # find separator, determine exchange
        sep = '/' in symbol
        if sep:
            # split and reassemble two parts of symbol
            symlist = symbol.split('/')
            # print(f"{symlist = }")
            base = symlist[1]
            quote = symlist[0]
            symbol = f"{base}_{quote}"
        # return symbol.replace("_", "/") if is_ccxt else symbol.replace("/", "_")
        return symbol
    except Exception as e:
        print(e)
        return None

def table_namer(symbol: str, interval: int, stack: list = None, init=None) -> str:
    # valid ccxt - "EOS/BTC" # symbols sent with
    # valid polo - "USDT_LINKBULL"
    # FORMAT
    # TABLE NAME FORMAT LIMITS
    max_sym = 12
    max_inval = 5 

    # Shims
    diff_sym = '_' * abs(max_sym - len(symbol))
    diff_inval: int = '_' * abs(max_inval - len(str(interval)))
    
    if stack:
        t_i_name: str = f"{symbol}{diff_sym}{interval}{diff_inval}{stack}".lower()
        # t_i_name: str = f"{t_name}{diff_inval}{stack}".upper()
        # print(t_i_name)
        return t_i_name
    else:
        t_name: str = f"{symbol}{diff_sym}{interval}".lower()
        # print(t_name)
        return t_name

def make_jobspec(symbols, interval=None, stack=None, init=None):
    import decimal
    from decimal import Decimal as D
    print('decimal.getcontext() ', decimal.getcontext())
    in_position: bool = False
    precision: int = 10

    # slice = interval = timeframe = period = '5m'
    # is_ccxt = True # TODO: kick off the right fetch exchange based on this boolean

    timeframes = {'5m': 300, '15m': 900, '30m': 1800, '2h': 7200, '4h': 14400, '1d': 86400}

    

    # if more than one symbol, should it be put into an async job queue from this point, or should the list of closures be called upon from a repository of same, to then be jobbed out/exec?

    for symbol in symbols:
        tablename = table_namer(symbol.replace("/", "_"), interval, stack)
        interval = timeframes.get(interval, 300) # convert from tablename dependent type,,, and is this a broken thing, probably 'yes', as the mutation is inline and not captured anywhere it won't need to be intervened upon procedurally, as an embedded dependency that can't be abstracted and changed at will without having to mess with program flow, so FIXME: FIXME: FIXME:
        start, end = slices(interval)
        init = check_table_exists(tablename)
        symbol = symbol_standardize(symbol)
        jobspec = {"interval": interval, "symbol": symbol, "start": start, "end": end, "tablename": tablename, "stack": stack, "init": init}
    print(f'{jobspec = }')
    return jobspec 

def fetch_ohlcv(jobspec):
    """Poloniex native api endpoint for OHLCV is preferred due to CCXT unified calls, due to missing data caused by confusion of the variable since """
    # TODO: also include the ccxt alias for native exchange api endpoint, and its associated params dict

    # # exchange = get_exchange()
    # # polo = Poloniex()

    # # slice = jobspec['slice'] # TODO: determine this earlier in a supporting :class

    # interval = 5 #TODO: must pass interval

    # start, end = slices(slice) # jobspec['start']
    start = jobspec['start']
    end = jobspec['end']
    interval = jobspec['interval']

    print(f"Fetching new bars for {datetime.datetime.now().isoformat()}")

    from api.polo import return_chart_data
    
    # from orders.kraken import return_ohlcv_data

    ## ---- Private/Public API (Poloniex)
    #{'date': 1640030400, 'high': 6.817e-05, 'low': 6.817e-05, 'open': 6.817e-05, 'close': 6.817e-05, 'volume': 0.00182126, 'quoteVolume': 26.71648132, 'weightedAverage': 6.817e-05}
    try:
        # data = polo.returnChartData(jobspec['symbol'], period=slice, start=start, end=end)
        data = return_chart_data(symbol=jobspec['symbol'], start=start, end=end, interval=jobspec['interval'])[0]
    except Exception as e:
        print(e)     
    except PoloniexCommandException as e:
        print(e)
        return None
    # without columns, below, added to df, it mangles the natural ordering to this: # cols = ['close', 'date', 'high', 'low', 'open', 'quoteVolume', 'volume', 'weightedAverage']
    columns=['date', 'high', 'low', 'open', 'close', 'volume', 'quoteVolume', 'weightedAverage']
    df = pd.DataFrame(data, columns=columns)
    # df = df.sort_values(by=['date']) # not tested, if rows are disordered
    cols = df.columns.to_list()
    # print(cols)

    # convert back to human time
    df['date'] = pd.to_datetime(df['date'], unit='s')
    # https://stackoverflow.com/questions/20225110/comparing-two-dataframes-and-getting-the-differences
    # FIXME: # mutating the df within a for loop? will the index flex around the deletion, alternatively is there a better method?

    # clean dirty data from df prior to sql processing
    # minutes
    _index_ = df.index
    dirty_min = []
    mod = int(interval / 60)
    valid_min = valid_interval_list(clock_len=60, interval=mod) # FIXME: interval doesn't work here, the list is invalid unless the mod is present
    print(f"{valid_min = }")
    for i, x in df.iterrows():
        dirty_min.append(True if x.date.minute not in valid_min else False)
    # print(_dirty_min)
    m_flagged = list(zip(_index_, dirty_min))
    for i, x in m_flagged:
        if x:
            try:
                print(f"the row by minute at index {i} {df.iloc[i, 0]} has been deleted")              
                df.drop(index=i, axis=0, inplace=True) 
            except IndexError as e:
                print(e)

    # seconds
    _index_ = df.index
    valid_second = valid_interval_list(clock_len = 60, interval = 60)
    print(f"{valid_second = }")
    dirty_second = (df['date'].dt.second != 0).to_list() # dirty seconds
    s_flagged = list(zip(_index_, dirty_second))
    # zip them together, check
    # print(f"returned -> start: {df.iloc[0, 0]} to end: {df.iloc[-1, 0]}")
    for i, x in s_flagged:
        if x:
            try:              
                print(f"the row by second at index {i} {df.iloc[i, 0]} has been deleted") 
                df.drop(index=i, axis=0, inplace=True) # mutating the df within a for loop? will the index flex around the deletion, alternatively is there a better method?
            except IndexError as e:
                print(e)

    # add some calcualted series/columns
    df['hl2'] = (df['high'] + df['low']) / 2
    df['hlc3'] = (df['high'] + df['low'] + df['close']) / 3
    df['ohlc4'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4


    from database import df_ohlcv_to_sql #.create_ohlcv_tables
    cols = df.columns.tolist()
    cols = tuple(cols)
    # print(f"{cols = }")

    set_the_table = df_ohlcv_to_sql(df, cols, jobspec)
    print(f"{set_the_table = }")

    # try:
    #     # set_the_table = 
    #     df_ohlcv_to_sql(df, cols, jobspec)
    # except Exception as e:
    #     print(e)
    #     df_ohlcv_to_sql(df, cols, jobspec)
    # finally:
    #     # print(f"{set_the_table = }")
    #     print(f"{jobspec = }")

if __name__ == '__main__':
    
    # symbol list
    symbols = ['LINKBULL/USDT', 'BTC_USDT', 'EOS/BTC', 'TRX_USDT', 'XRP/USDT', 'ETH/USDT']
    # TEST CASES
    # make_jobspec(['EOS_BTC'])
    # make_jobspec(['EOS/BTC'])
    # # make_jobspec(['EOSBTC'])
    
    for symbol in symbols:
        """Uncomment to initialize tables""" # TODO: handle symbols: list to complete the init loop 
        # fetch_ohlcv(make_jobspec(['EOS/BTC'], is_ccxt=False, stack=None, init=True))
        # WARNING
        # fetch_ohlcv(make_jobspec(['EOS/BTC'], is_ccxt=True)) # download is delayed, timeseries observations missing for current interval edge/peak
        pass

