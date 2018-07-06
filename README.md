# Minthood - Sync your Robinhood portfolios to Mint

## Installation

1. `pip install -r requirements.txt`
2. ` brew tap homebrew/cask`
3. `brew cask install chromedriver`

## Running

`python minthood.py`

The program will prompt you for your Mint and Robinhood credentials.
Note that since Mint is done via Selenium and Chromedriver, it'll open a Chrome window and log into Mint.
Once you're logged in, it'll continue.

### Caveats

- If the MFA screen comes up, you'll have to log in manually in the opened chrome window.

- As of right now, the program requires you to have named accounts for your Robinhood accounts.
The naming convention for this is `Robinhood-{ROBINHOOD_ACCOUNT_NUMBER}`.

## Updates Roadmap
1. ~~Dynamically create Mint accounts for each Robinhood account if needed~~ **Done**
2. Granularity: Mint accounts for each instrument and more if I think of it or people suggest it
3. ????
4. Profit!
