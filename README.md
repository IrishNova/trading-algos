# Learn about trading algos written in Python

_Overview_

Automated trading strategies, more commonly referred to as algorithms, have grown exponentially in use by institutional and retail traders. What once was only able to be done on a pit floor, now can be executed digitally, allowing for more and more complex strategies to be implemented. This repository is a portfolio of different trading algorithms. It shows how Python can be used to research and automate trading strategies. 

_Research vs Production_

There's a large difference between research algos/models and production (live) algos. The main difference is that I prefer to use a dataframe libarary called Pandas for researching, and pure Python or C++ for production. Pandas makes research go a lot faster but is too slow and clunky for running in production. 

_Models_

simple_backtest - This is the most basic, stripped-down version of a research algo I could come up with. It's intended to show people who are familiar with excel, the general process of creating a research algo in Python. Data is imported from a csv to a DataFrame, and signals are built up column by column. A column with Boolean operators (True/False) is used to determine long or short positions based on the signal. Next, non-log returns are calculated and applied to a $100,000 starting account balance. No transaction costs are added, slippage is not modeled. Again, this is an incredibly basic model. 

basic_research_model - A robust backtesting framework that's a copy of how I build them for researching strategies. As it stands now, this is just the simulation part that iterates over the dataframe and chooses if it should buy, sell, or stay flat (the logic). Risk management, trade recording, and performance calculations are not performed.  Still, there's a lot to view here. Focus on how I use Boolean operators (True/False) to dictate the logic within the algorithm and choose which methods to call.       
