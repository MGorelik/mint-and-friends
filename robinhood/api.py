'''
API interface for Robinhood

Using the API docs provided by https://github.com/sanko/Robinhood
'''
import requests


class RobinhoodApi(object):
    ROBINHOOD_API_URL = 'https://api.robinhood.com/'

    _token = None
    _auth_headers = None

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self.login()

    def login(self):
        if not self._token:
            response = requests.post(self.ROBINHOOD_API_URL + 'api-token-auth/',
                                     data={'username': self._username,
                                           'password': self._password})

            if response and response.json().get('token'):
                self._token = response.json().get('token')
                self._auth_headers = {
                    'Authorization': f"Token {self._token}"
                }

    def get_accounts(self):
        response = requests.get(self.ROBINHOOD_API_URL + 'accounts/', headers=self._auth_headers)

        if response and response.json():
            response_json = response.json()

            if response.status_code != 200:
                raise Exception(f"Error getting accounts: {response_json}")
            response_json = response.json()
            accounts = response_json.get('results')

            return accounts

        return []

    def get_portfolio(self, account):
        portfolio_url = account.get('portfolio')

        response = requests.get(portfolio_url, headers=self._auth_headers)

        if response and response.json():
            response_json = response.json()
            if response.status_code != 200:
                raise Exception(f"Error getting portfolio: {response_json}")

            return response_json

        return None
