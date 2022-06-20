'''
https://coderedirect.com/questions/195605/how-do-i-sign-a-post-request-using-hmac-sha512-and-the-python-requests-library
    
https://docs.python-requests.org/en/latest/user/authentication/#new-forms-of-authentication
'''
import os, sys
import pandas as pd
import numpy as np
from pathlib import Path
import requests
import hmac
import hashlib
from itertools import count
import datetime
import time



p = os.path.join(Path(__file__).parents[1])

basepath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, p)
print(f"{sys.path = }")

# from config import config
import config
# from database import get_conn


# Set environment variables
os.environ['API_USER'] = 'username'
os.environ['API_PASSWORD'] = 'secret'

# Get environment variables
USER = os.getenv('API_USER')
PASSWORD = os.environ.get('API_PASSWORD')

# Getting non-existent keys
FOO = os.getenv('FOO') # None
BAR = os.environ.get('BAR') # None
# BAZ = os.environ['BAZ'] # KeyError: key does not exist.

# store as a global variable
NONCE_COUNTER = count(int(time.time() * 1000)) #epoch
# then every time you create a request
# payload['nonce'] = next(NONCE_COUNTER)

def check_convert_symbol(symbol):
    # ascertain symbol type
    # if ccxt, convert to polo
    # if polo, leave
    # in all cases symbol.uppercase()
    # TODO: see jobspec()
    if '/' in symbol:
        base, quote = symbol.split('/')
        symbol = f"{quote}_{base}"
    # print(symbol)
    # TODO: check symbol exists in table
    return symbol.upper()

class ChkSymbol(object):
    def __init__(self, symbol, sep='/'):
        self.symbol = symbol
        self.base = None
        self.quote = None

    def __call__(self):
        pass

class BodyDigestSignature(object):
    def __init__(self, secret, header='Sign', algorithm=hashlib.sha512):
        self.secret = secret
        self.header = header
        self.algorithm = algorithm

    def __call__(self, request):
        body = request.body
        # print(f"{body = }")
        if not isinstance(body, bytes):   # Python 3
            body = body.encode('latin1')  # standard encoding for HTTP
        signature = hmac.new(self.secret, body, digestmod=self.algorithm)
        request.headers[self.header] = signature.hexdigest()
        return request

class WSSubscriptionSignature(object):
    def __init__(self, secret=None, header='Sign', algorithm=hashlib.sha512):
        self.secret = config.API_SECRET_POLONIEX.encode('utf-8')
        self.header = header
        self.algorithm = algorithm

    # @staticmethod
    def sub_channel_sign(self, channel: int):
        import json
    # def __call__(self, channel:int):
        # https://docs.python.org/3/library/hmac.html
        # from hmac import hmacsha512
        # headers['Key'] = config.POLONIEX_API_KEY
        # https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3
        # secret = config.POLONIEX_SECRET_KEY.encode('utf-8')
        nonce = next(NONCE_COUNTER)
        # noncea = f'"nonce={nonce}"'.encode('utf-8')
        noncea = []
        noncea.append(str(nonce))
        dir(noncea[0])
        nonceS = noncea[:][0]
        nonceB = (noncea[0]).encode('utf-8')
        print(nonceS, nonceB)


        # sign = hmac.new(self.secret, f'"nonce={nonce}"', digestmod=self.algorithm).hexdigest()
        # https://docs.poloniex.com/#subscribing-and-unsubscribing
        sign = hmac.new(self.secret, msg=nonceB, digestmod=self.algorithm).hexdigest()

        signed_subscribe = { "command": "subscribe", "channel": f"{channel}", "key": f"{config.API_KEY_POLONIEX}", "sign": f"{sign}", "payload": f"nonce={nonceS}" }

        return signed_subscribe

def get_request(url):
    # url = f"https://poloniex.com/public
    now = datetime.datetime.utcnow()
    print(f"{now}: {url = }")
    response = requests.get(url)
    dj = response.json()
    try:
        df = pd.DataFrame.from_dict(dj)
        cols = df.columns.tolist()
    except Exception as e:
        # data = {k: (v,) for k, v in dj.items()}
        # print(data)
        ds = pd.Series(dj)
        df = pd.DataFrame(ds).T
        cols = df.columns.tolist()
        # print(df)

    return [df, now, cols]
    

def post_request(payload, headers):
    payload['nonce'] = next(NONCE_COUNTER)
    headers['Key'] = config.API_KEY_POLONIEX
    # https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3
    secret = config.API_SECRET_POLONIEX.encode('utf-8')
    response = requests.post(
        'https://poloniex.com/tradingApi',
        data=payload, headers=headers, auth=BodyDigestSignature(secret))
    # auth = BodyDigestSignature(secret)
    # import json
    # json_data = dict(json.loads(response.text))
    # return json_data
    now = datetime.datetime.utcnow()
    print(f"{now}: {payload['command'] = }")
    dj = response.json() #builtin Requests method
    # print(dj)
    # djcols = dj.keys()
    # djvals = dj.values()
    # print(djcols)
    # print(djvals)
    try:
        df = pd.DataFrame.from_dict(dj)
        cols = df.columns.tolist()
    except Exception as e:
        # data = {k: (v,) for k, v in dj.items()}
        # print(data)
        ds = pd.Series(dj)
        df = pd.DataFrame(ds).T
        cols = df.columns.tolist()
        # print(df)

    return [now, cols, df]


