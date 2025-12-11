#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 19:19:02 2025

@author: ariel
"""

#%%
from web3 import Web3

#%%


# ---------- CONFIGURATION ----------

###############################################################################
# the LP token contract address for the pool (found on etherscan)
LP_TOKEN_ADDRESS = '0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E'  
# a large LP token holder in the pool (found on etherscan)
WHALE_ADDRESS    = '0xf4D898ae2bc5C83E7638DB434f33Dceb8dc7Ab19'  
# USDC mainnet address
USDC_ADDRESS = Web3.to_checksum_address('0xA0b86991c6218B36c1d19D4a2e9Eb0cE3606EB48')
###############################################################################

# port address for local fork (default)
RPC_URL = 'http://127.0.0.1:8545'

# Curve USDC/crvUSD pool address (from assignment)
POOL_ADDRESS = '0x4DEcE678ceceb27446b35C672dC7d61F30bAD69E'



# Index of USDC in the pool's coin array.
# On most UIs USDC is first, so i = 0; verify on Curve docs/Etherscan.
USDC_INDEX = 0

# Fraction of the whale's LP balance to withdraw
WITHDRAW_FRACTION = 0.1  


# ---------- MINIMAL ABIS ----------

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "success", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]

# For many plain 2-coin Curve pools:
# function remove_liquidity_one_coin(uint256 _token_amount, int128 i, uint256 min_amount)
POOL_ABI = [
    {
        "name": "remove_liquidity_one_coin",
        "outputs": [],
        "inputs": [
            {"type": "uint256", "name": "_token_amount"},
            {"type": "int128", "name": "i"},
            {"type": "uint256", "name": "min_amount"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

#%%

def main():
    # connect to local Anvil & check that connection worked
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    assert w3.is_connected(), 'Failed to connect to local Anvil node'

    # impersonate the whale address in Anvil (from assignment)
    w3.provider.make_request("anvil_impersonateAccount", [WHALE_ADDRESS])
    print('Impersonating whale address:', WHALE_ADDRESS)
    print()

    
    # instantiate contract objects
    lp_token = w3.eth.contract(address=LP_TOKEN_ADDRESS, abi=ERC20_ABI)
    usdc     = w3.eth.contract(address=USDC_ADDRESS, abi=ERC20_ABI)
    pool     = w3.eth.contract(address=POOL_ADDRESS, abi=POOL_ABI)


    # read whale lp token balance and print w/ or w/o decimal adjustment
    lp_balance = lp_token.functions.balanceOf(WHALE_ADDRESS).call()
    try:
        print('LP balance (dec adj):', lp_balance / (10**lp_token.functions.decimals().call())) # divide by decimals
    except Exception:
        print('decimal error')
        print('LP balance (no decimal):',lp_balance )
        
    usdc_start = usdc.functions.balanceOf(WHALE_ADDRESS).call()
   
    print('USDC balance (dec adj):', usdc_start / (10**6)) # divide by decimals


    # decide how much LP to burn
    amount_lp_to_burn = int(lp_balance * WITHDRAW_FRACTION)

    try:
        print('LP tokens to be burned (dec adj):' , amount_lp_to_burn / (10**lp_token.functions.decimals().call()))
    except Exception:
        print('LP tokens to be burned (no dec):' , amount_lp_to_burn )
        
    # need to approve pool to call remove_liquidity_one_coin
    print("Approving pool to spend LP tokens...")
    tx_approve = lp_token.functions.approve(POOL_ADDRESS, amount_lp_to_burn).build_transaction({
                "from": WHALE_ADDRESS,
                "nonce": w3.eth.get_transaction_count(WHALE_ADDRESS),
                "gasPrice": w3.eth.gas_price,
                })
    tx_hash_approve = w3.eth.send_transaction(tx_approve)
    receipt_approve = w3.eth.wait_for_transaction_receipt(tx_hash_approve)
    print(f"Approve tx mined in block {receipt_approve.blockNumber}")

    # call remove_liquidity_one_coin to withdraw USDC
    print("Removing liquidity into USDC...")
    nonce = w3.eth.get_transaction_count(WHALE_ADDRESS)
    tx_remove = pool.functions.remove_liquidity_one_coin(
                    amount_lp_to_burn,
                    USDC_INDEX,
                    0  
                    ).build_transaction({
                            "from": WHALE_ADDRESS,
                            "nonce": nonce,
                            "gasPrice": w3.eth.gas_price,
                            })
    tx_hash_remove = w3.eth.send_transaction(tx_remove)
    receipt_remove = w3.eth.wait_for_transaction_receipt(tx_hash_remove)
    print(f"Remove liquidity tx mined in block {receipt_remove.blockNumber}")

    # check USDC balance after withdrawal
    usdc_after = usdc.functions.balanceOf(WHALE_ADDRESS).call()
    usdc_delta = usdc_after - usdc_start

    print('USDC balance after (dec adj):', usdc_after / (10**6)) # divide by decimals
    print('USDC withdrawn (dec adj):', usdc_delta / (10**6)) # divide by decimals


if __name__ == "__main__":
    main()


#%%

#%%

#%%

#%%