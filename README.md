## Simulate/rebalance your cryptocurrency portfolio

**CURRENT WORK IN PROGRESS**
* Functionality to save transactions as a CSV, SQL, and/or MongoDB.
* Ability to set frequency of rebalancing
* There's only 1 table/collection to records transactions.  I want to add a summary 
table/collection to show the portfolio coins, quantities, average cost, etc.

### Contents

---

### rebalance portfolio
Files to start rebalancing your own crypto portfolio.  Note: code for API interaction
is designed for Binance.  If you are using a difference exchange, code in 'rebalance.py'
will need to be adjusted accordingly.

Currently, transactions are only recorded in CSV.

### backtests
Python files used to:
* Retrieve historical price data
* Simulate HODL of 2, 4, 6, 8, and 10 randomly chosen coins
* Simulate rebalance using coins used for HODL simulations

Also contains historical price data and simulation results.

### working files
Experimental files for testing new ideas/strategies.  Adding TA to rebalancing?
