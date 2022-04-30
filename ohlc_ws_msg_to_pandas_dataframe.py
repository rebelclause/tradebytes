# https://support.kraken.com/hc/en-us/articles/360022635992-Ticker
""" # https://docs.kraken.com/websockets/#message-ohlc
channelID 	integer 	Channel ID of subscription - deprecated, use channelName and pair
Array 	array 	
time 	decimal 	Begin time of interval, in seconds since epoch
etime 	decimal 	End time of interval, in seconds since epoch
open 	decimal 	Open price of interval
high 	decimal 	High price within interval
low 	decimal 	Low price within interval
close 	decimal 	Close price of interval
vwap 	decimal 	Volume weighted average price within interval
volume 	decimal 	Accumulated volume within interval
count 	integer 	Number of trades within interval
channelName 	string 	Channel Name of subscription
pair 	string 	Asset pair
"""

import pandas as pd
import numpy as np
import datetime

def ohlc_ex():
    """Kraken-specific websocket OHLC message extraction to dataframe."""
    
    ohlc_example = [343, ['1651352136.909793', '1651352160.000000', '38316.80000', '38332.30000', '38316.80000', '38320.00000', '38329.61479', '0.06570887', 4], 'ohlc-1', 'XBT/USD']

    ds = ohlc_example[1]
    columns = ["stime", "etime", "open", "high", "low", "close", "vwap", "volume", "count"]

    df = pd.DataFrame(ds, index=columns).T
    stime = datetime.datetime.fromtimestamp(float(df["stime"]))    
    etime = datetime.datetime.fromtimestamp(float(df["etime"]))  
    print(stime, etime)

    #df["channel"] = ohlc_example[2]
    df["pair"] = ohlc_example[3]
    df["pair"] = df["pair"].astype(np.str_)

    df["stime"] = pd.to_datetime(stime)
    df["etime"] = pd.to_datetime(etime)
    df["open"] = df["open"].astype(np.float64)
    df["high"] = df["high"].astype(np.float64)
    df["low"] = df["low"].astype(np.float64)
    df["close"] = df["close"].astype(np.float64)
    df["vwap"] = df["vwap"].astype(np.float64)
    df["volume"] = df["volume"].astype(np.float64)
    df["count"] = df["count"].astype(np.int8)

    df.filter(["pair", "stime", "etime", "open", "high", "low", "close", "vwap", "volume", "count"])

    return df

print(ohlc_ex().info())
print(ohlc_ex())
print(ohlc_ex().filter(["pair", "stime", "etime", "open", "high", "low", "close", "vwap", "volume", "count"]))
print(ohlc_ex().filter(["pair", "etime", "open", "high", "low", "close", "vwap"]))

if __name__ == '__main__':
    tickers =  ['XBT/USD', 'XRP/USD']
