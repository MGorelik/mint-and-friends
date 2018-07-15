import json

from coinbase.wallet.client import Client


class CoinbaseApi(object):

    client = None
    _api_version = '2018-07-15'

    def __init__(self, api_key, api_secret):
        self._api_key = api_key
        self._api_secret = api_secret
        self.authenticate()

    def authenticate(self):
        try:
            self.client = Client(self._api_key, self._api_secret, api_version=self._api_version)
        except Exception as e:
            raise e

    def get_accounts(self):
        accounts = self.client.get_accounts()
        if accounts:
            return accounts.data

    def get_account_value(self, account):
        price_response = self.client.get_spot_price(currency_pair=f'{account.balance.currency}-USD')
        price = price_response.get('amount') if price_response.get('amount') else 0

        return float(price) * float(account.balance.amount)
