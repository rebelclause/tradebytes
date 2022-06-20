import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import time
import math
from math import floor, fmod

# from create_ohlcv_tables.database import sql_to_df

class FeatureNotImplemented(Exception):
    pass

class Timeframes:
    # possibly do lookup on db depending on symbol_id, interval_id, exchange_id coincidence
    @staticmethod
    async def get_timeframe(value):
        timeframes = {'5m': 300, '15m': 900, '30m': 1800, '2h': 7200, '4h': 14400, '1d': 86400}

        if isinstance(value, int):
            if value in timeframes.values():
                return value
            else:
                raise FeatureNotImplemented
    

        if isinstance(value, str):
            try:
                valid = timeframes.get(value, 300)
                return valid
            except Exception as e:
                print(e)
                return 300

def sleep_to_next_interval_clock_top():
        """setup to run schedule"""
        # copied from database.py FIXME: intervals as per unique symbol class instances populated by symbol specific data, so this may yet be moved into a 'symbol' module, or into a base class for each symbol running on the asyncio event loop (when that happens in the transition from sync to asyncio...)
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
        sleep(snore)
        # sleep(10)


def elapsed_time(time_in_seconds=0, floor=True):
    if time_in_seconds != 0:
        weeks = fmod(time_in_seconds / (3600 * 24 * 7), 4)
        days = fmod(time_in_seconds / (3600 * 24), 7)
        hours = fmod(time_in_seconds / 3600, 24)
        minutes = fmod(time_in_seconds / 60, 60)
        seconds = fmod(time_in_seconds, 60)
        if floor:
            return math.floor(weeks), math.floor(days), math.floor(hours), math.floor(minutes), math.floor(seconds)
        return (weeks, days, hours, minutes, seconds)
    return None

def valid_interval_list(clock_len=60, interval=5):
    # in minutes
    # https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
    if isinstance(interval, str):
        interval = [int(s) for s in interval.split() if interval.isdigit()][0]
        print(interval)
    import pandas as pd
    from math import fmod
    # clock_len = 60
    # interval =3
    return [x for x in range(clock_len+1) if fmod(x, interval) == 0.0]
    # FIXME: see notes below

class myIterator:
	def __init__(self, input):  # __init__ to read in an input list
		self.listing = input
		self.max = len(input)  # start an index of
		self.index = -1
	def __iter__(self):
		return(self)  # This simply points the object back to itself when called
	def __next__(self):  # The essential iteration loop
		self.index += 1 # Increment index by 1 on each loop
		if self.index >= self.max:  # If we've reached the end of the list of items
			raise StopIteration    # This will stop iteration after the list is exhausted
		return(self.listing[self.index])
		
'''
# https://wellsr.com/python/basics/python-class-objects-and-class-applications/
listing = ["The", "best", "of", "times."]
x = myIterator(listing)
for item in x:
	print(item)'''



class Pagination:
    hour_in_seconds = 60*60
    day_in_seconds = 60*60*24
    def __init__(self, most_recent, now, max_intervals=4):
        # obtain most recent ?
        self.most_recent = most_recent
        self.now = now
        self.max_intervals = max_intervals
        self.elapsed = self.now - most_recent
        self.elapsed_seconds = self.elapsed.seconds # dt object
        self.elapsed_intervals = (self.elapsed_seconds / self.max_intervals * Pagination.hour_in_seconds) # in hours

    def get_periods_gen(self):
        # in hours, then seconds
        periods_list = []
        for i in self.chunk_interval(self.elapsed_seconds, self.elapsed_intervals):
            # add an hour of minutes for each fetch request
            # update most_recent {i}
            # start = self.most_recent - datetime.timedelta(hours=1)
            # end = start + datetime.timedelta(hours=self.max_interval)
            new_start = self.now - datetime.timedelta(seconds=i)
            start = new_start - datetime.timedelta(hours=1)
            end = start + datetime.timedelta(hours=self.max_intervals)
            # data = pd.period_range(start=start, end=end, freq='h')
            # print(data)
            periods_list.append((start, end))
        # final period
        start = self.now - datetime.timedelta(hours=2)
        periods_list.append((start, self.now))
        return periods_list

    def chunk_interval(self, n, intervals):
        # in hours # TODO: intervals is max_window, in hours, of each chunk of time between 0 and total time not to exceed max_window, clarify params and the rest
        intervals = 4
        x = n/(int(intervals))
        x = [i*x for i in range(1, int(intervals) + 1, 1)]
        x = sorted(x, reverse=True)
        print(len(x))
        print(x)
        for i in range(int(intervals)):
            yield x[i]
            # yield x if i == 0 else x += x if (x + x < n + x *.25) else None # ? wt(f)

