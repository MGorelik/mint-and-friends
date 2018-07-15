from getpass import getpass

import keyring

from coinbase_api.api import CoinbaseApi
from mint.api import MintApi
from robinhood.api import RobinhoodApi


def main(*args):
    if args and args[0] == 'coinbase':
        keyring.delete_password('minthood-coinbase-api', 'coinbase')
        keyring.delete_password('minthood-coinbase-secret', 'coinbase')

    username = input('Robinhood username: ')
    password = keyring.get_password('minthood-robinhood', username)

    if not password:
        password = getpass('Robinhood password: ')

    robinhood = RobinhoodApi(username, password)

    login = robinhood.login()

    if login:
        # store valid creds
        keyring.set_password('minthood-robinhood', username, password)

        # get accounts
        robinhood_accounts = robinhood.get_accounts()

        # try getting portfolio $
        portfolio_values = {}
        for account in robinhood_accounts:
            portfolio = robinhood.get_portfolio(account)
            equity = portfolio.get('equity') if portfolio.get('equity') else 0
            equity_after_hours = portfolio.get('extended_hours_equity') if portfolio.get('extended_hours_equity') else 0
            portfolio_value = max(float(equity), float(equity_after_hours))
            portfolio_values[account.get('account_number')] = portfolio_value

        # update the corresponding account in Mint
        username = input('Mint username: ')

        password = keyring.get_password('minthood-mint', username)

        if not password:
            password = getpass('Mint password: ')

        try:
            mint = MintApi(username, password)
        except Exception as e:
            raise e

        # store valid creds
        keyring.set_password('minthood-mint', username, password)

        # log into coinbase
        api_key = keyring.get_password('minthood-coinbase-api', 'coinbase')

        if not api_key:
            api_key = input('Coinbase API key: ')

        api_secret = keyring.get_password('minthood-coinbase-secret', 'coinbase')

        if not api_secret:
            api_secret = input('Coinbase API secret: ')

        try:
            coinbase = CoinbaseApi(api_key, api_secret)
            keyring.set_password('minthood-coinbase-api', 'coinbase', api_key)
            keyring.set_password('minthood-coinbase-secret', 'coinbase', api_secret)
        except Exception as e:
            raise e

        mint_accounts = mint.get_accounts()

        ROBINHOOD_PREFIX = 'Robinhood-'
        mint_rb_accounts = [mn for mn in mint_accounts if ROBINHOOD_PREFIX in mn.get('name')]

        # if we don't already have a mint account for a robinhood one, create it
        if len(robinhood_accounts) > len(mint_rb_accounts):
            for rb_account in robinhood_accounts:
                rb_name = rb_account.get('account_number')
                exists = False
                for mn_account in mint_rb_accounts:
                    mn_name = mn_account.get('name')

                    if f'{ROBINHOOD_PREFIX}{rb_name}' == mn_name:
                        exists = True
                if not exists:
                    try:
                        created = mint.create_property_account(f'{ROBINHOOD_PREFIX}{rb_name}', portfolio_values[rb_name])
                        if created.get('success'):
                            print(f'Created Mint account for Robinhood account {rb_name}')
                        else:
                            print(f"Problem creating Mint account for Robinhood account {rb_name}: {created.get('error')}")
                    except Exception as e:
                        raise e

        # do the same for coinbase
        cb_accounts = coinbase.get_accounts()
        coinbase_portfolio = {}
        for cb_account in cb_accounts:
            coinbase_portfolio[f'{cb_account.balance.currency}-USD'] = cb_account

        COINBASE_PREFIX = 'Coinbase-'
        mint_cb_accounts = [mn for mn in mint_accounts if COINBASE_PREFIX in mn.get('name')]

        if len(cb_accounts) > len(mint_cb_accounts):
            for cb_account in cb_accounts:
                cb_name = f'{cb_account.balance.currency}-USD'
                exists = False
                for mn_account in mint_cb_accounts:
                    mn_name = mn_account.get('name')

                    if f'{COINBASE_PREFIX}{cb_name}' == mn_name:
                        exists = True
                if not exists:
                    try:
                        value = coinbase.get_account_value(cb_account)
                        if value > 0:
                            created = mint.create_property_account(f'{COINBASE_PREFIX}{cb_name}', value)
                            if created.get('success'):
                                print(f'Created Mint account for Coinbase account {cb_name}')
                            else:
                                print(
                                    f"Problem creating Mint account for Coinbase account {cb_name}: {created.get('error')}")
                    except Exception as e:
                        raise e

        for account in mint_accounts:
            account_name = account.get('name')

            # update robinhood
            idx = account_name.find(ROBINHOOD_PREFIX)
            account_num = account_name[idx+len(ROBINHOOD_PREFIX):] if idx > -1 else ''

            if ROBINHOOD_PREFIX in account_name and account_num:
                updated = mint.set_property_account_value(account, portfolio_values.get(account_num))

                if updated.get('success'):
                    print(f'Updated value for account {account_name}')
                else:
                    print(f"Problem updating account {account_name}: {updated.get('error')}")

            # update coinbase
            idx = account_name.find(COINBASE_PREFIX)
            account_num = account_name[idx+len(COINBASE_PREFIX):] if idx > -1 else ''

            if COINBASE_PREFIX in account_name and account_num:
                updated = mint.set_property_account_value(account, coinbase_portfolio.get(account_num))
                if updated.get('success'):
                    print(f'Updated value for account {account_name}')
                else:
                    print(f"Problem updating account {account_name}: {updated.get('error')}")


def test_coinbase():
    api_key = keyring.get_password('minthood-coinbase-api', 'coinbase')

    if not api_key:
        api_key = input('Coinbase API key: ')

    api_secret = keyring.get_password('minthood-coinbase-secret', 'coinbase')

    if not api_secret:
        api_secret = input('Coinbase API secret: ')

    try:
        coinbase = CoinbaseApi(api_key, api_secret)
        keyring.set_password('minthood-coinbase-api', 'coinbase', api_key)
        keyring.set_password('minthood-coinbase-secret', 'coinbase', api_secret)
    except Exception as e:
        raise e

    accounts = coinbase.get_accounts()

    for account in accounts.data:
        balance = account.balance
        print('%s: %s %s' % (account.name, balance.amount, balance.currency))
        value = coinbase.get_account_value(account)
        print('val: ', value)

main()
# test_coinbase()