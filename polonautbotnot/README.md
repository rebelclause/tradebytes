# Maybe A Backtester Wannabe: IRL, Not A Trading Bot

> Runs with `database.py' after you delete the db (or keep it), and add some valid symbols.

Instead of this monstrosity taking up space beside better projects, it has been virtualized here for the sake of posterity, or maybe, if you agree, posteriority, since, well, ughhhh, it is so ugly...

It was written over three days last year and has never traded a dime never having been outfitted to do so, but on a revisit, thinking there might be code that could be of use for a project I had intended to take live, capturing it in memory well enough to migrate any parts of it into new uses was arduous and time-consuming, a fact made more difficult as variations moved decidedly asyncio, into the world of Python's concurrency model. By rights the part of this project that touches on asyncio should not even work...

Going live was planned for January of this year, however, due to unforeseen circumstances related to the regulatory environment for residents of Ontario coming down from the commission on trade, and the exchange in question's apparent reputation here, residents like myself were forced to leave the exchange. 

No matter, just find a new exchange, and because CCXT was never a part of it, write to a new API, right?

The real quicksand has been working on code reasoning skills by looking at other projects. Getting back to coding should not be a thing in that context, I've learned. Coding while learning a domain is better, even if just parts of it. Who knew: the grind sharpens!?!

Also, please avoid that other Rabbit Hole, believing it's better to merge code than to cobble it quickly from well organized domain comprehension and mature data flow perspectives. I'm sure to have more about that some time soon; without doubt, necessarily, as illustrative, accompanying much better code than you'll find here.

FWIW, you can delete the overlarge `sqlite` db here and then add your own symbols way down beneath the traditional conditional used in Python modules for when they are "__main__", in this case, the file `database.py`. It's a manual process with this thing... and I'm sure the list of symbols isn't even braced in a set, prepared for the day when some route upends the universe of automation to prevent an update from listing a symbol twice.

Oh, and there is no backtesting visualization. And I probably broke supertrend_strategy, on which this was first twisted up. There's some disease around overlong dataframes with no filter, merging or concatenation preparing input date for things like colliding, employing time-honored cross-validation or regression something or other... see here: [scikitlearn: cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html), and maybe part here: [Python Data Science Handbook, (venerable, the)](https://jakevdp.github.io/PythonDataScienceHandbook/index.html), artfully provided by its author Jake VanderPlas, with my gratitude.

Oh, and please forgive the notes in the code. I hope you don't find any expletives or confessionals there I've missed scrubbing away, but I can't look any more... this spaghetti is stuck to the wall, and so over for me.



