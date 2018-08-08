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
# -----------------------------------------------------
# -----------------------------------------------------
import pandas as pd
import ccxt
from datetime import datetime
from openpyxl import load_workbook


excel_file = 'test_excel.xlsx'
wb = load_workbook(file)
sheet = wb.active
row_num = sheet.max_row
test = sheet.cell(row=row_num, column=1).value

trade_id = sheet.cell(row=row_num, column=1).value + 1
single_trade = None
if not first_trade:
    rebalance_id = sheet.cell(row=row_num, column=2)
else:
    rebalance_id = sheet.cell(row=row_num, column=2) + 1

trade_date = '2018-08-16'
ticker = 'ETH/BTC'
ticker1 = ticker[:4]
ticker2 = ticker[4:]
dollar_value = 100




new_order = [trade_id, rebalance_id, trade_date, ticker1, ticker2, dollar_value]
for col_num,val in zip(len(new_order), new_order):
    sheet.cell(row=row_num, column=col_num + 1).value = val


wb.save(file)





























def write_to_excel(side, ticker, quantity, dollar_value, single_trade):
    excel_file = 'transactions.xlsx'
    wb = wb.load_workbook(file)
    sheet = wb.active
    row_num = sheet.max_row
    rebalance_id = sheet.cell(row=row_num, column=2).value
    if single_trade:
        rebalance_id = sheet.cells(row=row_num, column=2).value + 1

    trade_date = datetime.datetime.now.strftime('%Y-%m%-d %H:%M')
    ticker1 = ticker[:3]
    ticker2 = ticker[4:]
    fees = dollar_value * .00075
    transaction = []



    trades = pd.read_csv('test_orders.csv')
    last_order = trades.tail(n=1)
    trade_id = last_order['trade_id'] + 1
    if single_trade:
        rebalance_id = last_order['rebalance_id']
    else:
        rebalance_id = last_order['rebalance_id'] + 1

    trade_date = datetime.now.strftime('%Y-%m-%d %H-%M')
    ticker1 = ticker[:3]
    ticker2 = ticker[4:]
    fees = dollar_value * .00075
    single_trade ??

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

    return df

def rebalance_order(coin1, coin2, coin2_weight_dif):
    amt = coin2_weight_dif * port_dollar_value / light_value # Note: is light_value correct? do I need to change?
    try:
        side = 'buy'
        exchange.fetch_ticker(coin2 + '/' + coin1)['info']
        ticker = coin2 + '/' + coin1
    except:
        try:
            side = 'sell'
            exchange.fetch_ticker(coin1 + '/' + coin2)['info']
            ticker =  coin1 + '/' + coin2
        except:
            print(exchange.create_order(coin1 + '/BTC', 'market', side, amt, param))
            ticker = coin2 + '/BTC'
            side = 'buy'

    finally:
        print(exchange.create_order(ticker, 'market', side, amt, param))
        data.at(coin1, 'weight') -= coin2_weight_dif
        data.at(coin2, 'weight') += coin2_weight_dif

def get_coin_info(coin):
    dollar_value, weight = df.loc[coin, ['dollar_value', 'weight']].tolist()
    weight_dif = abs(weight - avg_weight)
    return coin, dollar_value, weight, weight_dif

file = "C:/Users/Carter Carlson/Documents/Excel References/secret.csv"
api = pd.read_csv(file)
exchange = ccxt.binance({'options': {'adjustForTimeDifference': True},'apiKey': api['apiKey'][0],'secret': api['secret'][0]})
balance = exchange.fetchBalance()
wallet = balance['info']['balances']

coins = []
heavy_coins = []
light_coins = []
coins = wallet.loc[float(wallet['free']) > 0, 'asset'].tolist()

[coins.append(asset['asset']) for asset in balance['info']['balances'] if float(asset['free']) > 0]
data = update_data(coins)
port_dollar_value = data['dollar_value'].sum()
data['weight'] = list(map(lambda x: x / port_dollar_value, data['dollar_value']))
data.sort_values('weight', ascending=False).set_index('symbol', inplace=True)
heavy_coins = data.loc[data['weight'] > avg_weight, 'symbol'].tolist()
light_coins = data.loc[~data['symbol'].isin(heavy_coins), 'symbol'].tolist()

param = {'test':True}
avg_weight = 1/len(coins)
thresh = .0005

for a in range(len(heavy_coins)):
    for b in range(len(light_coins)):
        heavy_coin, heavy_value, heavy_weight, heavy_weight_dif = get_coin_info(heavy_coins[a])
        light_coin, light_value, light_weight, light_weight_dif = get_coin_info(light_coins[b])
        print(get_coin_info(heavy_coins[a]))
        if abs(heavy_weight_dif - light_weight_dif) <= thresh:
            break
        elif heavy_weight_dif > light_weight_dif:
            rebalance_order(heavy_coin, light_coin, light_weight_dif)
            break
        else:
            for c in range(a + 1, len(heavy_coins)):
                heavy_coin, heavy_value, heavy_weight, heavy_weight_dif = get_coin_info(heavy_coins[c])
                if abs(heavy_weight_dif - light_weight_dif) <=thresh:
                    break
                elif light_weight_dif > heavy_weight_dif:
                    rebalance_order(light_coin, heavy_coin, heavy_weight_dif)
                else:
                    rebalance_order(heavy_coin, light_coin, light_weight_dif)
                    break


















































print('a')
