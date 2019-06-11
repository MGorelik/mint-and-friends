import sys
from _decimal import Decimal
from datetime import datetime
from getpass import getpass

import keyring

from coinbase_api.api import CoinbaseApi
from mint.api import MintApi
from robinhood.api import RobinhoodApi


class ConsoleColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# don't mind me, stupid utility function here to make it look like my code is a little cleaner below
def get_value_color(old_value, new_value):
    value_color = ConsoleColors.BOLD
    if new_value > old_value:
        value_color = ConsoleColors.OKGREEN
    elif old_value < new_value:
        value_color = ConsoleColors.FAIL

    return value_color


def login_mint(reset_creds):
    # update the corresponding accounts in Mint
    username = input('Mint username: ')

    password = keyring.get_password('minthood-mint', username)

    if not password or reset_creds:
        password = getpass('Mint password: ')

    try:
        mint = MintApi(username, password, mfa_method='sms', mfa_input_callback=True)
    except Exception as e:
        raise e

    # store valid creds
    keyring.set_password('minthood-mint', username, password)

    return mint


def canary():
    reset_creds = False
    detailed = False
    if len(sys.argv) > 1:
        if 'detailed' in sys.argv:
            detailed = True
        if 'reset_creds' in sys.argv:
            reset_creds = True
            print(ConsoleColors.BOLD + ConsoleColors.WARNING + 'Credentials will be asked for logins' + ConsoleColors.ENDC)

    mint = login_mint(reset_creds)

    mint_accounts = mint.get_accounts()

    credit_cards = []
    for mint_account in mint_accounts:
        if mint_account.get('name') == 'CREDIT CARD':
            credit_cards.append(mint_account)

    # get all of today's transactions for each credit card
    transaction_dict = {}
    for credit_card in credit_cards:
        transactions = mint.get_transactions_json(id=credit_card.get('id'),
                                                  start_date=datetime.strftime(datetime.today(), '%m/%d/%y'))

        last4 = credit_card.get('yodleeAccountNumberLast4')[3:]
        transaction_dict[last4] = transactions

    full_cough = clear_throat(transaction_dict)
    cough(full_cough, detailed)


def clear_throat(cough_dict):
    full_cough = {}
    categories = {}
    total = Decimal('0.00')
    for coughs in cough_dict:
        for cough in cough_dict[coughs]:
            category = cough.get('category')

            if category in categories:
                categories[category].append(cough)
            else:
                categories[category] = [cough]

            amt = cough.get('amount')[1:]
            total += Decimal(amt)

    full_cough['categories'] = categories
    full_cough['total'] = total

    return full_cough


def cough(full_cough, detailed=False):
    print(ConsoleColors.BOLD + ConsoleColors.HEADER + f"\nYou've spent {full_cough.get('total')} today." + ConsoleColors.ENDC)

    categories = full_cough.get('categories')
    for category in categories:
        running_total = Decimal('0.00')

        print('----------------------------------------------------------')
        print(ConsoleColors.BOLD + ConsoleColors.OKBLUE + f'{category}' + ConsoleColors.ENDC)

        for transaction in categories[category]:
            amt = transaction.get('amount')[1:]
            running_total += Decimal(amt)

            if detailed:
                print('----------------------------------')
                print(f"Merchant: {transaction.get('mmerchant')}")
                print(f"Amount: {transaction.get('amount')}")
                print('----------------------------------')

        print(ConsoleColors.BOLD + f'Total: {running_total}' + ConsoleColors.ENDC)


