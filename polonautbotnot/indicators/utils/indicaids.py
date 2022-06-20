import os, sys

from math import *
from math import pi
print("indicaids hello: ", pi)
from pygame import mixer
mixer.init() 

# from create_ohlcv_tables.indicators.utils.moving_avgs import sma, \
#    ema, hma, macd
basedir = os.path.dirname(os.path.abspath(__file__))
# print(basedir)

def play_enter():
    bigsound = os.path.join(basedir, 'bigsound_bell.ogg')
    # https://bigsoundbank.com/detail-0292-small-bell-1.html
    sound=mixer.Sound(bigsound)
    sound.play()

def play_exit():
    bigsound = os.path.join(basedir, 'bigsound_beep.ogg')
    # https://bigsoundbank.com/detail-2252-detector-2.html
    sound=mixer.Sound(bigsound)
    sound.play()

# some of these are placeholders for pine functions

def _input(): pass

def timenow(): pass

def ceil(): pass # builtin math.ceil

# def atr(): pass # in ./utils.atr.py 

def crossover(a, b):
    # function to replace pinescript's crossover
    result = a > b #True if a > b else False
    return result

def crossunder(a, b):
    # function to replace pinescript's crossunder
    result = a < b #True if a > b else False
    return result

def plot(fn):
    # TODO: pinscript plot() ????
    pass

def higher(a, b): pass

def lower(a, b): pass


from dataclasses import dataclass, field
@dataclass
class Color: # roygbiv
    green: str = field(default='🟢') 
    blue: str = field(default='🔵')
    fuchsia: str = field(default='🌒')
    lime: str = field(default='🌘')
    red: str = field(default='🛑')
    white: str = field(default='⚪') # ⬜
    black: str = field(default='⚫')
    maroon: str = field(default='🟤')
    navy: str = field(default='🌓') # first quarter, last quarter 🌗
    yellow: str = field(default='🟡')
    purple: str = field(default='🟣')
    navy: str = field(default='X') # 💎
    orange: str = field(default='🟠')
    violet: str = field(default='❕')
    indigo: str = field(default='🇨🇦')

'''
    :red_circle:
    :yellow_circle:
    :large_blue_circle:
    :purple_circle:
    :black_circle:
    :green_circle:
    :orange_circle:
    :brown_circle:
    :white_circle:
'''
# https://unicode.org/emoji/charts/full-emoji-list.html#1f6d1
# signs = [🛑, 🛑, 🛑, 🛑, 🛑, 🛑]

color = Color()

@dataclass
class Shape:
    pass  

shape = Shape()


'''color = #
moons_of_uranus[{"new_moon": 🌑, "waxing": 🌒, "waxing_crescent": 	, "first":
🌓, }]
# first quarter moon
# 979 	U+1F314 	🌔 	🌔 	🌔 	🌔 	🌔 	🌔 	🌔 	🌔 	🌔 	— 	🌔 	🌔 	waxing gibbous moon
# 980 	U+1F315 	🌕 	🌕 	🌕 	🌕 	🌕 	🌕 	🌕 	🌕 	🌕 	— 	🌕 	— 	full moon
# 981 	U+1F316 	🌖 	🌖 	🌖 	🌖 	🌖 	🌖 	🌖 	🌖 	— 	— 	— 	— 	waning gibbous moon
# 982 	U+1F317 	🌗 	🌗 	🌗 	🌗 	🌗 	🌗 	🌗 	🌗 	— 	— 	— 	— 	last quarter moon
# 983 	U+1F318 	🌘 	🌘 	🌘 	🌘 	🌘 	🌘 	🌘 	🌘 	—]
'''


