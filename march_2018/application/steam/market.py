from steam.utils import login_required


class SteamMarket:
    CURRENCY_USD = 1
    CURRENCY_GBP = 2
    CURRENCY_EURO = 3
    CURRENCY_CHF = 4
    CURRENCY_RUB = 5

    COUNTRY_USA = 'USA'
    COUNTRY_RUSSIA = 'RU'

    LANGUAGE_EN = 'english'

    APP_ID_DOTA2 = 570
    APP_ID_CSGO = 730
    APP_ID_TF2 = 440
    APP_ID_PUBG = 578080

    CONTEXT_ID = 2

    currency = CURRENCY_USD
    country = COUNTRY_USA
    language = LANGUAGE_EN
    app_id = APP_ID_PUBG
    context_id = CONTEXT_ID

    def __init__(self, api):
        self.api = api

    def configure(self, currency=None, country=None, language=None,
                  app_id=None, context_id=None):
        self.currency = currency or self.currency
        self.country = country or self.country
        self.language = language or self.language
        self.app_id = app_id or self.app_id
        self.context_id = context_id or self.context_id

    @property
    def is_logged_in(self):
        return self.api.is_logged_in

    # --- API Methods --- #

    # Not a JSON
    def get_price_history(self, market_hash_name, **kwargs):
        app_id = kwargs.get('app_id') or self.app_id
        method = f'/market/listings/{app_id}/{market_hash_name}'
        response = self.api.get(method)
        return self.api.get(method)

    def get_price_overview(self, market_hash_name, **kwargs):
        method = '/market/priceoverview/'
        payload = {
            'country': kwargs.get('country', self.country),
            'currency': kwargs.get('currency', self.currency),
            'appid': kwargs.get('app_id', self.app_id),
            'market_hash_name': market_hash_name,
        }
        return self.api.get(method, payload)

    def get_price_histogram(self, item_name_id, **kwargs):
        method = '/market/itemordershistogram/'
        payload = {
            'country': kwargs.get('country', self.country),
            'language': kwargs.get('language', self.language),
            'currency': kwargs.get('currency', self.currency),
            'item_nameid': item_name_id,
            'two_factor': 0,
        }
        return self.api.get(method, payload)

    @login_required
    def create_sell_order(self, asset_id, money_to_receive, **kwargs):
        method = '/market/sellitem/'
        payload = {
            'sessionid': self.api.session_id,
            'assetid': asset_id,
            'contextid': kwargs.get('context_id', self.context_id),
            'appid': kwargs.get('app_id', self.app_id),
            'amount': 1,
            'price': money_to_receive,
        }
        headers = {
            'Referer':
                f'{self.api.base_url}/profiles/' \
                f'{self.api.session_id}/inventory'
        }
        return self.api.post(method, payload, headers)

    @login_required
    def create_buy_order(self, market_hash_name, quantity,
                         total_price, **kwargs):
        method = '/market/createbuyorder/'
        payload = {
            'sessionid': self.api.session_id,
            'currency': kwargs.get('currency', self.currency),
            'appid': kwargs.get('app_id', self.app_id),
            'market_hash_name': market_hash_name,
            'price_total': total_price,
            'quantity': quantity
        }
        headers = {
            'Referer':
                f'{self.api.base_url}/market/listings/' \
                f'{self.app_id}/{market_hash_name}'
        }
        return self.api.post(method, payload, headers)

    @login_required
    def cancel_sell_order(self, sell_listing_id):
        method = f'/market/removelisting/{sell_listing_id}'
        payload = {'sessionid': self.api.session_id}
        headers = {'Referer': self.api.base_url + '/market/'}
        return self.api.post(method, payload, headers)

    @login_required
    def cancel_buy_order(self, buy_order_id):
        method = '/market/cancelbuyorder/'
        payload = {
            'sessionid': self.api.session_id,
            'buy_orderid': buy_order_id
        }
        headers = {'Referer': f'{self.api.base_url}/market/'}
        return self.api.post(method, payload, headers)

    # @login_required
    # def get_my_market_listings(self):
    #     import pdb; pdb.set_trace()
    #     response = self.api.get('/market')
    #     text = response.text
    #
    #     assets_descriptions = get_text_between(text, 'var g_rgAssets = ', ';\r\n')
    #     assets_descriptions = eval(assets_descriptions)
    #
    #     listing_id_to_assets_address = get_listing_id_to_assets_address_from_html(response.text)
    #     listings = get_market_listings_from_html(response.text)
    #     listings = merge_items_with_descriptions_from_listing(listings, listing_id_to_assets_address, assets_descriptions)
    #     if '<span id="tabContentsMyActiveMarketListings_end">' in response.text:
    #         n_showing = int(text_between(response.text, '<span id="tabContentsMyActiveMarketListings_end">', '</span>'))
    #         n_total = int(text_between(response.text, '<span id="tabContentsMyActiveMarketListings_total">', '</span>'))
    #         if n_total > n_showing:
    #             url = "%s/market/mylistings/render/?query=&start=%s&count=%s" % (
    #             SteamUrl.COMMUNITY_URL, n_showing, -1)
    #             response = self._session.get(url)
    #             jresp = response.json()
    #             listing_id_to_assets_address = get_listing_id_to_assets_address_from_html(
    #                 jresp.get("hovers"))
    #             listings_2 = get_market_sell_listings_from_api(
    #                 jresp.get("results_html"))
    #             listings_2 = merge_items_with_descriptions_from_listing(
    #                 listings_2, listing_id_to_assets_address,
    #                 jresp.get("assets"))
    #             listings["sell_listings"] = {**listings["sell_listings"],
    #                                          **listings_2["sell_listings"]}
    #
    #     return listings
