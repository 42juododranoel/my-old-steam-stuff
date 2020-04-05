import rsa
import time
from base64 import b64encode

import requests

from steam.market import SteamMarket
from steam.utils import login_required
from steam.guard import generate_one_time_code


class SteamAPI:
    def __init__(self, api_key, credentials):
        self.market = SteamMarket(self)
        self.base_url = 'https://steamcommunity.com'

        self.api_key = api_key
        self.credentials = credentials
        self.guard = credentials['guard']

        self.session = requests.Session()
        self.one_time_code_created_at = None

    @property
    def session_id(self):
        return self.session.cookies.get_dict()['sessionid']

    @property
    def is_logged_in(self):
        response = self.get('/')
        return self.credentials['username'] in response.text

    # --- Login, logout and login's low-level dependencies --- #

    def login(self, username, password, guard):
        response = self._send_login_request()

        if response.json()['requires_twofactor']:
            one_time_code = self._generate_one_time_code()
            response = self._send_login_request(one_time_code)

        if not response.json()['success']:
            raise PermissionError(response.json())

        self._perform_redirects(response)
        self._set_session_id_cookies()

    def logout(self):
        url = 'https://store.steampowered.com/logout/'
        payload = {'sessionid': self.session_id}
        return self.request('post', url, payload)

    def _send_login_request(self, one_time_code=None):
        rsa_params = self._get_rsa_params()
        encrypted_password = self._encrypt_password(
            self.credentials['password'], rsa_params
        )
        payload = {
            'username': self.credentials['username'],
            'password': encrypted_password,
            'twofactorcode': one_time_code,
            'remember_login': 'false',
            'emailauth': None,
            'emailsteamid': None,
            'loginfriendlyname': None,
            'captcha_text': None,
            'captchagid': '-1',
            'rsatimestamp': rsa_params['rsa_timestamp'],
            'donotcache': int(time.time() * 1000)
        }
        url = 'https://store.steampowered.com/login/dologin'
        return self.request('post', url, payload)

    def _get_rsa_params(self, current_number_of_repetitions=0):
        maximal_number_of_repetitions = 5
        url = 'https://store.steampowered.com/login/getrsakey/'
        payload = {'username': self.credentials['username']}
        response = self.request('post', url, payload)
        json = response.json()

        try:
            params = {
                'rsa_key': rsa.PublicKey(
                    int(json['publickey_mod'], 16),
                    int(json['publickey_exp'], 16)
                ),
                'rsa_timestamp': json['timestamp']
            }
            return params

        except KeyError:
            # TODO: Probably, needs refactoring
            if current_number_of_repetitions < maximal_number_of_repetitions:
                return self._get_rsa_params(current_number_of_repetitions + 1)
            else:
                raise ValueError('Could not obtain rsa-key')

    @staticmethod
    def _encrypt_password(password, rsa_params):
        utf8_password = password.encode('utf-8')
        encrypted_password = b64encode(
            rsa.encrypt(utf8_password, rsa_params['rsa_key'])
        )
        return encrypted_password

    # TODO: Probably rename
    def _perform_redirects(self, response):
        json = response.json()
        parameters = json.get('transfer_parameters')
        # TODO: Stupid case, needs refactoring
        if not parameters:
            raise Exception(
                'Cannot perform redirects after login, no parameters fetched'
            )
        for url in json['transfer_urls']:
            self.request('post', url, parameters)

    def _set_session_id_cookies(self):
        for domain in ['steamcommunity.com', 'store.steampowered.com']:
            cookie = {
                'name': 'sessionid',
                'value': self.session_id,
                'domain': domain,
            }
            self.session.cookies.set(**cookie)

    def _generate_one_time_code(self):
        if self.one_time_code_created_at:
            now = int(time.time())

            # If 30 seconds have not passed since previous code
            if not (self.one_time_code_created_at + 30 > now):
                time_for_sleeping = (self.one_time_code_created_at + 30) - now
                time.sleep(time_for_sleeping + 1)

        self.one_time_code_created_at = int(time.time())
        one_time_code = generate_one_time_code(self.guard['shared_secret'])
        return one_time_code

    # --- API request helpers --- #

    def get(self, api_method, query_params=None, headers=None):
        url = self.base_url + api_method
        return self.request('get', url, query_params, headers)

    def post(self, api_method, data=None, headers=None):
        url = self.base_url + api_method
        return self.request('post', url, data, headers)

    def request(self, http_method, url, payload=None, headers=None):
        if http_method == 'get':
            response = self.session.get(url, params=payload, headers=headers)
        elif http_method == 'post':
            response = self.session.post(url, data=payload, headers=headers)
        else:
            raise AttributeError(f'Unsupported HTTP method {http_method}')
        return response

    # --- API Methods --- #

    @login_required
    def get_my_inventory(self, **kwargs):
        app_id = kwargs.get('app_id', self.market.app_id)
        context_id = kwargs.get('context_id', self.market.context_id)
        method = f'/my/inventory/json/{app_id}/{context_id}'
        return self.get(method)

    @login_required
    def get_partner_inventory(self, partner_steam_id, **kwargs):
        method = '/tradeoffer/new/partnerinventory/'
        payload = {
            'sessionid': self.session_id,
            'partner': partner_steam_id,
            'appid': kwargs.get('app_id', self.market.app_id),
            'contextid': kwargs.get('context_id', self.market.app_id),
        }
        partner_account_id = steam_id_to_account_id(partner_steam_id)
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': '{}/tradeoffer/new/?partner={}'.format(
                self.base_url, partner_account_id
            ),
            'X-Prototype-Version': '1.7'
        }
        return self.get(method, payload, headers)
