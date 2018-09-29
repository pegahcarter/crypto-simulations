import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from dateutil.parser import parse
import matplotlib.pyplot as plt
%matplotlib inline


start_date = '20170928'
end_date = '20180928'
webpage = 'https://coinmarketcap.com/currencies/tether/historical-data/?start=' + start_date + '&end=' + end_date

page = requests.get(webpage, timeout=5)
content = BeautifulSoup(page.content, "html.parser")
table = content.find_all("td")

date = [table[i].text for i in range(0,len(table),7)]
price = [table[i].text for i in range(1,len(table),7)]
volume = [table[i].text for i in range(5,len(table),7)]
market_cap = [table[i].text for i in range(6,len(table),7)]
clean_date = [parse(day).date() for day in date]

data = pd.DataFrame(columns=['volume', 'date'])
data['volume'] = volume
data['clean_date'] = clean_date