def get_balances():
    '''
    Returns all of your balances available for trade after having deducted all open orders.
    '''
    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'returnBalances',
                'account': 'all'}
    # payload['nonce'] = next(NONCE_COUNTER)
    if symbol:
        payload['account'] = symbol
    
    return post_request(payload, headers, secret)


# Use this with your requests calls:
def get_complete_balances(symbol=None):
    '''
    Field 	Description
    available 	Number of tokens not reserved in orders.
    onOrders 	Number of tokens in open orders.
    btcValue 	The BTC value of this token's balance.
    '''
    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'returnCompleteBalances',
                'account': 'all'}
    # payload['nonce'] = next(NONCE_COUNTER)
    if symbol is not None:
        payload['account'] = symbol

    return post_request(payload, headers)


def cancel_order(order_number=None):
    '''
    Input Fields
    Field 	Description
    orderNumber 	(Optional) The identity number of the order to be canceled.
    clientOrderId 	(Optional) User specified 64-bit integer identifier.
    '''
    # https://docs.poloniex.com/#buy

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'cancelOrder',
                'orderNumber': order_number,}

    if order_number is None:
        return None

    return post_request(payload, headers)
    '''
    Output Fields
    Field 	Description
    success 	A boolean indication of the success or failure of this operation.
    amount 	The remaning unfilled amount that was canceled in this operation.
    message 	A human readable description of the result of the action.
    clientOrderId 	(optional) If clientOrderId exists on the open order it will be returned in the cancelOrder response.
    '''


def cancel_all_orders(symbol=None):
    '''
    Input Fields
    Field 	Description
    currencyPair 	(optional) A string that defines the market, "USDT_BTC" for example.
    '''
    # https://docs.poloniex.com/#cancelAllOrders

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'cancelAllOrders',
                'account': 'all'}

    if symbol is not None:
        # TODO: symbol = convert_cymbal(symbol)
        symbol = check_convert_symbol(symbol)
        payload['currencyPair'] = symbol

    return post_request(payload, headers)

    '''
    Output
    Field 	Description
    success 	A boolean indication of the success or failure of this operation.
    message 	A human readable description of the result of the action.
    orderNumbers 	array of orderNumbers representing the orders that were canceled.
    '''

def cancel_replace(orderNumber=None, order_id=None, rate=None, amount=None):
    '''    
    Input Fields
    Field 	Description
    orderNumber 	The identity number of the order to be canceled.
    clientOrderId 	(optional) User specified 64-bit integer identifier to be associated with the new order being placed. Must be unique across all open orders for each account.
    rate 	The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    amount 	(optional) The amount of tokens in this order.'''

    # https://docs.poloniex.com/#buy

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'cancelReplace',
                'account': 'all'}
    if symbol is not None:
        # TODO: symbol = convert_cymbal(symbol)
        payload['currencyPair'] = symbol
    
    return post_request(payload, headers)

    '''Canceled Output Fields
    Field 	Description
    success 	A boolean indication of the success or failure of the cancellation.
    amount 	The remaining unfilled amount that was canceled.
    message 	A human readable description of the result of the cancellation.
    clientOrderId 	(optional) User specified 64-bit integer identifier associated with the canceled order.
    fee 	The fee multiplier for the canceled older.
    currencyPair 	A string that defines the market, "USDT_BTC" for example.
    placed 	The new order (see placed output fields).'''


    '''Placed Output Fields
    Field 	Description
    success 	A boolean indication of the success or failure of this operation.
    orderNumber 	The newly created order number.
    resultingTrades 	An array of the trades that were executed, if any, on order placement.
    tokenFee 	The total fee paid, if any, using a token to pay fees.
    tokenFeeCurrency 	The currency used to pay fees if any token fee was used.
    message 	(optional) A human-readable message summarizing the activity.
    fee 	The fee multiplier for this order.
    clientOrderId 	(optional) Client specified 64-bit integer identifier.
    currencyPair 	A string that defines the market, "USDT_BTC" for example.'''

