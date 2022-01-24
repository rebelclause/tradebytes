import asyncio
from asyncio import Queue, LifoQueue, PriorityQueue
from dataclasses import MISSING, dataclass, field
from enum import Enum, auto
from typing import Any, Optional, Union, TypeVar, Awaitable, Callable, ClassVar
import datetime
import random
from random import choice, randint
from decimal import Decimal

malformed = []

# Signals are binary; off or on, buy or sell, enter or exit.
# Markets are diverse, but each offers a similarly binary choice -- with caveats, most of those being the type of entry, or the partative nature of an exit, full or part. All of these pivot on price. What price are you willing to pay for an asset. What price are you willing to let an asset go for, to a buyer, or a pool of buyers?
# OrderType classifies LONG, SHORT, and EXIT. In a sense, LONG and SHORT are both of an ENTRY class because the in_position standing of the asset remains True while either LONG or SHORT applies.
# EXIT and LONG are the only true opposites in the OrderType class.
# Refactoring this relationship will push decision-making to a class, or set of classes, already implied as possibly including ENTRY (LONG & SHORT) and EXIT (EXIT), but to account for their application of logic to determining price it is necessary to know both in_position and Market by its type, and consequently which of the REST API calls or params need to be called/assembled to accomplish the task of transacting and confirming the success or failure of any given Order.

@dataclass
class OrderType(Enum):
    LONG: str = auto()
    SHORT: str = auto()
    EXIT: str = auto()

@dataclass
class Balance:
    balance: Decimal
    price_enter: Decimal
    price_exit: Decimal
    time_of_last_check: datetime

@dataclass
class Symbol:
    # (init=True, repr=True, eq=False, order=False, unsafe_hash=False, frozen=False, match_args=True, kw_only=False, slots=False)
    symbol: str
    symbol_id: int
    interval: int
    q: Queue
    _signal: OrderType = field(init=False, default=MISSING)
    _price: float  = field(init=False, default=MISSING) # Decimal
    _task: Any = field(init=False, default=MISSING)
    # price_enter
    # price_exit
    # balance

    def __post_init__(self):
        self.price = MISSING # missing is a sentinel value not ordinarily used here, not recommended, useful when init=False and there is no default value
        self._signal = MISSING
        self.task = MISSING # warning will include 'self', an instance of Symbol, as a positional param

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        self._price = price

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task

    # async def signal(self, *, signal:OrderType=None):
    async def signal(self, signal):
        global malformed
        self._signal = signal

        if self._signal.name == 'EXIT':
            # print('EXIT')
            priority = 1
            order = 1

        if self._signal.name == 'SHORT':
            # print('SHORT')
            priority = 1
            order = 3

        if self._signal.name == 'LONG':
            # print('LONG')
            priority = 1
            order = 2

        try:
            task = OrderTask(priority, order, "High priority", self)
            self.q.put_nowait(task)
            # self.q.put(self._task)
        except (UnboundLocalError, TypeError, Exception) as e:
            print(e)
            malformed.append((self.symbol, self._signal.name, datetime.datetime.utcnow()))


@dataclass(order=True)
class OrderTask:
    priority: int
    order: int
    data: str = field(compare=False)
    symbol: Symbol = field(compare=False)


async def order_place(task):
    global malformed
    symbol = task.symbol.symbol
    price = task.symbol.price
    signal = task.symbol._signal.name
    message = "Exchange API Buy or Sell @ Market"
    # while len(malformed) > 0:
    #     print(malformed.pop())
    return f"<ORDER_ID>, {signal=}, {symbol=}, {price=}"

async def order_long(task):
    try:
        task.symbol.price = await order_long_price(task.symbol.symbol)
        result = await order_place(task)
        print(result)
        print(f"{task.symbol.symbol=} {task.symbol.price=} -listing order details, -filing order number")
    except Exception as e:
        print("LONG failed with: ", e)

async def order_short(task):
    try:
        task.symbol.price = await order_short_price(task)
        result = await order_place(task)
        print(result)
        print(f"{task.symbol.symbol=} {task.symbol.price=} -listing order details, -filing order number")
    except Exception as e:
        print("SHORT failed with: ", e)

