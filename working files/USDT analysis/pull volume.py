import os
import sys
import ccxt
import numpy as np
import pandas as pd

exchange = ccxt.binance({'options': {'adjustForTimeDifference': True}})
