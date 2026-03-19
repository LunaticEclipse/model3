# KCDE quantitative option pricing model
This model aims to find the **true probability density** of price movement in the next trading day. Market randomness is neither time-independent nor follows normal distribution perfectly. This model exploits the shape differences between the true density and the normal distribution, performing statistical arbitrage on options for profit.

## Usage
This model is best used at market open for forecasting the closing price of NVDA on the same day. 

Scroll until you find the #CONTROL# section. Set the 'atm' and 'initial_x' to be the open price of the current trading day, and (atm - last close) / atm respectively. 

Firstly, the code will output the conditional density of the overall percentage intraday price movement in the upcoming trading hours, compared to the normal distribution fitted to the same data. The slider allows for adjusting the value of initial_x to observe how the conditional density evolves across different inputs. 

Secondly, the code will print its estimated prices of the truncated option chain using the estimated density. Compare it with their real market prices to look for arbitrage opportunities (if you harbour sufficient trust in the model of an undergraduate student, that is).

## Conditioning on extended-hour move
The extended hour market often hints at the price movement the following day. A big sell-off pre-market could signal risk aversion in the following trading day, and a big rise in the pre-market could point to a correction when market opens. This model quantifies this by modelling the distribution \[intraday move | extended-hour move\]

## Choice of stock
NVDA daily prices from 2025-08 to 2026-03 are used to fit the models in the example. It is observed that NVDA is in a distinct regime of stably drifting between 170 and 200 throughout the used day range, while being a highly traded stock nonetheless. This serves as a prime testing ground for my model.

While the data pool may seem small, using a wider date range (e.g. from 2019 to 2026) actually increases the model's deviation from the normal distribution model. However, this is deemed less meaningful as NVDA has experienced multiple significant regime changes within this time period. 

## Examples of deviates from the normal distribution model
<img width="796" height="400" alt="image" src="https://github.com/user-attachments/assets/611d23fe-5074-409c-a0db-3af4a38d4307" />

^ evidently, a small down trend before market opens tends to continue into regular trading hours, with a small chance of a major rebounce (the rightmost hump). Notice that the mean is still 0 when fitted with the normal distribution - showing that the stock price itself is priced correctly (as expected from an efficient market), but the density shape is mispriced/

<img width="789" height="393" alt="image" src="https://github.com/user-attachments/assets/a6d657b1-03de-467f-a478-e0a445f3be81" />

^ another notable deviant. A major rise in the extended hours could lead to a tri-modal density in the upcoming trading day. 

<img width="797" height="398" alt="image" src="https://github.com/user-attachments/assets/88f9724d-5d46-4b6f-bac5-4e590821fd6f" />

^ a tamer example. Even in this relatively bell-shaped case, the model is capable of expressing a higher negative skew and higher kurtosis in the estimated distribution compared to the normal model, showing the advantage of using this model rather than a normal distribution.

## Statistical Arbitrage
The KCDE is used to compute the expected payoff of options at various strikes. Notice that far OTM options are often priced at 0.00 (aka below 0.005). This does not mean it is impossible for the price to move to such extremes - rather, the model is saying it is on average always profitable to short options at that range as long as it is currently worth 0.01 or above. Excluding commission fees. 

<img width="418" height="545" alt="image" src="https://github.com/user-attachments/assets/bdb3828b-4268-44cb-b985-a16dc0b95269" />
