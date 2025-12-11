"""
Created on Thu Dec 11 11:37:28 2025

@author: ariel
"""

# Curve USDC/crvUSD Single-Sided Withdrawal (Local Mainnet Fork)

This project demonstrates how to withdraw single-sided USDC from the Curve USDC/crvUSD pool
by burning LP tokens on a local Ethereum mainnet fork using Anvil and web3.py.

## Prerequisites

- Python3 installed
- install Foundry (for `anvil`) 
- An Ethereum mainnet RPC URL (i used Alchemy)

## 1. Start Anvil Mainnet Fork

In one terminal, run:


anvil --fork-url https://eth-mainnet.alchemyapi.io/v2/YOUR_KEY
(sub in your api key for YOUR_KEY)

## 2. Install Python dependencies
In another  terminal run:

python -m venv .venv
source .venv/bin/activate       
pip install -r requirements.txt

Alternatively you can just pip install web3==6.17.1 (if not in virtual env)

## 3. Edit python script withdraw_usdc.py to update the following variables
    WHALE_ADDRESS
    LP_TOKEN_ADDRESS
    USDC_ADDRESS

## 4. Run the script
In the terminal run:

python withdraw_usdc.py

The script will:
    Impersonate the whale address on the local fork
    Burn some LP tokens 
    Print the USDC balance before/after

#%%