def enter(symbol=None, order_id=None, quote_price=0, fillOrKill=False, immediateOrCancel=False, postOnly=False):
    '''
    Input Fields
    Field 	Description
    currencyPair 	A string that defines the market, "USDT_BTC" for example.
    rate 	The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    amount 	The total amount offered in this buy order.
    fillOrKill 	(optional) Set to "1" if this order should either fill in its entirety or be completely aborted.
    immediateOrCancel 	(optional) Set to "1" if this order can be partially or completely filled, but any portion of the order that cannot be filled immediately will be canceled.
    postOnly 	(optional) Set to "1" if you want this buy order to only be placed if no portion of it fills immediately.
    clientOrderId 	(optional) 64-bit Integer value used for tracking order across http responses and "o", "n" & "t" web socket messages. Must be unique across all open orders for each account.

    '''
    # https://docs.poloniex.com/#buy

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'buy'}
    payload['fillOrKill'] = 1 if fillOrKill == True else ''
    payload['immediateOrCancel'] = 1 if immediateOrCancel == True else ''
    payload['postOnly'] = 1 if postOnly == True else ''
    payload['clientOrderId'] = order_id if order_id != None else ''

    if symbol is None:
        return None

    symbol = check_convert_symbol(symbol)
    payload['currencyPair'] = symbol
    
    # return post_request(payload, headers)

    buy_dict = { "orderNumber": "514845991795",
                "resultingTrades":
                [ { "amount": "3.0",
                    "date": "2018-10-25 23:03:21",
                    "rate": "0.0002",
                    "total": "0.0006",
                    "tradeID": "251834",
                    "type": "buy" } ],
                "fee": "0.01000000",
                "clientOrderId": "12345",
                "currencyPair": "BTC_ETH" }

    # dict_keys(['orderNumber', 'resultingTrades', 'fee', 'clientOrderId', 'currencyPair'])
    # dict_keys(['amount', 'date', 'rate', 'total', 'tradeID', 'type'])

    print(buy_dict.keys())
    print('enter end')

    '''
    Output Fields
    Field 	Description
    orderNumber 	The identification number of the newly created order.
    resultingTrades 	An array of the trades that were executed, if any, on order placement.
    amount 	The amount of tokens remaining unfilled in this order.
    date 	The UTC date this order was created.
    rate 	The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    total 	The total value of this order.
    tradeID 	The identifier for this trade.
    type 	Designates a buy or a sell order. (always "buy" in this case)
    fee 	The fee multiplier for this trade.
    currencyPair 	A string that defines the market, "USDT_BTC" for example.
    clientOrderId 	(optional) User specified 64-bit integer identifier.
    tokenFee 	The total fee paid, if any, using a token to pay fees.
    tokenFeeCurrency 	The currency used to pay fees if any token fee was used.
    '''

def exit(symbol=None, order_id=None, quote_price=0, fillOrKill=False, immediateOrCancel=False, postOnly=False):

    ''' 
    Input Fields
    Field 	Description
    currencyPair 	A string that defines the market, "USDT_BTC" for example.
    rate 	The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    amount 	The total amount offered in this sell order.
    fillOrKill 	(optional) Set to "1" if this order should either fill in its entirety or be completely aborted.
    immediateOrCancel 	(optional) Set to "1" if this order can be partially or completely filled, but any portion of the order that cannot be filled immediately will be canceled.
    postOnly 	(optional) Set to "1" if you want this sell order to only be placed if no portion of it fills immediately.
    clientOrderId 	(optional) 64-bit Integer value used for tracking order across "o", "n" & "t" web socket messages. Must be unique across all open orders for each account.
    '''
    # https://docs.poloniex.com/#sell

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'sell'}
    payload['fillOrKill'] = 1 if fillOrKill == True else ''
    payload['immediateOrCancel'] = 1 if immediateOrCancel == True else ''
    payload['postOnly'] = 1 if postOnly == True else ''
    payload['clientOrderId'] = order_id if order_id != None else ''

    if symbol is None:
        return None

    symbol = check_convert_symbol(symbol)
    payload['currencyPair'] = symbol

    # return post_request(payload, headers)

    sell_dict = { "orderNumber": "514845991926",
        "resultingTrades":
        [ { "amount": "1.0",
            "date": "2018-10-25 23:03:21",
            "rate": "10.0",
            "total": "10.0",
            "tradeID": "251869",
            "type": "sell" } ],
    "fee": "0.01000000",
    "clientOrderId": "12345",
    "currencyPair": "BTC_ETH" }

    print(sell_dict.keys())
    # dict_keys(['orderNumber', 'resultingTrades', 'fee', 'clientOrderId', 'currencyPair'])
    # dict_keys(['amount', 'date', 'rate', 'total', 'tradeID', 'type'])
    print(sell_dict['resultingTrades'][0].keys())
    print("exit end")

    '''
    Output Fields
    Field 	Description
    orderNumber 	    The identification number of the newly created order.
    resultingTrades 	An array of the trades that 
                        were executed, if any, on order placement.
        amount 	The amount of tokens remaining unfilled in this order.
        date 	The UTC date this order was created.
        rate 	The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
        total 	The total value of this order.
        tradeID 	The identifier for this trade.
        type 	Designates a buy or a sell order. (always "sell" in this case)
    fee 	            The fee multiplier for this trade.
    currencyPair 	    A string that defines the market, "USDT_BTC" for example.
    clientOrderId 	    (optional) User specified 64-bit integer identifier.
    tokenFee 	        The total fee paid, if any, using a token to pay fees.
    tokenFeeCurrency 	The currency used to pay fees if any token fee was used.
    '''

