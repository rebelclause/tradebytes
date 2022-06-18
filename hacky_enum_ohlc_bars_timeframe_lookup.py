from enum import Enum

valid_frames = {'1m': 60, '3m': 180,'5m': 300, '15m': 900, '30m': 1800, '1h': 3600, '2h': 7200, '4h': 14400, '1d': 86400}

reverse = {}
for k, v in valid_frames.items():
    reverse[v]=k
print(reverse)
# reverse = {60: '1m', 180: '3m', 300: '5m', 900: '15m', 1800: '30m', 3600: '1h', 7200: '2h', 14400: '4h', 86400: '1d'}


new = []
for k, v in valid_frames.items():
    print(f"{v} = {v:d}, {v/3600:.0f}, '{k}'") 
print(new) # find its slightly altered output beneath the Enum declaration

# Please Note: There are better ways to do this, but Enums are standard fare
# in Python with backports into Python2.x versions following adoption,
# so they're worth knowing about and becoming adept at applying correctly
# to the problems they address best, across problem domains and programming languages.
# This example presses on past best practices, however, just to dunder along with it.

# In any case, now the sales brochure is over, run the code against your own dict
# representation of vital and valid timeframes, then copy your terminal output
# to fit it beneath the Enum class declaration below which you'll see
# is already filled out with data, though not perfectly.

# There is an intentional error here, forcing you to choose whether
# you want to use overwrought syntax to reveal the hourly values
# which are calculated above, or to just delete them.

# If you want to calculate them, change the above {v/3600:.0f} to {v/3600:.1f},
# and the table will print with the first decimal included. Where the result
# would not provide an integer representation of the timeframe in hours, you'll find a zero (0).

# If you don't want to keep the floats, you can also get rid of the
# operator overload dunder method hanging on the vframes class.

# You might agree the example is hampered by the fact 
# Python variables can not start with an integer, and there's nothing short
# of changing Python at a fundamental level to be done that could possibly change that.

# Incidentally, 'i' in Enum class variables stands in for 'interval'.
# If you want to learn more about Enums and the many things they can do
# when not being pushed with hacky attempts to bend them 
# around already robust standards. 

# For more and better, visit Python.org at https://docs.python.org/3/library/enum.html.

class vframes(Enum):
    i60 = 60, 0.0, '1m'
    i180 = 180, 0.0, '3m'
    i300 = 300, 0.0, '5m'
    i900 = 900, 0.0, '15m'
    i1800 = 1800, 0.0, '30m'
    i3600 = 3600, 1.0, '1h'
    i7200 = 7200, 2.0, '2h'
    i14400 = 14400, 4.0, '4h'
    i86400 = 86400, 24.0, '1d'

    def __int__(self):
        return self.value[0]

    def __float__(self):
        return self.value[1]

    def __str__(self):
        return self.value[2]
    
print(vframes.i60)
print(int(vframes.i300))
print(int(float(vframes.i3600))) # kinda out there, syntactially speaking...
print(str(vframes.i300))
