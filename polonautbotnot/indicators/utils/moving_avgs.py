import pandas as pd
import numpy as np
import pandas_ta as ta
# ta.wma

# https://www.quantstart.com/articles/Backtesting-a-Moving-Average-Crossover-in-Python-with-pandas/
# https://stackoverflow.com/questions/36932019/how-to-test-ema-crossover-obtained-from-pandas-python-in-ms-excel

# Trend Finding Methods
# https://medium.com/codex/simple-moving-average-and-exponentially-weighted-moving-average-with-pandas-57d4a457d363

    # Freehand Graphical Method,
    # Method of selected points,
    # Method of semi-averages,
    # Method of moving averages,
    # Method of Least Squares.

# pd windowing
# https://pandas.pydata.org/docs/user_guide/window.html#window-exponentially-weighted
# for window in s.rolling(window=2):
#     print(window)

# s = pd.Series(range(5), index=pd.date_range('2020-01-01', periods=5, freq='1D'))
# s.rolling(window='2D').sum()

# py logical operators
# https://docs.python.org/3/library/operator.html#mapping-operators-to-functions

def sma(df, x):
    # TODO: find out if and how it is possible to work the window over an input pd.df using python builtins, probably a list deque over the input frame indicies, but not fully understood
    sma = df.rolling(x).mean() #window=x
    # sum = 0.0
    # # for i = 0 to y - 1:
    # for i in range(x-1):
    #     sum = sum + df.iloc[i] / x
    # return sum
    return sma

def ema(df, x):
    # TODO: see sma(), this module
    ema = df.ewm(x).mean() #span
    # sum = 0.0
    # # for i = 0 to y - 1:
    # for i in range(x-1):
    #     sum = sum + df.iloc[i] / x
    # return sum
    return ema

def hma(df=None, window=9):
    if df:
        df['wma'] = ta.trend.wma_indicator(df['close'], window=window, fillna=False)
        # y = wma from polo df
        df['hma'] = df.wma
    # might not work for other exchanges util/unless VWMA is separately calculated from ohlcv inputs
    # https://www.motivewave.com/studies/hull_moving_average.htm
    # https://www.investopedia.com/articles/active-trading/052014/how-use-moving-average-buy-stocks.asp
    # HMA[i] = MA( (2*MA(input, period/2) – MA(input, period)), SQRT(period))
    """
    https://tickertape.tdameritrade.com/trading/investing-hull-moving-average-18444
    For this example, we’ll use 16 as the length for the HMA calculation:

    1.       Calculate the WMA for the full length (16-day WMA)

    2.       Calculate the WMA for half the Length (8-day WMA)

    3.       Subtract step 1 result from step 2 (find the difference between WMA of 16 and 8 lengths)

    4.       Add step 3 to step 2 (add difference to WMA 8 day)

    5.       Calculate the square root of the full length (v16 = 4)

    6.       Calculate the WMA of step 4 using length of step 5
    """

    return df

def macd():
    pass

# https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html?highlight=hull%20moving%20average#ta.momentum.AwesomeOscillatorIndicator
# ta.momentum.AwesomeOscillatorIndicator(high: pandas.core.series.Series, low: pandas.core.series.Series, window1: int = 5, window2: int = 34, fillna: bool = False)