def m_enter(symbol=None, order_id=None, quote_price=0.0, amount=0.0):

    '''
    Input Fields
    Field 	Description
    currencyPair 	A string that defines the market, "USDT_BTC" for example.
    rate 	The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    lendingRate 	The interest rate you are willing to accept per day. (default is 0.02 which stands for 2% per day)
    amount 	The amount to buy.
    clientOrderId 	(optional) 64-bit Integer value used for tracking order across http responses as well as "o", "n" & "t" web socket messages. Must be unique across all open orders for each account.
    '''
    # https://docs.poloniex.com/#marginSell

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'marginBuy'}

    if symbol is None:
        return
    
    symbol = check_convert_symbol(symbol)
    payload['currencyPair'] = symbol
    payload['clientOrderId'] = order_id if order_id != None else ''
    payload['rate'] = quote_price if quote_price != 0.0 else ''
    payload['lendingRate'] = 0.02
    payload['amount'] = amount if amount else ''

    # return post_request(payload, headers)

    m_enter_dict = { "orderNumber": "515007818812",
                        "resultingTrades": [],
                        "message": "Margin order placed.",
                        "clientOrderId": "12345" }

    print(m_enter_dict.keys())
    # dict_keys(['orderNumber', 'resultingTrades', 'message', 'clientOrderId'])
    print('m_enter end')

    '''
    Output Fields
    Field 	Description
    orderNumber 	The newly created order number.
    resultingTrades 	An array of trades immediately filled by this offer, if any.
    message 	A human-readable message summarizing the activity.
    clientOrderId 	(optional) Client specified 64-bit integer identifier.
    '''

def m_exit(symbol=None, order_id=None, quote_price=0.0, amount=0.0):
    '''
    Input Fields
    Field 	Description
    currencyPair 	A string that defines the market, "USDT_BTC" for example.
    rate 	The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    lendingRate 	The interest rate you are willing to accept per day. (default is 0.02 which stands for 2% per day)
    amount 	The amount of currency to sell.
    clientOrderId 	(optional) 64 bit Integer value used for tracking order across http responses as well as "o", "n" & "t" web socket messages. Must be unique across all open orders for each account.

    '''
    # https://docs.poloniex.com/#marginSell

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'marginSell'}
    
    if symbol is None:
        return
    
    symbol = check_convert_symbol(symbol)
    payload['currencyPair'] = symbol
    payload['clientOrderId'] = order_id if order_id != None else ''
    payload['rate'] = quote_price if quote_price != 0.0 else ''
    payload['lendingRate'] = 0.02
    payload['amount'] = amount if amount else ''

    # return post_request(payload, headers)

    m_exit_dict = { "orderNumber": "515007818812",
                    "resultingTrades": [],
                    "message": "Margin order placed.",
                    "clientOrderId": "12345" }

    print(m_exit_dict.keys())
    # dict_keys(['orderNumber', 'resultingTrades', 'message', 'clientOrderId'])
    print('m_exit end')


    '''
    Output Fields
    Field 	Description
    orderNumber 	The newly created order number.
    resultingTrades 	An array of trades immediately filled by this offer, if any.
    message 	A human-readable message summarizing the activity.
    clientOrderId 	(optional) 64 bit Client specified integer identifier.
    '''

def get_margin_position(symbol=None):
    '''
    Input Fields
    Field 	Description
    currencyPair 	A string that defines the market, "USDT_BTC" for example.
    '''
    # https://docs.poloniex.com/#getMarginPosition

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'getMarginPosition'}
    
    if symbol is None:
        return
    
    symbol = check_convert_symbol(symbol)
    payload['currencyPair'] = symbol

    return post_request(payload, headers)

    '''
    Output Fields
    Field 	Description
    amount 	The net amount of the market's currency you have bought or sold. If your position is short, this value will be negative.
    total 	The total amount of the currency in your position.
    basePrice 	The approximate price at which you would need to close your position in order to break even.
    liquidationPrice 	The estimated highest bid (if your position is long) or lowest ask (if it is short) at which a forced liquidation will occur.
    pl 	Estimated profit or loss you would incur if your position were closed. Includes lending fees already paid.
    lendingFees 	The estimated value of outstanding fees on currently-open loans.
    type 	Denotes the overall position in this market as either "long" (buy heavy) or "short". (sell heavy)
    '''

def close_margin_position(symbol=None):
    '''
        Input Fields
        Field 	Description
        currencyPair 	A string that defines the market, "USDT_BTC" for example.
    '''
    # https://docs.poloniex.com/#closeMarginPosition

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'closeMarginPosition'}

    if symbol is None:
        return

    symbol = check_convert_symbol(symbol)
    payload['currencyPair'] = symbol

    data = post_request(payload, headers) # returned as json
    print(data['success'])
    print(data['message'])
    print(data['resultingTrades'])

    return data

    '''
    Output Fields
    Field 	Description
    success 	Denotes whether a success (1) or a failure (0) of this operation.
    message 	A human-readable message summarizing the activity.
    resultingTrades 	An array of any trades that have executed as a result of closing this position.
    '''
