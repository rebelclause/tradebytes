# https://www.investopedia.com/terms/c/change.asp

def change(s) -> float:
    """Receives a select series from a dataframe"""
    # idx = df['close'].index
    # change = s.iloc[0, idx] - s.iloc[1, idx]
    change = s.iloc[0] - s.iloc[1]
    print("change.py - Confirm the correct idx's are used, top v. bottom")
    return change

if __name__ == '__main__':
    pass