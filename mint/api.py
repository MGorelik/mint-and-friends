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

    def login_and_get_token(self, email, password, mfa_method=None,
                            mfa_input_callback=None, headless=True,
                            session_path=None, imap_account=None,
                            imap_password=None,
                            imap_server=None,
                            imap_folder=None):
        super(MintApi, self).login_and_get_token(email, password, mfa_method=mfa_method,
                                                 mfa_input_callback=mfa_input_callback,
                                                 headless=headless)

        doc = html.document_fromstring(self.get(MINT_OVERVIEW_URL).text)
        self.mint_user_id = json.loads(doc.get_element_by_id('javascript-user').value)['userId']
        self.browser_auth_api_key = self.driver.execute_script('return window.MintConfig.browserAuthAPIKey')

    def patch(self, url, **kwargs):
        return self.driver.request('PATCH', url, **kwargs)

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

        if result:
            if result.status_code == 200 or result.status_code == 204:
                # check if we got an error
                # (Mint returns a 200 even on failure and then puts the error in the response text)
                if 'error' in result.text:
                    return {'success': False, 'error': result.text}
                return {'success': True, 'error': None}
        return {'success': False, 'error': None}

    def create_property_account(self, account_name, value):
        account_create_url = PROPERTY_CREATE_URL_FORMAT.format(self.get_token())

        result = self.post(account_create_url,
                data={
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
                    'content-type': 'application/x-www-form-urlencoded'
                    })

        if result:
            if result.status_code == 200:
                # check if we got an error
                # (Mint returns a 200 even on failure and then puts the error in the response text)
                if 'error' in result.text:
                    return {'success': False, 'error': result.text}
                return {'success': True, 'error': None}
        return {'success': False, 'error': None}


