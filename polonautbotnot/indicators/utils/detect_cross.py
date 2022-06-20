import pandas as pd
import numpy as np

df = pd.DataFrame({'a': [10, 20, 30, 40, 50], 'b': [0, 10, 40, 45, 50]}, columns = ['a', 'b'])

print(df)

mask = (df['a'].shift()) < (df['b'])

# df['mask'] = df['a'].shift().lt(df['b']) & df['a'].ge(df['b'])
# meme chose
df['mask'] = (df['a'].shift() < df['b']) & (df['a'] >= df['b'])

print(mask)

# print(df['mask'].index.tolist())