def slices(interval=300, start_utc=None, end_utc=None):
    timeframes = {'5m': 300, '15m': 900, '30m': 1800, '2h': 7200, '4h': 14400, '1d': 86400}

    # FIXME: param 'slice', interval

    mode = []
    # mode = ['init']
    # mode=['recovery']

    # modes applicable to individual symbol/table updates on same database
    # FIXME: values transmitted via jobspec, however, no subscription, 
    modes = ['testing', 'production', 'init', 'recovery']

    now = datetime.datetime.utcnow()
    # obtain recovery information 
    # most_recent = sql_to_df('symbol') # $$$$$ rework to produce this datapoint in the flow
    most_recent = now - datetime.timedelta(hours=8)
    # recovery = sql_to_df(tablename) # FIXME: we don't do tablename here, modularize slices as a helper function, moving mode to its own fn/class??? but still in this module? what then is the flow intercession point?

    interval = (interval / 60) # int removed, is now float to accommodate timeframes less than the number of seconds in a minute, TODO: test across inputs to be sure seconds are being sent to this function every single time
    pages = rows = None

    if interval >= 1:
        interval = int(interval)

    if 'testing' in mode:
        test_start = now
        pages = 8

    if 'production' in mode:
        prod_start = now
        pages = 12

    if 'init' in mode:
        from pathlib import Path
        print(Path("..").resolve())
        init_start = most_recent = now - datetime.timedelta(weeks=2)
        # if it doesn't exist in the tablename re. symbol__interval
        # tr = pd.period_range(start='2017-01-01 8:00', end='2017-01-01 9:00', freq='s')
        # populate and consume generator
        p = Pagination(most_recent, now)
        gen = p.get_periods_gen()
        for i in gen:
            # convert to unix time
            start = pd.Timestamp(i[0]).value // 10e8
            end = pd.Timestamp(i[1]).value // 10e8
            # do_the_run(start, end)
            print(f"{start = }, {end =}")
            
    if 'recovery' in mode:
        # recovery_start = sql_to_df(lastest('recovery'))
        # get latest result from symbol ohlcv table
        # convert date to np.datetime64
        # timedelta from this date to datetime.datetime.utcnow()
        # through an even distribution, or appropriately sliced request timeframes
        pages = Pagination(most_recent, now)
        # range= pd.date_range(start=)
    
    if pages is None:
        pages = 15
    mins = int(interval*pages) #/1.3)

    # nowminute = int(end_utc.minute / interval) * interval
    nowminute = int(now.minute / interval) * interval
    print(f"{nowminute = }")
    
    if start_utc:
        pass
    else:
        # start_utc = datetime.datetime.utcnow() - timedelta(minutes=mins) 
        start_utc = now - timedelta(minutes=mins) 
        print(f"{start_utc}")

    if end_utc:
        pass
    else:
        try:
            end_utc = now.replace(minute=nowminute, second=20, microsecond=0) # nowminute + 1
            print(f"{end_utc = }")
        except Exception as e:
            print(e)
    freq = f'{interval}m' 

    # print(f"{start_utc = } {end_utc = }")

    # convert to unix time
    start = pd.Timestamp(start_utc).value // 10e8
    end = pd.Timestamp(end_utc).value // 10e8
    
    return start, end