async def order_exit(task):
    # obtain price in the appropriate market to the up-to-date Symbol instance
    try:
        task.symbol.price = await order_exit_price(task)
        result = await order_place(task)
        print(result)    
        print(f"{task.symbol.symbol=} {task.symbol.price=} -listing order details, -filing order number")
    except Exception as e:
        print("EXIT failed with ", e) # TODO: log these errors

async def order_long_price(task):
    # returns price on the symbol to the queue signal handler assigned from orderbook
    p = float(1.0000000000)
    print(f"orderbook LONG")
    return p

async def order_short_price(task):
    # TODO: request orderbook price for a SHORT
    p = float(1.0000000000)
    print(f"orderbook SHORT") #{task.symbol.symbol} @ {task.symbol.price}")
    return p

async def order_exit_price(task):
    # TODO: request orderbook price for an EXIT
    p = float(1.0000000000)
    print(f"orderbook EXIT")
    return p

async def delay(seconds=None):
    if seconds is None:
        seconds = random.randint(5, 12)
    await asyncio.sleep(seconds)

async def producer(queue: Queue=None):
    # 111. make a batch of symbols
    global q
    symbols = []
    bases = ['btc', 'eth', 'usd', 'cad', 'usdt', 'usdc', 'chf', 'aud', 'eur']
    quotes = ['eos', 'xrp', 'ada', 'matic', 'atom', 'nrm', 'aug', 'loom', 'bch', 'bchsv']
    symbol_id = 0
    intervals = [1, 5, 10, 15, 30, 60, 120, 240, 300, 360, 1440, 2880]
    for base in bases:
        for quote in quotes:
            symbol_id += 1
            # signature = Symbol(symbol, symbol_id, interval, q)
            symbols.append(Symbol(f"{base}/{quote}".upper(), symbol_id, choice(intervals), q))
    signals = [OrderType.LONG, OrderType.EXIT, OrderType.SHORT]

    # 222. mock a signal to each symbol,
    #################################
    # # for entry onto the queue
    # for symbol in symbols: 
    #     # TODO: subclass list of symbols with __aenter__ and __aexit__ dunders so async for can be used
    #     # q.put_nowait(task)
    #     # print(f"{symbol=}")
    #     # for k, v in symbol.__dict__.items():
    #     #     print(k,v)
    #     # for k in symbol.__dict__.keys():
    #     #     print(k)
    #     alert = choice(signals)
    #     # print(choice)
    #     await delay(.1)
    #     symbol.signal(alert) #FIXME: was an async awaitable on Symbol
    #################################
    
    # 222. replaced for loop with a gather, but if one task is canceled they all get canceled.
    asyncio.gather(*[symbol.signal(choice(signals)) for symbol in symbols])

    await delay()

async def worker(queue: Queue):
    while True:
        try:
            while not queue.empty():

                print(q.qsize())
                task = await queue.get()

                if task.symbol._signal.name == "EXIT":
                    print("EXIT")
                    await order_exit(task)
                    q.task_done()

                if task.symbol._signal.name == "SHORT":
                    print("SHORT")
                    await order_short(task)
                    q.task_done()

                if task.symbol._signal.name == "LONG":
                    print("LONG")
                    await order_long(task)
                    q.task_done()
                print(q.qsize())
        except Exception as e:
            print('worker ', e)
            continue
        print("Perpetually generate symbols and signals...")
        await producer()

async def main():
    global q
    q = PriorityQueue(0)

    worker_task = asyncio.create_task(worker(q))

    # single
    ## UNCOMMENT the try block to run for a review
    # of sequential messsages; from instance,
    # queue to handling functions and back
    # try:
    #     # instance a 'primer' Symbol and send it a Signal
    #     xtcbre = Symbol("xtc/bre".upper(), 8080, 56, q)
    #     # print(f"{xtcbre =}")
    #     signals = [OrderType.LONG, OrderType.EXIT, OrderType.SHORT]
    #     await xtcbre.signal(OrderType.EXIT)
    # except Exception as e:
    #     print(e)

    # multiple
    # for x in range(2022):
    #     await xtcbre.signal(choice(signals))

    # integrated re(batch) # old version primer, might work...
    # await producer()

    # await asyncio.gather(q.join(), worker_task) 
    await asyncio.gather(worker_task)


asyncio.run(main(), debug=True)
