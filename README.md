# Algorithmic Trading using Python

I am following FreeCodeCamp's "Algorithmic Trading using Python" course. The course covers:
1) Building an equal-weight S&P 500 portfolio.
2) Quantitative momentum strategy: equal weight portfolio of the 50 best performing stocks in terms of "high-quality momentum".
3) Value strategy.

I make the following modifications:
1) I make a market-capitalization-weighted portfolio to reflect the true index.
2) I use a different measure of momentum quality. The tutorial suggests using the arithmetic mean of the 1, 3, 6 and 12 month return percentiles. I use the geometric mean, so as to penalise variability.

Not that I only have access to an API for *randomized* US stock market data, so this does not reflect accurate prices and I cannot use FTSE stocks.

Sources:
1) https://www.youtube.com/watch?v=xfzGZB4HhEE&ab_channel=freeCodeCamp.org
2) https://github.com/nickmccullum/algorithmic-trading-python/