def sincemaker(interval=5): 
    #TODO: variable interval support
    # strip the clock back to hours for minute resolution
    nowdate = pd.to_datetime(datetime.datetime.now())
    code = 'h'
    date = np.datetime64(nowdate, code)
##    print(f"np.datetime64 - hour: \t{date}")
    code = 'ms'
    delta = np.timedelta64(interval, code)
    date = np.datetime64(date, code)
    nowminute = int(nowdate.minute / interval) * interval # * (interval *2)
##    print(f"{nowminute = }")
    nowdelta = np.timedelta64(nowminute, code)
    nearestnowdate = date + nowdelta
    nearestnowdate = np.datetime64(nearestnowdate)
##    print(f"{nearestnowdate = }")
    prevdate = nearestnowdate - (delta *288)
    nextdate = nearestnowdate + delta
    tseries = pd.Series([nearestnowdate, prevdate, nextdate]).astype(np.datetime64)
##    print(tseries)
##    print(f"np.datetime64 - delta, in m: \t{prevdate}")
##    print(f"np.datetime64 + delta, in m: \t{nextdate}")
    t0 = time.mktime(tseries[0].timetuple()) #*10**6 # to ms
    t1 = time.mktime(tseries[1].timetuple()) #*10**6 # to ms
##    print(f"{t0 = }")
##    print(f"{t1 = }")

    return t1, t0
##    print(datetime.datetime.fromtimestamp(t0))
##    print(datetime.datetime.fromtimestamp(t1))
 

