This repository was used to simulate a HODL strategy and a daily rebalancing strategy to analyze the effectiveness of rebalancing.
Simulations were conducted by randomly selecting a basket of 5 coins 1,000 times and documenting the daily value of the portfolio over the course of one year.

To combat any inherent bias of choosing the date range to simulate, I calculated the difference of the overall crypto market cap from the
first day to the same day a year later.  From there, I chose the date range with the median difference.

## Contents

* Python scripts used to pull historical data
* Python scripts used to simulate HODLing and rebalancing

### data
  * __historical__
     * historical crypto market cap
     * historical price of most top-100 cryptocurrencies
  * __simulations__
     * results of hourly, daily, and monthly simulated rebalancing
  
#### Coming soon: a deep, comparative analysis between the HODL and rebalance simulations.
