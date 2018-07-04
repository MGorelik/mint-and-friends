'''
API interface for Mint using https://github.com/mrooney/mintapi

Also using update account property logic from https://github.com/flavioribeiro/update-my-mint/blob/master/mint.py
'''

import json

from lxml import html
from mintapi import Mint

MINT_OVERVIEW_URL = 'https://mint.intuit.com/overview.event'
PROPERTY_URL_FORMAT = 'https://mint.intuit.com/mas/v1/providers/PFM:{}_{}/accounts/PFM:OtherPropertyAccount:{}_{}'
PROPERTY_CREATE_URL_FORMAT = 'https://mint.intuit.com/updateAccount.xevent?token={}'


class MintApi(Mint):

    browser_auth_api_key = None
    mint_user_id = None

    def login_and_get_token(self, email, password):
        super(MintApi, self).login_and_get_token(email, password)

        doc = html.document_fromstring(self.get(MINT_OVERVIEW_URL).text)
        self.mint_user_id = json.loads(doc.get_element_by_id('javascript-user').value)['userId']
        self.browser_auth_api_key = self.driver.execute_script('return window.MintConfig.browserAuthAPIKey')

    def patch(self, url, **kwargs):
        self.driver.request('PATCH', url, **kwargs)

    def set_property_account_value(self, account, value):
        account_id = account['accountId']
        account_login_id = account['fiLoginId']
        account_update_url = PROPERTY_URL_FORMAT.format(self.mint_user_id, account_login_id, self.mint_user_id, account_id)

        result = self.patch(account_update_url,
                json={
                    'name': account['accountName'],
                    'value': value,
                    'type': 'OtherPropertyAccount'
                    },
                headers={
                    'authorization':
                    'Intuit_APIKey intuit_apikey={}, intuit_apikey_version=1.0'.format(
                        self.browser_auth_api_key),
                    'content-type': 'application/json'
                    })

        return result

    # TODO: make this work
    def create_property_account(self, account_name, value):
        account_create_url = PROPERTY_CREATE_URL_FORMAT.format(self.get_token())

        result = self.post(account_create_url,
                json={
                    'types': 'pr',
                    'accountName': account_name,
                    'accountValue': value,
                    'isAdd': 'T',
                    'accountType': 'a',
                    'associatedLoanRadio': 'T',
                    'associatedLoanChkbox': 'on',
                    },
                headers={
                    'authorization':
                    'Intuit_APIKey intuit_apikey={}, intuit_apikey_version=1.0'.format(
                        self.browser_auth_api_key),
                    'content-type': 'application/json'
                    })

        return result