def return_margin_summary():
    # data, index, columns, dtype=dtype, copy=copy, typ=manager
    
    '''
    Output Fields
    Field 	            Description
    totalValue 	        Total margin value in BTC.
    pl 	                Unrealized profit and loss in BTC.
    lendingFees 	    Unrealized lending fees in BTC.
    netValue 	        Net value in BTC.
    totalBorrowedValue 	Total borrowed value in BTC.
    currentMargin 	    The current margin ratio.
    '''
    # https://docs.poloniex.com/#returnMarginAccountSummary

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'returnMarginAccountSummary'}

    return post_request(payload, headers)

def return_currencies():
    """    
    Returns information about currencies.
    Request Parameter 	Description
    includeMultiChainCurrencies (optional) 	A boolean that indicates if multi chain currencies are included (default value is false).
    """
    url = f"https://poloniex.com/public?command=returnCurrencies"
    
    return get_request(url) # returned as json
    
    """
    Field 	Description
    id 	ID of the currency.
    name 	Name of the currency.
    humanType 	The type of blockchain the currency runs on.
    currencyType 	The type of the currency.
    txFee 	The network fee necessary to withdraw this currency.
    minConf 	The minimum number of blocks necessary before a deposit can be credited to an account.
    depositAddress 	If available, the deposit address for this currency.
    disabled 	Designates whether (1) or not (0) deposits and withdrawals are disabled.
    frozen 	Designates whether (1) or not (0) trading for this currency is disabled for trading.
    blockchain 	The blockchain the currency runs on.
    delisted 	Designates whether (1) or not (0) this currency has been delisted from the exchange.
    isGeofenced 	Designates whether this currency is available (1) or not (0) to this customer due to geofencing restrictions.

    If the currency lists a deposit address, deposits to that address must be accompanied by a deposit message unique to your account. See the Balances, Deposits & Withdrawals page for more information.
    """

def return_trade_history(symbol=None, start=None, end=None):
    '''    
    Field 	Description
    globalTradeID 	The globally unique ID associated with this trade.
    tradeID 	The ID unique only to this currency pair associated with this trade.
    date 	The UTC date and time of the trade execution.
    type 	Designates this trade as a buy or a sell from the side of the taker.
    rate 	The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    amount 	The number of units transacted in this trade.
    total 	The total price in base units for this trade.
    orderNumber 	The order number for this trade.
    '''
    # https://docs.poloniex.com/#returnTradeHistory # Public

    # curl "https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_ETH"
    # curl "https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_ETH&start=1410158341&end=1410499372"

    payload = { 'command': 'returnTradeHistory'}
    url = f"https://poloniex.com/public?command=returnTradeHistory"
    
    if symbol is None:
        return None

    symbol = check_convert_symbol(symbol)
    # payload['currencyPair'] = symbol
    url = f"{url}&currencyPair={symbol}"
    # url = f"{url}&currencyPair={symbol}"

    if start and end:
        # payload['start'] = start
        # payload['end'] = end
        url = f"{url}&start={start}&end={end}"
    
    data = get_request(url) # returned as json

    return [data, symbol, start, end]

    '''[
    {
        "globalTradeID": 606194436,
        "tradeID": 52944618,
        "date": "2021-10-05 12:54:30",
        "type": "buy",
        "rate": "0.06915192",
        "amount": "0.00000028",
        "total": "0.00000001",
        "orderNumber": 971265513397
    },]'''

def return_open_orders(symbol=None):
    """
    Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_ETH". Set "currencyPair" to "all" to return open orders for all markets. Note that the "startingAmount" is not the order placement amount but it is the starting amount of the open order in the book, which excludes any amount that was immediately filled before the order is posted on the book.
    """
    # # Note: set the nonce to the current milliseconds. For example: date +%s00000
    # echo -n "command=returnOpenOrders&currencyPair=BTC_ETH&nonce=154264078495300" | \
    # openssl sha512 -hmac $API_SECRET
    
    """Input Fields
    Field 	Description
    currencyPair 	A string that defines the market, "USDT_BTC" for example. Use "all" for all markets.
    """
    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'returnOpenOrders'}

    if symbol is None:
        return

    symbol = check_convert_symbol(symbol)
    payload['currencyPair'] = symbol

    data = post_request(payload, headers)
    return [symbol] + data
    
    """
    Output Fields
    Field 	Description
    orderNumber 	The number uniquely identifying this order.
    type 	Denotes this order as a "buy" or "sell".
    rate 	The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    startingAmount 	The size of the original order.
    amount 	The amount left to fill in this order.
    total 	The total cost of this order in base units.
    date 	The UTC date of order creation.
    margin 	Denotes this as a margin order (1) or not. (0)
    clientOrderId 	User specified 64-bit integer identifier.
    """


def return_order_book(symbol=None, depth=15):
    """
    Request Parameter 	Description
    currencyPair 	A string that defines the market, "USDT_BTC" for example. Use "all" for all markets.
    depth (optional) 	Default depth is 50. Max depth is 100.
    """
    url = f"https://poloniex.com/public?command=returnOrderBook"
    
    if symbol is None:
        return None
    symbol = check_convert_symbol(symbol)

    url = f"{url}&currencyPair={symbol}"
    # depth
    url = f"{url}&depth={depth}"
    
    data = get_request(url) # returned as json

    return data + [symbol, depth]

    """
    Field 	Description
    asks 	An array of price aggregated offers in the book ordered from low to high price.
    bids 	An array of price aggregated bids in the book ordered from high to low price.
    isFrozen 	Indicates if trading the market is currently disabled or not.
    postOnly 	Indicates that orders posted to the market (new or move) must be non-matching orders (no taker orders) or canceling open orders. Any orders that would match will be rejected.
    seq 	An always-incrementing sequence number for this market.
    """

