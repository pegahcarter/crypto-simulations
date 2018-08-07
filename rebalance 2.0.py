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
param = {'test':True}
port_dollar_value = data['dollar_value'].sum()
avg_weight = 1/len(coins)
thresh = .0005

heavy_coins = []
light_coins = []
[heavy_coins.append(coin) if data[data['symbol'] == coin]['weight'].values[0] > avg_weight else light_coins.append(coin) for coin in coins]

def rebalance_order(coin1, coin2):
    try:
        exchange.fetch_ticker(coin2 + '/' + coin1)['info']
        side = 'buy'
        ticker = coin2 + '/' + coin1
    except:
        side = 'sell'
        try:
            exchange.fetch_ticker(coin1 + '/' + coin2)['info']
            ticker =  coin1 + '/' + coin2
        except:
            ticker = coin2 + '/BTC'
            print(exchange.create_order(coin1 + '/BTC', 'market', side, quantity, param))
            side = 'buy'
            # document two trades
            quantity = smaller_weight_dif * port_dollar_value / data[data['symbol'] == coin2]['price'].values[0]
    finally:
        print(exchange.create_order(ticker, 'market', side, quantity, param))

def get_coin_info(coin):
    dollar_value = data[data['symbol'] == coin]['dollar_value'].values[0]
    weight = data[data['symbol'] == coin]['weight'].values[0]
    #dollar_value = data[data[coin]['symbol'] == coin]['dollar_value']
    weight_dif = abs(weight - avg_weight)
    return coin, dollar_value, weight, weight_dif

def test(coin1, coin2, smaller_weight_dif):
    q = smaller_weight_dif * port_dollar_value / light_value
    data[heavy_coin]['weight'] -= smaller_weight_dif
    data[light_coin]['weight'] -= smaller_weight_dif
    return q

for a in range(len(heavy_coins)):
    for b in range(len(light_coins)):
        heavy_coin, heavy_value, heavy_weight, heavy_weight_dif = get_coin_info(heavy_coins[a])
        light_coin, light_value, light_weight, light_weight_dif = get_coin_info(light_coins[b])
        print(get_coin_info(heavy_coins[a]))
        if abs(heavy_weight_dif - light_weight_dif) <= thresh:
            break
        elif heavy_weight_dif > light_weight_dif:
            quantity = test(heavy_coin, light_coin, light_weight_dif)
            rebalance_order(coin1, coin2)
            break

        else:
            for c in range(a + 1, len(heavy_coins)):
                heavy_coin, heavy_value, heavy_weight, heavy_weight_dif = get_coin_info(heavy_coins, c)
                if abs(heavy_weight_dif - light_weight_dif) <=thresh:
                    break
                elif light_weight_dif > heavy_weight_dif:
                    quantity = test(light_coin, heavy_coin, heavy_coin_dif)
                    rebalance_order(light_coin, heavy_coin)
                else:
                    quantity = test(heavy_coin, light_coin, light_weight_dif)
                    rebalance_order(heavy_coin, light_coin)
                    break


















































print('a')
