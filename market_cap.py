import pandas as pd
import os
import time
from selenium import webdriver
from datetime import datetime

driver = webdriver.Chrome('../Coin-Scrape/chromedriver.exe')

page = 'https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20170101&end=20181206'
driver.get(page)

table= driver.find_elements_by_xpath('//table[@class="table"]/tbody/tr')

df = []

for i in range(len(table),0, -1):
	date = table[i-1].find_element_by_xpath('td[1]').text
	date = datetime.strptime(date, '%b %d, %Y')

	mcap = table[i-1].find_element_by_xpath('td[7]').text
	mcap = int(mcap.replace(',',''))

	df.append([date, mcap])



df = pd.DataFrame(df, columns=['date', 'market_cap'])
df.set_index('date', drop=True, inplace=True)

# Save file
df.to_csv('data/historical/market_cap.csv')