def return_ticker():
    """
    Field 	Description
    id 	            Id of the currency pair.
    last 	        Execution price for the most recent trade for this pair.
    lowestAsk 	    Lowest current purchase price for this asset.
    highestBid 	    Highest current sale price for this asset.
    percentChange 	Price change percentage.
    baseVolume 	    Base units traded in the last 24 hours.
    quoteVolume 	Quoted units traded in the last 24 hours.
    isFrozen 	    Indicates if this market is currently trading or not.
    postOnly 	    Indicates that orders posted to the market (new or move) must be non-matching orders (no taker orders) or canceling open orders. Any orders that would match will be rejected.
    high24hr 	    The highest execution price for this pair within the last 24 hours.
    low24hr 	    The lowest execution price for this pair within the last 24 hours.
    """
    url = f"https://poloniex.com/public?command=returnTicker"
    
    # if symbol is None:
    #     return None

    # symbol = check_convert_symbol(symbol)
    # payload['currencyPair'] = symbol
    # url = f"{url}&currencyPair={symbol}"
    # url = f"{url}&currencyPair={symbol}"

    # if start and end:
        # payload['start'] = start
        # payload['end'] = end
        # url = f"{url}&start={start}&end={end}"
    
    return get_request(url) #, symbol=None) #, symbol) # returned as json


def return_24hour_volume():
    url = "https://poloniex.com/public?command=return24hVolume"

    """
    # Example output:
    {
    "BTC_BTS": {
        "BTC": "0.28698296",
        "BTS": "328356.84081156"
    },
    """
    return get_request(url) #, symbol=None) #, symbol) # returned as json


def return_tradable_balances():
    # Returns your current tradable balances for each currency in each market for which margin trading is enabled. Please note that these balances may vary continually with market conditions.

    # https://docs.poloniex.com/#returnMarginAccountSummary

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'returnTradableBalances'}
    
    return post_request(payload, headers)

def return_chart_data(symbol=None, start=None, end=None, interval=14400):
    """
    Returns candlestick chart data. Required GET parameters are "currencyPair", "period" (candlestick period in seconds; valid values are 300, 900, 1800, 7200, 14400, and 86400), "start", and "end". "Start" and "end" are given in UNIX timestamp format and used to specify the date range for the data returned.
    """
    # curl "https://poloniex.com/public?command=returnChartData&currencyPair=BTC_XMR&start=1546300800&end=1546646400&period=14400"

    """
    Fields include:
    Input Fields
    Field 	Description
    currencyPair 	A string that defines the market, "USDT_BTC" for example.
    period 	Candlestick period in seconds. Valid values are 300, 900, 1800, 7200, 14400, and 86400.
    start 	The start of the window in seconds since the unix epoch.
    end 	The end of the window in seconds since the unix epoch.
    """
    url = "https://poloniex.com/public?command=returnChartData"

    if symbol is None:
        return None

    symbol = check_convert_symbol(symbol)
    # payload['currencyPair'] = symbol
    url = f"{url}&currencyPair={symbol}"
    # url = f"{url}&currencyPair={symbol}"

    if start and end:
        # payload['start'] = start
        # payload['end'] = end
        url = f"{url}&start={start}&end={end}"

    url = f"{url}&period={interval}"
    
    data = get_request(url) #, symbol) # returned as json
    
    return data + [symbol, interval, start, end]

    """
    Output Fields
    Field 	Description
    date 	The UTC date for this candle in miliseconds since the Unix epoch.
    high 	The highest price for this asset within this candle.
    low 	The lowest price for this asset within this candle.
    open 	The price for this asset at the start of the candle.
    close 	The price for this asset at the end of the candle.
    volume 	The total amount of this asset transacted within this candle.
    quoteVolume 	The total amount of base currency transacted for this asset within this candle.
    weightedAverage 	The average price paid for this asset within this candle.
    """

def return_deposit_addresses():
    """
    Returns all of your deposit addresses.

    Some currencies use a common deposit address for everyone on the exchange and designate the account for which this payment is destined by including a payment ID field. In these cases, use returnCurrencies to look up the mainAccount for the currency to find the deposit address and use the address returned here in the payment ID field. Note: returnCurrencies will only include a mainAccount property for currencies which require a payment ID."""

    # https://docs.poloniex.com/#returnDepositAddresses

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'returnDepositAddresses'}
    
    return post_request(payload, headers)

