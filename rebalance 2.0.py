def update_data(coins):

    df = pd.DataFrame(columns=['symbol', 'quantity', 'price', 'dollar_value'])
    btc_price = float(exchange.fetch_ticker('BTC/USDT')['info']['lastPrice'])

    for coin in coins:
        quantity = balance[coin]['total']
        if coin == 'BTC':
            price = btc_price
        else:
            btc_ratio = float(exchange.fetch_ticker(coin + '/BTC')['info']['lastPrice'])
            price = btc_ratio * btc_price

        dollar_value = quantity * price
        df = df.append({'symbol': coin,'quantity':quantity,'price':price,'dollar_value':dollar_value}, ignore_index=True)

    df['weight'] = list(map(lambda x: x / df['dollar_value'].sum(), df['dollar_value']))
    df = df.sort_values('weight', ascending=False).reset_index(drop=True)
    return df

def rebalance_order(coin1, coin2):
    try:
        exchange.fetch_ticker(coin1 + '/' + coin2)['info']
        return coin1 + '/' + coin2, 'sell'
    except:
        try:
            exchange.fetch_ticker(coin2 + '/' + coin1)['info']
            return coin2 + '/' + coin1, 'buy'
        except:
            return coin1 + '/BTC', 'sell', coin2 + '/BTC', 'buy'

def bnb_order(coin):
    if balance['BNB']['total'] < 1:
        return
    if coin != 'BTC':
        bnb_btc = 2 * float(exchange.fetch_ticker('BNB/BTC')['info']['lastPrice'])
        coin_btc = float(exchange.fetch_ticker(coin + '/BTC')['info']['lastPrice'])
        quantity = bnb_btc / coin_btc
        exchange.create_order(coin + '/BTC', 'market', 'sell', quantity)

    exchange.create_order('BNB/BTC', 'market', 'buy', 2)
    print("Purchased 2 BNB with {:0.3f} {}".format(quantity, coin))

file = "C:/Users/Carter Carlson/Documents/Excel References/secret.csv"
api = pd.read_csv(file)
exchange = ccxt.binance({'options': {'adjustForTimeDifference': True},'apiKey': api['apiKey'][0],'secret': api['secret'][0]})
balance = exchange.fetchBalance()
coins = []
[coins.append(asset['asset']) for asset in balance['info']['balances'] if float(asset['free']) > 0]

data = update_data(coins)

n = 1/len(coins)
thresh = .1
i = 1

while data['weight'][0] - data['weight'][len(data) - 1] > 2 * n * thresh and i < 5:
#while not data[data['weight'] > (n + thresh * n)].empty:

    order = rebalance_order(data['symbol'][0], data['symbol'][len(data) - 1])
    weight_to_move = (data['weight'][0] - data['weight'][len(data) - 1]) / 2
    quantity = round(weight_to_move * data['dollar_value'].sum() / data[data['symbol'] == order[0][:3]]['price'].values[0], 5)
    exchange.create_order(order[0], 'market', order[1], quantity)
    print(order[0], order[1], quantity)

    if len(order) > 2:
        quantity = round(weight_to_move * total_value / data[data['symbol'] == order[2][:3]]['price'].values[0], 5)
        exchange.create_order(order[2], 'market', order[3], quantity)
        print(order[2], order[3], quantity)

    balance = exchange.fetchBalance()
    data = update_data(coins)
    print('Balance after rebalance #', i, '\n', data)
    i += 1

# Note: base rebalancing on sdev instead of baseline %?
# -----------------------------------------------------
port_dollar_value = data['dollar_value'].sum()
avg_weight = 1/len(coins)

heavy_coins = []
light_coins = []
[heavy_coins.append(coin) for coin in coins if data[coin]['weight'] > avg_weight]
[light_coins.append(coin) for coin in coins if data[coin]['weight'] < avg_weight]
# [heavy_coins.append(coin) for coin in coins if data[coin]['weight'] > avg_weight else light_coins.append(coin)]


    # 1 - only buy light coins that satisfy light_coin_weight < heavy_coin_weight
    # 2 - buy light coins even if light_coin_weight > heavy_coin_weight
        # a. trade for heavy_weight_dif
        # b. subtract heavy_weight_dif from light_weight_dif
    # 3 - loop through heavy_coins, if heavy_coin_weight < light_coin_weight, goto next heavy_coin

def test_order(coin1, coin2):
    try:
        exchange.fetch_ticker(coin2 + '/' + coin1)['info']
        test = coin2 + '/' + coin1, 'buy'
        quantity = heavy_weight_dif * port_dollar_value / light_weight_dif
    except:
        try:
            exchange.fetch_ticker(coin1 + '/' + coin2)['info']
            test =  coin1 + '/' + coin2,
            sell_order = True
        except:
            test = coin1 + '/BTC', coin2 + '/BTC'
        finally:
            quantity = light_weight_dif * port_dollar_value / light_weight_dif
            exchange.create_order(test[0], 'market', 'sell', quantity)
            heavy_weight -=

    finally:
        if sell_order:
            return

        exchange.create_order()

for a in range(len(heavy_coins)):
    heavy_coin = data['symbol'][a]
    heavy_weight = data[heavy_coin]['weight']
    heavy_weight_dif = heavy_weight - avg_weight

    for b in range(len(light_coins)):
        light_coin = data['symbol'][b]
        light_value = data[light_coin]['dollar_value']
        light_weight = data[light_coin]['weight']
        light_weight_dif = avg_weight - light_weight

        if heavy_weight_dif > light_weight_dif:
            quantity = light_weight_dif * port_dollar_value / light_value
            create_order(...)
            heavy_weight -= light_weight_dif
            light_weight = avg_weight
            data[heavy_coin]['weight'], data[light_coin]['weight'] = heavy_weight, light_weight
            break

        else:

            for c in range(a, len(heavy_coins)): # error if at last heavy_coin?
                heavy_coin = data['symbol'][c]
                heavy_weight = data[heavy_coin]['weight']
                heavy_weight_dif = heavy_weight - avg_weight

                if light_weight_dif > heavy_weight_dif:
                    quantity = heavy_weight_dif * port_dollar_value / light_value
                    create_order(...)
                    heavy_weight = avg_weight
                    light_weight -= heavy_weight_dif
                    data[heavy_coin]['weight'], data[light_coin]['weight'] = heavy_weight, light_weight
                    light_weight_dif = avg_weight - light_weight

                else:
                    quantity = light_weight_dif * port_dollar_value / light_value
                    create_order(...)
                    heavy_weight -= light_weight_dif
                    light_weight = avg_weight
                    data[heavy_coin]['weight'], data[light_coin]['weight'] = heavy_weight, light_weight
                    break


















































print('a')
