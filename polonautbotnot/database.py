# https://datatofish.com/sql-to-pandas-dataframe/
# https://datatofish.com/pandas-dataframe-to-sql/

import asyncio
from concurrent.futures.process import _ExceptionWithTraceback
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from threading import RLock

import os, sys  # using path, maybe pathlib?

import sqlite3

import numpy as np
import pandas as pd

import typing as t
from typing import List, Dict, Any, Optional

from pandas.core.frame import DataFrame
import pprint

# create_ohlcv_tables.
from indicators.utils.sincer_checkpoint import slices

# from indicators.utils.sincer_checkpoint import sincer

# from df_ohlcv import make_jobspec

pp = pprint.pprint

# basepath = os.path.dirname(__file__)
basepath = os.path.dirname(os.path.abspath(__file__))

def update(table) -> str: # Various kinds of update
    """Construct statement for the scenario"""
    statement = f"""UPDATE {table} SET column='value' """
    
    def ud_creation():...
    def ud_continuous():...
    def ud_trim():...

    conn = get_conn()
    c = conn.cursor()
    c.execute(statement)
    conn.commit()

    return statement

def df_symbol(symbols: str, interval: str):
    #how-to-pass-a-function-with-more-than-one-argument-to-python-concurrent-futures
    try:
        from df_ohlcv import fetch_ohlcv, make_jobspec
    except ImportError as e:
        print(e)
    except Exception as e:
        print(e)

    # TODO: implement a queue, then consider threading it
    from concurrent.futures import ThreadPoolExecutor # thread safe??
    pool = ThreadPoolExecutor(3)
    init = pool.submit


    ##### REVIEW:> usedfule to keep, excepting ticker lookups, orderbook, or the initialization/restart fetch_ohlcv results, 5m is lowest level exchg timeframe
    # interval: int = #'5m' # lowest exchg timeframe
    extant: bool = False # won't know until we look

     # TEST INPUT PARAMS / considerations for DB ENTITIES DATA MODEL
    # symbol: str = 'eth_usdt'
    # interval: int = 5 # in minutes, should the table report length so 
    # indicator_id: int = 0

    # TODO: for Trader-side use only??? begging, should remote be able to create tables on the fly, and, of course, yes... 
    indicator: str = 'ao' # convenience
    stack: list = ['st', indicator, '5er', 'angleo'] # a list of indicators 
    stack = "_".join(stack).upper()

    print(symbols)
    # for symbol in symbols:
    #     name = table_namer(symbol, interval)
    #     check = table_extant(name)
    #     if check:
    #         update_type = date_last_entry() # ensure the right update happens
    #         # update types: enum? ['simple', 'paginated']
    #         df_update(update_type)
        # else:
    #         df = df_fetch_from_exchange(symbol, interval) if not extant else df_fetch_from_sql(symbol, exchange)
    
    for symbol in symbols:
        # data = init(fetch_ohlcv, make_jobspec([str(symbol)], interval, stack = False, is_ccxt=False, init=True))
        data = fetch_ohlcv(make_jobspec([str(symbol)], interval, stack = False, init=False))
        # print(f"{data = }")
        # data = data.result() # only for ThreadPoolExecutor

    # data = pool.submit(fetch_ohlcv, make_jobspec(['EOS/BTC'],"5m", stack, is_ccxt=False, init=True))
    # data = data.result()

    # data = pool.submit(fetch_ohlcv, make_jobspec(['LINKBULL/USDT'],"5m", stack=False, is_ccxt=False, init=True))
    # data = data.result()
    
    # df_dump(df) # save_to_table(df)


def get_conn(db_name: str = None) -> Any:
    #### TODO: multi-database strategy?
    ## will need to create cursor if conn is returned
    ## or distract on calls requiring conn
    # TODO: for asyncio operation, figure out and build sequential FIFO futures execution and associated thread lock stack...RLock
    # db_name = "test_db.sqlite" if not db_name else db_name # tested, works
    conn = None
    if not db_name:
        db_name = "test_db.sqlite"
    db_path = os.path.join(basepath, db_name)
    # print(db_path)
    conn = sqlite3.connect(db_path)
    # c = conn.cursor()
    return conn
    # return db_path, conn, c
    # return c

