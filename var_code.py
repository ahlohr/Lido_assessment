#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 11:53:11 2025

@author: ariel
"""

#%%

import os
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------------- CONFIG -----------------

# Load COINGECKO_API_KEY from .env


COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
if not COINGECKO_API_KEY:
    raise RuntimeError("Please set COINGECKO_API_KEY in your .env file")


# CoinGecko Pro base URL
CG_BASE = "https://pro-api.coingecko.com/api/v3"

# Coin IDs on CoinGecko
ETH_ID   = "ethereum"
STETH_ID = "staked-ether"  # or "lido-staked-ether" depending on CG; adjust if needed

VS_CURRENCY = "usd"
DAYS_BACK   = "max"  # or e.g. "1000" if you want to limit

# Rolling VaR parameters
LOOKAHEAD_DAYS = 14
WINDOW_DAYS    = 100
ALPHA          = 0.01   # 1% left tail => 99% VaR


def cg_grab_dailyPrices(coin_id: str, vs_currency: str = "usd", days: str = "max"):
    """
    Fetches CoinGecko market_chart data for a given coin_id and vs_currency.
    Uses CoinGecko Pro API key via header.
    Returns a DataFrame with columns: ['date', 'price'] at daily frequency.
    """
    url = f"{CG_BASE}/coins/{coin_id}/market_chart"    
    headers = {
        "x-cg-pro-api-key": COINGECKO_API_KEY
    }
    params = {
        "vs_currency": vs_currency,
        "days": 730
    }

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data["prices"], columns=["timestamp_ms", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    df["date"] = df["timestamp"].dt.date

    df = df.groupby("date")["price"].last().to_frame(name="price").reset_index()

    return df

def main():
    eth_daily = cg_grab_dailyPrices(ETH_ID, VS_CURRENCY, DAYS_BACK)
    eth_daily.rename(columns={"price": "eth_price"}, inplace=True)
    
    steth_daily = cg_grab_dailyPrices(STETH_ID, VS_CURRENCY, DAYS_BACK)
    steth_daily.rename(columns={"price": "steth_price"}, inplace=True)
    
    prices = eth_daily[['date','eth_price']].merge(steth_daily[['date','steth_price']], on = 'date', how = 'left').dropna().drop_duplicates().sort_values(by = ['date'], ascending = True)
        
    prices["basis_ratio"] = prices["steth_price"] / prices["eth_price"]
    prices["basis_dev"]   = (prices["basis_ratio"] - 1.0)*100
    
    prices['log_ret'] = np.log(prices['basis_ratio']/prices['basis_ratio'].shift(1))
    prices['log_ret_14day'] = prices['log_ret'].rolling(LOOKAHEAD_DAYS).sum()
    prices['var_14d_99'] = (prices['log_ret_14day'].rolling(WINDOW_DAYS, min_periods = WINDOW_DAYS).quantile(0.01))
    prices['var_14d_99'] = (np.exp(prices['var_14d_99'])-1)*100
    prices['var_14d_99_flip'] = -prices['var_14d_99']
    
    # 6. Plot basis deviation and VaR
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    

    
    # Basis deviation
    ax1.plot(np.array(prices['date']), np.array(prices["basis_dev"]), label="stETH/ETH Basis Deviation")
    ax1.axhline(0.0, linestyle="--", linewidth=1)
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Basis Deviation (%)")
    ax1.set_title("stETH/ETH Basis and 14-Day 99% Historical VaR (CoinGecko Pro Data)")
    
    # VaR on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(np.array(prices.date), np.array(prices["var_14d_99"]), label="14d 99% VaR Bounds", linewidth=2, color = 'orange', linestyle='--')
    ax2.plot(np.array(prices.date), -np.array(prices["var_14d_99"]),  linewidth=2, color = 'orange', linestyle='--')
    ax2.fill_between(
        np.array(prices.date),
        np.array(prices["var_14d_99"]),   # lower bound (bad outcomes)
        -np.array(prices["var_14d_99"]),                      # upper bound (no loss)
        alpha=0.2,
    )
    ax2.set_ylabel("VaR magnitude (absolute 14d move in basis ratio)")

    left_min  = prices["basis_dev"].min()
    left_max  = prices["basis_dev"].max()
    
    right_min = left_min
    right_max = right_min
    
    left_span  = max(abs(left_min), abs(left_max))
    right_span = max(abs(right_min), abs(right_max))
    
    ax1.set_ylim(-left_span, left_span)
    ax2.set_ylim(-right_span, right_span)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

#%%

#%%
