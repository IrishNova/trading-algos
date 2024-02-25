# Learn about trading algos written in Python

Overview
Automated trading strategies, more commonly referred to as algorithms, have grown exponentially in use by institutional and retail traders. What once was only able to be done on a pit floor, now can be executed digitally, allowing for more and more complex strategies to be implemented. This repository is a portfolio of different trading algorithms. It shows how Python can be used to implement automated trading strategies. 

_Models_

SimpleAlgo - This is the most basic, stripped-down version of a research algo I could come up with. It's intended to show people who are familiar with excel, the general process of creating a research algo in Python. Data is imported from a csv to a DataFrame, and signals are built up column by column. A column with Boolean operators (True/False) is used to determine long or short positions based on the signal. Next, non-log returns are calculated and applied to a $100,000 starting account balance. No transaction costs are added, slippage is not modeled. Again, this is an incredibly basic model. 