def clean_duplicates(tablename):
    conn = get_conn()
    c = conn.cursor()
    result: Any = None
    if check_table_exists(tablename):
        statement = "SELECT DISTINCT date FROM {} ORDER BY date".format(tablename)
        try:
            result = c.execute(statement).fetchall()
            print(result)
            statement = """ DELETE FROM {} 
                            WHERE rowid IN (
                                SELECT DISTINCT date
                                FROM {}
                                ORDER BY date)""".format(tablename, tablename)
            result = c.execute(statement).fetchall()
            print(result)
            statement = "SELECT DISTINCT date FROM {} ORDER BY date".format(tablename)
            result = c.execute(statement).fetchall()
            # result = c.fetchone()[0]
            print(result)
            conn.commit()
        except Exception as e:
            print("Exception in test", e)
    conn.close()
    return result #, result

def list_tables():
    conn = get_conn()
    with conn:
        c = conn.cursor()
        statement = "SELECT * FROM sqlite_master WHERE type='table'"
        c.execute(statement)
        result = c.fetchall()
        # conn.close() # with does close the db
    # for r in result:
    #     print(r)
    # idx = 'volume20s' # FIXME: volume20s does not play nicely and the list being sorted fixes it only because the table then gets called last, letting the others work out, but meaning any tables with an alpha greater than 'v' won't, as with xrp...
    result = sorted(result, key=(lambda x: x[1]))
    result = list(filter(lambda x: x[1] != 'volume20s', result))
    # idx = result.index(lambda x: x[1] == 'volume20s')
    # result.remove(idx)
    return result

def check_table_exists(tablename) -> bool:
    # TODO: with conn ??
    conn = get_conn()
    c = conn.cursor()
    statement = "SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{}'".format(tablename)
    c.execute(statement)
          
    if c.fetchone()[0] == 1:
        conn.commit()
        conn.close()
        return True
    else:
        conn.commit()
        conn.close()
        return False
    
    # c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='students1' ''')

    ## Alternative q/query integration
    # IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = N'employee_ids') BEGIN PRINT 'Yes' END ELSE BEGIN PRINT 'No' End.

    # # check if in memory db table exists
    # SELECT name FROM sqlite_temp_master WHERE type='table' AND name='table_name';

def test_checks():
    # TESTS in the middle of nowhere
    # TODO: might be possible to bypass init flag, just by checking exists table
    # TODO: relegate to sincer, or select another delegate/method
    print("table eos_btc_____5m___st_ao_5er_angleo exists: ", check_table_exists('eos_btc_____5m___st_ao_5er_angleo'))
    print("cleaning {} dups from eos_btc_____5m___st_ao_5er_angleo: ".format(clean_duplicates('eos_btc_____5m___st_ao_5er_angleo')))
    print('test checks complete')

def ohlcv_multi_table_constructor(symbol: list, **kwargs) -> None:
    ##    kwargs = {'connection': Callable} , particulars related to the active 
    # 
    # 
    # db connection
    conn = get_conn()
    c = conn.cursor()
    interval: str
    tablename: str = f"{symbol}"
    statement: str = f"{tablename}"
    conn.close()


def df_ohlcv_to_sql(df, cols, jobspec):
    conn = get_conn()
    c = conn.cursor()

    tablename = str(jobspec['tablename'])

    ########################################################
    statement = "CREATE TABLE IF NOT EXISTS {} ({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, CONSTRAINT uniq{} UNIQUE (date) ON CONFLICT REPLACE)".format(tablename, *cols, tablename)

    # print(statement)
    c.execute(statement)
    ########################################

    ####################### REVIEW
    statement = "CREATE INDEX IF NOT EXISTS idx{}ZZZ ON {} (date)".format(tablename, tablename)
    # print(statement)
    c.execute(statement)

    #######################
    # APPEND WRITE sans duplicates https://stackoverflow.com/a/51922280/7955763
   
    # @@@ ////////////////////////////////////////////////////////////////////
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html?highlight=to_sql#pandas.DataFrame.to_sql
    # /////////////////////////////////////////////////////////////////// @@@ 
    # from sqlite3 import OperationalError
    # loop = 0

    df.to_sql(name=tablename, index=False, if_exists='append', method='multi', con=conn)

    if jobspec['init'] is False: # no rows exist on init
        pass
    else:
        pass