def return_order_trades(orderNumber = None):
    """
    Returns all trades involving a given order, specified by the "orderNumber" POST parameter. If no trades for the order have occurred or you specify an order that does not belong to you, you will receive an error. See the documentation here for how to use the information from returnOrderTrades and returnOrderStatus to determine various status information about an 
    order.
    """

    """Input Fields
    Field 	Description
    orderNumber 	The order number whose trades you wish to query."""

    if orderNumber is None:
        return None

    # https://docs.poloniex.com/#returnOrderTrades

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'returnOrderTrades'}
    payload['orderNumber'] = orderNumber
    
    return post_request(payload, headers)

    """Output Fields
    Field 	Description
    globalTradeID 	The globally unique identifier of this trade.
    tradeID 	    The identifier of this trade unique only within this trading pair.
    currencyPair 	A string that defines the market, "USDT_BTC" for example.
    type 	        Denotes a "buy" or a "sell" execution.
    rate 	        The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    amount 	        The amount transacted in this trade.
    total 	        The total cost in base units of this trade.
    fee 	        The fee paid for this trade.
    date 	        The UTC date at which this trade executed."""

def return_order_status(orderNumber=None):
    """ Returns the status of a given order, specified by the "orderNumber" POST parameter. If the specified orderNumber is not open, or it is not yours, you will receive an error.

    Note that returnOrderStatus, in concert with returnOrderTrades, can be used to determine various status information about an order:"""

    """
    If returnOrderStatus returns status: "Open", the order is fully open.
    If returnOrderStatus returns status: "Partially filled", the order is partially filled, and returnOrderTrades may be used to find the list of those fills.
    If returnOrderStatus returns an error and returnOrderTrades returns an error, then the order was cancelled before it was filled.
    If returnOrderStatus returns an error and returnOrderTrades returns a list of trades, then the order had fills and is no longer open (due to being completely filled, or partially filled and then cancelled)."""

    """Input Fields
    Field 	Description
    orderNumber 	The identifier of the order to return."""

    if orderNumber is None:
        return None

    # https://docs.poloniex.com/#returnOrderStatus

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'returnOrderStatus'}
    payload['orderNumber'] = orderNumber
    
    return post_request(payload, headers)
    """Output Field
    Field 	Description
    status 	Designates this order's fill state.
    rate 	The price. Units are market quote currency. Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    amount 	The amount of tokens remaining unfilled in this order.
    currencyPair 	A string that defines the market, "USDT_BTC" for example.
    date 	The UTC date this order was created.
    total 	The total value of this order.
    type 	Designates a buy or a sell order.
    startingAmount 	The original order's amount."""

def move_order(orderNumber=None, order_id=None, quote_price=None):
    """    Cancels an order and places a new one of the same type in a single atomic transaction, meaning either both operations will succeed or both will fail. Required POST parameters are "orderNumber" and "rate"; you may optionally specify "amount" if you wish to change the amount of the new order. "postOnly" or "immediateOrCancel" may be specified for exchange orders, but will have no effect on margin orders."""

    """Input Fields
    Field 	Description
    orderNumber 	The identity number of the order to be canceled.
    clientOrderId 	(optional) User specified 64-bit integer identifier to be associated with the new order being placed. Must be unique across all open orders for each account.
    rate 	        The price. Units are market quote currency. 
                    Eg USDT_BTC market, the value of this field would be around 10,000. Naturally this will be dated quickly but should give the idea.
    amount 	        (optional) The amount of tokens in this order."""

    rate = quote_price

    if orderNumber is None:
        return None

    # https://docs.poloniex.com/#returnOrderTrades

    headers = { 'nonce': '',
                'Key' : '',
                'Sign': '',}
    payload = { 'command': 'moveOrder'}
    payload['orderNumber'] = orderNumber
    payload['clientOrderId'] = order_id if order_id else ''
    payload['rate'] = quote_price if quote_price != 0.0 else ''
    payload['amount'] = amount if amount else ''

    # return post_request(payload, headers)



