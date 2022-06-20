#https://backtest-rookies.com/2020/03/29/tradingview-creating-trend-lines/




def slope(x1, x2, y1, y2):
    m = y2 - y1 / x2 - x1

def y_intercept(m, x1, y1):
    b = y1-m*x1
    
def y_value(m, b, x):
    y = mx+b
    b = y - mx
    return b, y

# rework the equation to solve y and b in relation to one another