def sql_to_df(tablename=None): # TODO: hook into jobspec indicator
    # TODO: need to look up by symbol
    def clean_seconds(): pass # TODO: clean seconds, sql on table and pd on update or init df
    # Putting all the code components together:
    # print(f"sql_to_df pre-bool: {tablename = }")
    conn = get_conn()
    c = conn.cursor()
    # if tablename == None:
    #     jobspec = {}
    #     tablename = jobspec['tablename'] = 'linkbull_usdt_5m'
    key: str = 'date'
    limit: int = 50 # depends on the timeframe, whether grouping or aggregating
    
    # TODO: require aggregation/group jobspec meta, possibly separate from updating loop, possibly in a different program... no lock on thread,,, what are the implications for multiple client access, re. ACID, referential integrity, etc.
    # CREATE TABLE linkbull_usdt_5m (date, high, low, open, close, volume, quoteVolume, weightedAverage, hl2, hlc3, ohlc4)
    # statement = "SELECT * FROM {} ORDER BY {} LIMIT {}".format(key, tablename, key,limit) # works , key, limit)
    # statement = "SELECT DISTINCT * FROM {} ORDER BY {} DESC LIMIT {}".format( tablename, key, limit) # works, but gives reverse data, key, limit)
    statement = """
                SELECT DISTINCT * FROM (
                SELECT * FROM {} ORDER BY {} DESC LIMIT {})
                ORDER BY {} ASC
                """.format( tablename, key, limit, key)
        

    # c.execute(statement)
    # result = c.execute(statement).fetchall()
    # print(result)
    # print()
    
    # with conn:        
    # SELECT * FROM products WHERE price = (SELECT max(price) FROM products)
    columns=['date', 'high', 'low', 'open', 'close', 'volume', 'quoteVolume', 'weightedAverage', 'hl2', 'hlc3', 'ohlc4']
    if check_table_exists(tablename):
        print(f"sql_to_df:: {tablename = }")
        c.execute(statement)
        df = pd.DataFrame(c.fetchall(), columns=columns)
        # df = df.filter(['open', 'high', 'low', 'close', 'volume'])
        # print(df)
        df['date'] = pd.to_datetime(df['date']) #, !!unit='s', dayfirst=True,  errors='coerce')
        # pp(df.dtypes)
        conn.close()

    return df

def stuff(x):
    print(x)

async def main():
    from concurrent import futures
    with ThreadPoolExecutor() as pool:
        # TODO: Create the stack that'll run table creation and updating, as a separately running program with its own docker-compose service instance, no need for a framework, and really, no need for asyncio, but then, what of future integration with the main program stack, and portability re. data interchange and necessary mutations of the core database(s), for instance, including indicator data aligned to timeseries ohlcv, on the same table, just having more horizontal fields, adding backtest-produced results as observations in addition to the price information depended upon?
        # TODO: So, the real question is how is a symbol and its interval related to indicators, what are the best and most efficient way(s) of separating concerns?
        conn = pool.submit(get_conn())
        # await conn
        if conn:
            print(conn)
        # map
        # exec
        # stuffs = [asyncio.create_task(stuff(x)) for x in range(10)]
        # await pool.gather(*stuffs) # do some list of job(s)
            print('at last, my time has come...')
        conn.close()

# define exportable core list of symbols you want to instantiate
# symbols = ['LINKBULL/USDT', 'BTC/USDT', 'EOS/BTC', 'TRX/USDT', 'XRP/USDT', 'ETH/USDT']

