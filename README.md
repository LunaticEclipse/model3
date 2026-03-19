# My model
This model aims to find the **true probability density** of price movement in the next trading day. Market randomness is neither time-independent nor follows normal distribution perfectly. This model exploits the shape differences between the true density and the normal distribution, performing statistical arbitrage on options for profit.

## Conditioning on interday move
The interday market potentially gives insight to the price movement the following day. A big sell-off pre-market could signal the overall risk-aversion in the following trading day, and a big rise in the pre-market could point to a correction when market opens. This model quantifies this by modelling the distribution \[intraday move | interday move\]

<img width="796" height="400" alt="image" src="https://github.com/user-attachments/assets/611d23fe-5074-409c-a0db-3af4a38d4307" />