if __name__ == '__main__':
    import pandas as pd
    from uuid import uuid4
    def main(): pass

    # # SELL <- EXIT
    # symbol = 'btc/usdt'
    # order_id = str(uuid4)
    # quote_price = 3213685.465546546
    # fok = True
    # ioc = False
    # nly = False
    # dj = exit(symbol=symbol, order_id=order_id, quote_price=quote_price, fillOrKill=fok, immediateOrCancel=ioc, postOnly=nly)
    # print(dj)

    # # BUY <- ENTER
    # symbol = 'btc/usdt'
    # order_id = str(uuid4)
    # quote_price = 1213685.465546546
    # fok = True
    # ioc = False
    # nly = False
    # dj = enter(symbol=symbol, order_id=order_id, quote_price=quote_price, fillOrKill=fok, immediateOrCancel=ioc, postOnly=nly)
    # print(dj)
    # # # MOVE ORDER
    # # # TODO: TEST
    # # ...

    # # MARGIN BUY <- M_ENTER
    # symbol = 'btc/usdt'
    # order_id = str(uuid4)
    # quote_price = 1213685.465546546
    # amount = '?????'
    # m_enter(symbol=symbol, order_id=order_id, quote_price=quote_price, amount=amount)
    
    # # MARGIN SELL <- M_SELL
    # symbol = 'btc/usdt'
    # order_id = str(uuid4)
    # quote_price = 3213685.465546546
    # amount = '?????'
    # m_exit(symbol=symbol, order_id=order_id, quote_price=quote_price, amount=amount)

    # # RETURN ORDER STATUS
    # dj = return_order_status(order_id=None)
    # print(dj)
    
    # # RETURN ORDER TRADES # TODO: orderNumber a.k.a order_id to test
    # dj = return_order_trades(orderNumber=None)
    # print(dj)
    
    # # RETURN DEPOSIT ADDRESSES
    # dj = return_deposit_addresses()
    # print(dj)
    
    # # RETURN OPEN ORDERS
    # dj = return_open_orders('BTC/USDT')
    # print(dj)

    # # # RETURN CHART DATA # TODO: get start and end times
    # end = datetime.datetime.utcnow()
    # backby = datetime.timedelta(hours=2)
    # start = end - backby
    # print(f"{start = }")
    # print(f"{end = }")
    # # start = datetime.datetime.timestamp(start) #// 10e8
    # # end = datetime.datetime.timestamp(end) #// 10e8
    # # start = start.strftime("%s")
    # # end = end.strftime("%s")
    # # convert to unix time
    # start = pd.Timestamp(start).value // 10e8
    # end = pd.Timestamp(end).value // 10e8
    # print(start)
    # print(end)
    # dj = return_chart_data('btc/usdt', interval=1800, start=start, end=end)
    # print(dj)
    # zipped= zip(dj[0].columns.tolist(), dj[0].dtypes)
    # for i in zipped: print(i)
    
    # # # RETURN CURRENCIES
    # dj = return_currencies()
    # print(dj)
    # print(dj[0])
    # print(dj[0].T)

    # # # RETURN ORDER BOOK
    # # # isFrozen and postOnly need to be checked re. what's going on with trading!!
    # # dj = return_order_book('BTC/USDT')
    # # print(dj)
    # dj = return_order_book('BTC_ETH')
    # print(dj)
    # print(dj[0])
    # # print(dj[0].T)

    # # # RETURN TRADE HISTORY
    # dj = return_trade_history('BTC/USDT')
    # print(dj)
    # print(dj[0])
    # # print(dj[0].T)
    # # dj = return_trade_history('BTC_ETH')
    # # print(dj)

    # # RETURN TICKER
    # #TODO: create tables off of ticker updates, 1 min?
    dj = return_ticker()[0].T

    print(dj)
    # tables = dj[0].columns
    # print(tables)
    # # print(dj[0])
    # print(dj[0].T)
    # cols = dj[0].T.columns
    # print(cols)
    # ticker_cols = ['id', 'last', 'lowestAsk', 'highestBid', 'percentChange', 'baseVolume', 'quoteVolume', 'isFrozen', 'postOnly', 'marginTradingEnabled', 'high24hr', 'low24hr']
    # print('stop')
    # for each entry, a table is populated, 
    # df[0].T is split, new label on 
    # table = symbol()
    #   pair_name, pair_id, exchange_id(gen), ccxt_name(gen), 
    # table = interval()
    # df.iloc[-10:-1, :8]
    # how to 'label' the Name column following df.T (transposition of orginal df)
    '''

    id        last   lowestAsk  highestBid percentChange  ... isFrozen postOnly marginTradingEnabled     high24hr     low24hr
BTC_BTS      14  0.00000071  0.00000072  0.00000071   -0.01388888  ...        0        0                    0   0.00000072  0.00000070
    
    '''


    # # # RETURN 24HOUR VOLUME
    # # # volume comparisons between timeframes against top of day totals
    # dj = return_24hour_volume()
    # # print(dj)
    # print(dj[0])
    # print(dj[0].T)
   
    # # # TRADABLE BALANCES
    # dj = return_tradable_balances()
    # # not req'd - df = pd.DataFrame.from_dict(dj)
    # print(dj)
    # # print(dj[0])
    # # print(dj[0].T)
    # # df.to_csv(os.path.join(basepath, 'margin_tradable_balances_2.csv'), encoding='utf-8')

    # # COMPLETE BALANCES
    # dj = get_complete_balances() # is a response object with results data.content, data.text, data.json(), methods which consume the response object
    # print(dj)
    # print(dj[0])
    # # print(dj[0].T)
    # # df.to_csv(os.path.join(basepath, 'completeBalances.csv'), encoding='utf-8')

    # # MARGIN SUMMARY
    # dj = return_margin_summary()
    # print(dj[0])
    # # print(dj[0].T)
    # print(dj)



    # print(dj.T)
    # margin_summary_keys = dj.keys()
    # print(margin_summary_keys)
    # # idx = pd.Index(margin_summary_keys)
    # idx = pd.Index(range(len(dj)+1))
    # df = pd.DataFrame(data=dj, index=idx) #columns=margin_summary_keys) #
    # print(df)
    # # print(df.T)
    # # TODO: # data, index, columns, dtype=dtype, copy=copy, typ=manager
    # df.to_csv(os.path.join(basepath, 'margin_summary.csv'), encoding='utf-8')

    # return response