if __name__ == '__main__':
    import datetime
    from time import sleep
    from indicators.utils.sincer_checkpoint import slices
    # import schedule, time
    import time
    from indicators.utils.beep import say

    # Obtain DataFrame, then Create a Table and Dump 
    # https://stackoverflow.com/questions/42056738/

    # test_checks()
    # TODO: SINCER awareness of last record date, pagination style update

    # df = sql_to_df()
    # df = df.filter(['date', 'open', 'high', 'low', 'close', 'volume'])
    # # pp(jobspec())
    # pp(df.dtypes)
    # pp(df.tail(3))
    # pp(df.head(3))
    
    # TODO: contains invalid symbols, those with an underscore '_'
    # symbols = ['LINKBULL/USDT', 'BTC_USDT', 'EOS/BTC', 'TRX_USDT', 'XRP/USDT', 'ETH/USDT']
    # Uses ccxt valid symbols, converting them to Poloniex
    async def run():

        async def a(s=None) -> None:
            if s == None:
                interval = '5m'
                # defined as exportable above, working here through testing
                # symbols = ['LINKBEAR/USDT', 'EOS/BTC', 'TRX/USDT', 'XRP/USDT', 'ETH/USDT', 'LINKBULL/USDT', 'BTC/USDT']
                # TODO: validate these Symbols exist even if there is a tablename with values...
                symbols = ['EOS/BTC', 'TRX/USDT', 'XRP/USDT', 'ETH/USDT', 'BTC/USDT']
                # a list of populated symbol instances, each with an interval appropriate to tablenamer(), fetch_ohlcv() and others
            else:
                symbols = [s]
            print(symbols)
            result = df_symbol(symbols, interval) # all on the same interval
            if result:
                # TODO: inform subscribers new timestamp is in TODO: confirm timestamp is current
                pass

        def b(t: list) -> DataFrame:
            # tables = list_tables()
            # t = tables
            # # t = tables[-1]
            # # t = [t]
            for tablename in t:
                df = sql_to_df(str(tablename[1])) # need to set jobspec
                df = df.filter(['date', 'open', 'high', 'low', 'close', 'hl2', 'hlc3', 'ohlc4', 'volume'])
                # # pp(jobspec())
                # pp(df.dtypes)
                # print(df.info())
                # pp(df.head(3)) 
                # pp(df.tail(3))
                # print(df)
                # pp(df)
                return df
        
        def c():
            # from orders import order
            pass
            
        ## optionally test individual symbols
        # symbol = 'ETH/USDT'
        # symbol = 'BTC/USDT'
        # symbol = 'EOS/BTC'
        # symbol = 'LINKBULL/USDT'
        await a()
        # a(symbol)

        c() # lets make the orders table

        async def strategy():
            from indicators.supertrend_strategy import run as supertrend
            from indicators.utils.atr import atr

            # FIXME: error: local variable 'fetch_ohlcv' referenced before assignment; when using other venvs??? seems implausible, but it's happening that way

            # stacks = [supertrend, fiver, ao, angleo]
            stacks = [supertrend] #, macdraw]

            # load options for each 
            tables = list_tables()
            # FIXME: must lookup tables following tablenamer conversion, or store tablename in db and load as global schema into individual symbol class instances so the list can update and strategy...
            # print('tables: ', tables)
            t = tables
            # t = tables[-1]
            # t = [t]
            for table in tables:
                print(str(table[1]))
            for tablename in t:
                print('strategy: ', str(tablename[1]))
                # if str(tablename[1]) == 'volume20s':
                #     return
                for stack in stacks:
                    print('in strategy for each - tablename - to b(): ', str(tablename[1]))
                    df = b([tablename])
                    # add common indicators #TODO add conditionally
                    frame = atr(df, period=7, atr_multiplier=3)
                    # print(frame)
                    df = stack(frame)
                    # stack(df)
                    print(df.iloc[:, np.r_[0, 4, 9, 18]].tail(7))

        await strategy()

    try:
        asyncio.run(run()) # run immediately
    except Exception as e:
        print(e)

    async def sleep_to_next_interval_clock_top():
        """setup to run schedule"""
        import datetime
        from time import sleep
        from indicators.utils.sincer_checkpoint import slices
        start, end = slices()
        delta = datetime.timedelta(seconds=300)
        end = datetime.datetime.fromtimestamp(end) + delta
        print(datetime.datetime.now())
        print(f"{end = }")
        # targets don't lie, they hang
        snore = end - datetime.datetime.now()
        # added in sincer_checkpoint.py _end_utc, 45sec
        snore = snore.total_seconds() # + 30
        snore_min = snore/60
        print(f"{snore = }")
        # print(f"{snore_min = }")
        # sleep(snore)
        # asyncio.gather(*[asyncio.sleep(snore)])
        await asyncio.sleep(snore)
        # sleep(10)


    # import schedule, time
    import time

    # sleep_to_next_interval_clock_top()
    
    while True:
        asyncio.run(sleep_to_next_interval_clock_top())
        say()
        try:
            asyncio.run(run())
        except Exception as e:
            print(e)
            continue

    # schedule.every(5).minutes.do(run)

    # while True:
    #     # print(datetime.datetime.now())
    #     schedule.run_pending()
    #     time.sleep(1)
    #     # print(datetime.datetime.now())


    # TODO: possible controller stubs DESIGN
    # taking cyclic update input from table names list
    # console input to include a new symbol
    # console input to exclude a symbol from updates
    # console input to apply a strategy to a symbol
    # "" to remove a symbol from a strategy
    
   



    