def sync():
    reset_creds = False
    skip_cb = True
    if len(sys.argv) > 1:
        if 'coinbase' in sys.argv:
            skip_cb = False
            print(ConsoleColors.BOLD + ConsoleColors.OKBLUE + 'Coinbase will be included in sync' + ConsoleColors.ENDC)
        if 'reset_creds' in sys.argv:
            reset_creds = True
            print(ConsoleColors.BOLD + ConsoleColors.WARNING + 'Credentials will be asked for logins' + ConsoleColors.ENDC)

    username = input('Robinhood username: ')
    password = keyring.get_password('minthood-robinhood', username)

    if not password or reset_creds:
        password = getpass('Robinhood password: ')

    try:
        robinhood = RobinhoodApi(username, password)
    except Exception as e:
        raise e

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

    if skip_cb:
        coinbase = None
        cb_accounts = []
        coinbase_portfolio = {}
    else:
        # log into coinbase
        api_key = keyring.get_password('minthood-coinbase-api', 'coinbase')

        if not api_key or reset_creds:
            api_key = input('Coinbase API key: ')

        api_secret = keyring.get_password('minthood-coinbase-secret', 'coinbase')

        if not api_secret or reset_creds:
            api_secret = input('Coinbase API secret: ')

        try:
            coinbase = CoinbaseApi(api_key, api_secret)
        except Exception as e:
            raise e

        keyring.set_password('minthood-coinbase-api', 'coinbase', api_key)
        keyring.set_password('minthood-coinbase-secret', 'coinbase', api_secret)

        cb_accounts = coinbase.get_accounts()
        coinbase_portfolio = {}
        for cb_account in cb_accounts:
            coinbase_portfolio['{}-USD'.format(cb_account.balance.currency)] = cb_account

    # update the corresponding accounts in Mint
    username = input('Mint username: ')

    password = keyring.get_password('minthood-mint', username)

    if not password or reset_creds:
        password = getpass('Mint password: ')

    try:
        mint = MintApi(username, password)
    except Exception as e:
        raise e

    # store valid creds
    keyring.set_password('minthood-mint', username, password)

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

                if '{}{}'.format(ROBINHOOD_PREFIX, rb_name) == mn_name:
                    exists = True
            if not exists:
                try:
                    created = mint.create_property_account('{}{}'.format(ROBINHOOD_PREFIX, rb_name), portfolio_values[rb_name])
                    if created.get('success'):
                        print('Created Mint account for Robinhood account {}{}{} (${:,.2f})'.format(ConsoleColors.BOLD,
                                                                                                    rb_name,
                                                                                                    ConsoleColors.ENDC,
                                                                                                    portfolio_values[rb_name]))
                    else:
                        print('{}Problem creating Mint account for Robinhood account {}: {}{}'.format(ConsoleColors.FAIL,
                                                                                                      rb_name,
                                                                                                      created.get('error'),
                                                                                                      ConsoleColors.ENDC))
                except Exception as e:
                    raise e

    COINBASE_PREFIX = 'Coinbase-'
    if not skip_cb:
        # do the same for coinbase
        mint_cb_accounts = [mn for mn in mint_accounts if COINBASE_PREFIX in mn.get('name')]

        if len(cb_accounts) > len(mint_cb_accounts):
            for cb_account in cb_accounts:
                cb_name = '{}-USD'.format(cb_account.balance.currency)
                exists = False
                for mn_account in mint_cb_accounts:
                    mn_name = mn_account.get('name')

                    if '{}{}'.format(COINBASE_PREFIX, cb_name) == mn_name:
                        exists = True
                if not exists:
                    try:
                        account_value = coinbase.get_account_value(cb_account)
                        if account_value > 0:
                            created = mint.create_property_account('{}{}'.format(COINBASE_PREFIX, cb_name), account_value)
                            if created.get('success'):
                                print('Created Mint account for Coinbase account {}{}{} (${:,.2f})'.format(ConsoleColors.BOLD,
                                                                                                           cb_name,
                                                                                                           ConsoleColors.ENDC,
                                                                                                           account_value))
                            else:
                                print('{}Problem creating Mint account for Coinbase account {}: {}{}'.format(ConsoleColors.FAIL,
                                                                                                             cb_name,
                                                                                                             created.get('error'),
                                                                                                             ConsoleColors.ENDC))
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
                result_string = '{}${:,.2f} -> {}${:,.2f}{}'.format(ConsoleColors.BOLD,
                                                                    account.get('value'),
                                                                    get_value_color(account.get('value'), portfolio_values.get(account_num)),
                                                                    portfolio_values.get(account_num),
                                                                    ConsoleColors.ENDC)
                print('Updated value for account {}{}{} ({})'.format(ConsoleColors.BOLD, account_name, ConsoleColors.ENDC, result_string))
            else:
                print('{}Problem updating account {}: {}{}'.format(ConsoleColors.FAIL, account_name, updated.get('error'), ConsoleColors.ENDC))

        if skip_cb:
            continue

        # update coinbase
        idx = account_name.find(COINBASE_PREFIX)
        account_num = account_name[idx+len(COINBASE_PREFIX):] if idx > -1 else ''

        if COINBASE_PREFIX in account_name and account_num:
            account_value = coinbase.get_account_value(coinbase_portfolio.get(account_num))
            updated = mint.set_property_account_value(account, account_value)
            if updated.get('success'):
                result_string = '{}${:,.2f} -> {}${:,.2f}{}'.format(ConsoleColors.BOLD,
                                                                    account.get('value'),
                                                                    get_value_color(account.get('value'), account_value),
                                                                    account_value,
                                                                    ConsoleColors.ENDC)

                print('Updated value for account {}{}{} ({})'.format(ConsoleColors.BOLD, account_name, ConsoleColors.ENDC, result_string))
            else:
                print('{}Problem updating account {}: {}{}'.format(ConsoleColors.FAIL, account_name, updated.get('error'),
                                                                   ConsoleColors.ENDC))


def main():
    if len(sys.argv) > 1:
        if 'sync' in sys.argv:
            sync()
        elif 'canary' in sys.argv:
            canary()
        else:
            print(f'Invalid command: {sys.argv[0]}')
            exit(1)

main()
