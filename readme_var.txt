
"""
Created on Thu Dec 11 15:08:51 2025

@author: ariel
"""


This project computes and visualizes a 14-day 99% historical Value-at-Risk (VaR) for the stETH/ETH basis using CoinGecko Pro as the price data source.

It pulls daily USD prices for:

ETH
stETH

the basis (stETH/ETH) is computed, 14-day returns for the basis ratio and a rolling 100 day window is used to estimate the 1% quantile of the returns (i.e. a 99% VaR)

Plots:

The basis time series, and

The VaR time series (and optionally a shaded confidence band).

The program requires a coingecko pro api key, make sure to set the key as an environment variable via the command

export COINGECKO_API_KEY=<YourKey>

Notes: 
    I used a 100 day window as opposed to a 720 day window because the total time series was around 730 days, the python program var_code.py can easily be configured to change to 720 days.
    I signed up for a monthly api plan with coingecko to grab the data, looking back I would've gone with coinmarketcap.com; coinbase had data but it was for cbETH which is not identical to Lido's stETH.
            







