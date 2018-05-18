# Strategy folder
contains classes to implement trading strategies.

Trading Strategy gets as an imput a current time, coin, source etc and provide as an output a subselection of already generated Signasl (from Signal table) which constitute the given strategy.

StrategyRef is a DB linked model class which is a list(reference) of
all strategies we have in the system

before we run it first time we have to pre-populate DB table with existing strateies by calling add_all_strategies() method

The rest of the classes are non-django-models classes which implements all possible strategies by implementing two common methods:

- check_signal_now(), at a given time point returns a signal belonging to a particular strategy if any. We call it if we need to check if there is s signal at the current time point
- get_all_signals_in_time_period(), the same but for a period of time. We can you it for a back testing of a particlar strategy, so it returnd all signal which a particular strategy emits





#### NOTE.
- each python file can contain several strategies belonging to one group
- In future some advanced strategies shall use and generate not Signals from signal table but Evennts_elementary as well
- TODO: for each strategy we have to add a mechanizm to check that one signal goes exactly after another one... not repeting


- another idea to implement strategy: not by subselecting signals but by providing a continious Strategy function which at every given moment of time will say whether it is a buy or sell momeent (green/red)