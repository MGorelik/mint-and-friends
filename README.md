# Mint and Friends - Sync your Robinhood and Coinbase portfolios to Mint

## Installation

1. `pip install -r requirements.txt`

### Mac OS
2. `brew tap homebrew/cask`
3. `brew cask install chromedriver`

### Windows
2. [Download ChromeDriver](http://chromedriver.chromium.org/downloads)
3. Extract `chromedriver.exe` somewhere
4. Add that location to your `PATH`

## Additional Setup

### Coinbase
In order to use the Coinbase functionality, you'll need to create an API key to use with the app. The only permission your API key needs is `wallet:accounts:read`. **Make sure to save your API key and secret! The secret will only be shown when you create a key.**

You'll be prompted for those two values when you run the app for the first time.

## Running

`python mint_and_friends.py`

The program will prompt you for your Mint and Robinhood credentials.
Note that since Mint is done via Selenium and Chromedriver, it'll open a Chrome window and log into Mint.
Once you're logged in, it'll continue.

### Optional Arguments
You can pass two arguments after the main script name:
1. `reset_creds`: This will prompt you for all your logins and will update the saved values for that account. Useful if you need to update your password.
2. `skip_cb`: This will skip Coinbase syncing if you don't want it or don't have a Coinbase account.

### Results
`Mint and Friends` will create `Property` accounts in Mint for your Robinhood and/or Coinbase accounts.

For Robinhood, it will create one `Property` per account using the naming convention of `Robinhood-{ROBINHOOD_ACCOUNT_NUMBER}`.

For Coinbase, it will create one `Propery` per wallet that you have any currency in using the naming convention of `Coinbase-{CURRENCY}`.

### Caveats

- If the MFA screen comes up, you'll have to log in manually in the opened chrome window.

## Updates Roadmap
1. ~~Dynamically create Mint accounts for each Robinhood account if needed~~ **Done**
2. Granularity: Mint accounts for each instrument and more if I think of it or people suggest it
3. Other services (~~Coinbase~~ **Done**, etc)
