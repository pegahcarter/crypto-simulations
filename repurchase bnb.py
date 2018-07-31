# Check if we need more BNB for transaction fees
# Note: figure out auto-purchase of bnb if < 1.0 bnb

bnb_quantity = balance['BNB']['total']
if bnb_quantity < 1:
    max_val = 0
    # find coin used to buy more BNB
    for item in data.items():
        # Note: figure how to trade - BNB/BTC and BNB/ETH, but XRP/BNB
        if item[1]['dollar_value'] > max_val and item[0] != 'OMG' and item[0] != 'XRP':
            max_val = item[1]['dollar_value']
            coin_for_bnb = item[0]
