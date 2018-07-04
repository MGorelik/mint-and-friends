# Minthood - Sync your Robinhood portfolios to Mint

## Installation

1. `pip install -r requirements.txt`
2. ```
    brew tap homebrew/cask
    brew cask install chromedriver
   ```

## Running

`python minthood.py`

The program will prompt you for your Mint and Robinhood credentials.
Note that since Mint is done via Selenium and Chromedriver, it'll open a Chrome window and log into Mint.
This means that you may have to do the MFA screen yourself if it comes up. Once you're logged in, it'll continue.

### Caveat

As of right now, the program requires you to have named accounts for your Robinhood accounts.
The naming convention for this is `Robinhood-{ROBINHOOD_ACCOUNT_NUMBER}`.

I'll be adding the ability to dynamically create Mint accounts for each Robinhood account next.