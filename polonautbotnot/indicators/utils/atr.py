# https://www.investopedia.com/terms/a/atr.asp

def tr(data):
    # fixed datatype for high-low, high-pc, low-pc, tr, etc. as these are/were in scientific notation, working on their own, but not with floats
    data['previous_close'] = data['close'].shift(1)
    data['high-low'] = abs(data['high'] - data['low'])
    data['high-low'].astype(float)
    data['high-pc'] = abs(data['high'] - data['previous_close'])
    data['high-pc'].astype(float)
    data['low-pc'] = abs(data['low'] - data['previous_close'])
    data['low-pc'].astype(float)
    tr = data[['high-low', 'high-pc', 'low-pc']].max(axis=1).astype(float)
    return tr

def aatr(data, period):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()
    return atr

def atr(df, period=7, atr_multiplier=3):
    df['atr'] = aatr(df, period)
    return df

if __name__ == '__main__':
    pass