if __name__ == "__main__":
    # TODO: clock FLAW: would have to plan for tracking the time in on a position for a valid interval reference list to be effective, as intervals mod60 which are not evenly divisible force the clock total to be a factor of the base clock 60 and the interval time, valid intervals outside mod60 do not reconcile against the system clock... for instance 24 in 60 produces 24, 48, and zero, making 12 a valid interval, but extending the clock to 240m while it may roll over at the end of that period, produces values over 60
    # it would be possible to determine the current and next factor of 60 clock top and and substract the next interval from it to deterime a mod60 interval, 
    # so if the interval is 24 and 72 minutes have passed, the next clock top would be 120, and being between 60 and 120, the difference between 72 and 60 would place the next interval at 12, not the clock top...
    # FIXME: the clock done in the naive way produces a 0 for the clock top, and the clock is always normalized to the system time, not the start time of the position, leaving a gap between position entry and the next interval which may be longer (or shorter) than the official interval...

    result = sincemaker(interval = 1)
    print(result[0], " ", result[1])
    print(valid_interval_list(60, 24))
    print(valid_interval_list(240, 24))
    print(valid_interval_list(24, 2))
    l = valid_interval_list(31, 7) # but what if it starts on a different date???q song of the ages...
    print(l)
    l[:] = [x * 5 for x in l]
    print(l)
    print(elapsed_time(30))
    print(elapsed_time(60))
    print(elapsed_time(90))
    print(elapsed_time(3600))
    print(elapsed_time(3720))
    print(elapsed_time(36030))
    print(elapsed_time(363063))
    print(elapsed_time(436306200, floor=False))

     # DATE RANGE
    # *Specifying the values**

    # The next four examples generate the same DatetimeIndex, but vary the combination of start, end and periods.

    # Specify start and end, with the default daily frequency.
    pd.date_range(start='1/1/2018', end='1/08/2018')
    # DatetimeIndex(['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04','2018-01-05', '2018-01-06', '2018-01-07', '2018-01-08'],dtype='datetime64[ns]', freq='D')

    # Specify start and periods, the number of periods (days).
    pd.date_range(start='1/1/2018', periods=8)
    # DatetimeIndex(['2018-01-01', '2018-01-02', '2018-01-03', '2018-01-04','2018-01-05', '2018-01-06', '2018-01-07', '2018-01-08'],dtype='datetime64[ns]', freq='D')

    # Specify end and periods, the number of periods (days).
    pd.date_range(end='1/1/2018', periods=8)
    # DatetimeIndex(['2017-12-25', '2017-12-26', '2017-12-27', '2017-12-28', '2017-12-29', '2017-12-30', '2017-12-31', '2018-01-01'],dtype='datetime64[ns]', freq='D')

    # Specify start, end, and periods; the frequency is generated automatically (linearly spaced).
    pd.date_range(start='2018-04-24', end='2018-04-27', periods=3)
    # DatetimeIndex(['2018-04-24 00:00:00', '2018-04-25 12:00:00', '2018-04-27 00:00:00'], dtype='datetime64[ns]', freq=None)

    # **Other Parameters**

    # Changed the freq (frequency) to 'M' (month end frequency).
    pd.date_range(start='1/1/2018', periods=5, freq='M')
    # DatetimeIndex(['2018-01-31', '2018-02-28', '2018-03-31', '2018-04-30', '2018-05-31'], dtype='datetime64[ns]', freq='M')

    # Multiples are allowed
    pd.date_range(start='1/1/2018', periods=5, freq='3M')
    # DatetimeIndex(['2018-01-31', '2018-04-30', '2018-07-31', '2018-10-31','2019-01-31'], dtype='datetime64[ns]', freq='3M')

    # freq can also be specified as an Offset object.
    pd.date_range(start='1/1/2018', periods=5, freq=pd.offsets.MonthEnd(3))
    # DatetimeIndex(['2018-01-31', '2018-04-30', '2018-07-31', '2018-10-31', '2019-01-31'], dtype='datetime64[ns]', freq='3M')

    # Specify tz to set the timezone.
    pd.date_range(start='1/1/2018', periods=5, tz='Asia/Tokyo')
    # DatetimeIndex(['2018-01-01 00:00:00+09:00', '2018-01-02 00:00:00+09:00','2018-01-03 00:00:00+09:00', '2018-01-04 00:00:00+09:00','2018-01-05 00:00:00+09:00'], dtype='datetime64[ns, Asia/Tokyo]', freq='D')

    # closed controls whether to include start and end that are on the boundary. The default includes boundary points on either end.
    pd.date_range(start='2017-01-01', end='2017-01-04', closed=None)
    # DatetimeIndex(['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-04'], dtype='datetime64[ns]', freq='D')

    # Use closed='left' to exclude end if it falls on the boundary.
    pd.date_range(start='2017-01-01', end='2017-01-04', closed='left')
    # DatetimeIndex(['2017-01-01', '2017-01-02', '2017-01-03'], dtype='datetime64[ns]', freq='D')

    # Use closed='right' to exclude start if it falls on the boundary.
    pd.date_range(start='2017-01-01', end='2017-01-04', closed='right')
    # DatetimeIndex(['2017-01-02', '2017-01-03', '2017-01-04'], dtype='datetime64[ns]', freq='D')

    # PERIOD
    pd.period_range(start='2017-01-01', end='2018-01-01', freq='M')
    # PeriodIndex(['2017-01', '2017-02', '2017-03', '2017-04', '2017-05', '2017-06','2017-07', '2017-08', '2017-09', '2017-10', '2017-11', '2017-12','2018-01'], dtype='period[M]')

    # If start or end are Period objects, they will be used as anchor endpoints for a PeriodIndex with frequency matching that of the period_range constructor.

    pd.period_range(start=pd.Period('2017Q1', freq='Q'), end=pd.Period('2017Q2', freq='Q'), freq='M')
    # PeriodIndex(['2017-03', '2017-04', '2017-05', '2017-06'], dtype='period[M')
    