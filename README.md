## Simulate/rebalance your cryptocurrency portfolio

### Contents

---

### rebalance portfolio
Files to start rebalancing your own crypto portfolio.  Note: code for API interaction
is designed for Binance.  If you are using a difference exchange, code in 'rebalance.py'
will need to be adjusted accordingly.

Currently, transactions are only recorded in a CSV file.  I am working to include
functionality to save transactions in SQL and mongodb.  Once implemented, users will
be able to choose which format they want to store their transactions, with the choice
to save in multiple formats.

### backtests
Python files used to:
* Retrieve historical price data
* Simulate HODL of 2, 4, 6, 8, and 10 randomly chosen coins
* Simulate rebalance using coins used for HODL simulations

Also contains historical price data and simulation results.

### working files
Experimental files for testing new ideas/strategies.
