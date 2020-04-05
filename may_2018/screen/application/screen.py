from time import sleep
from datetime import datetime

import requests
from flask_rest.database import orm

from steamapi.constants import SteamMarketConstants


class Screen(orm.Model):
    __tablename__ = 'screens'
    id = orm.Column(
        orm.Integer,
        primary_key=True,
    )

    item_name_id = orm.Column(orm.Text)
    market_hash_name = orm.Column(orm.Text)

    country = orm.Column(orm.Text)
    language = orm.Column(orm.Text)
    currency = orm.Column(orm.SmallInteger)

    buy_price = orm.Column(orm.Float)
    sell_price = orm.Column(orm.Float)

    fields = (
        'item_name_id', 'market_hash_name',
        'country', 'language', 'currency',
        'buy_price', 'sell_price'
    )

    def __init__(self, item_name_id, market_hash_name,
                 buy_price=None, sell_price=None,
                 country=None, language=None, currency=None):
        self.item_name_id = item_name_id
        self.market_hash_name = market_hash_name

        self.country = country or SteamMarketConstants.COUNTRY_USA
        self.language = language or SteamMarketConstants.LANGUAGE_EN
        self.currency = currency or SteamMarketConstants.CURRENCY_USD

        self.buy_price = buy_price
        self.sell_price = sell_price

    def as_dict(self):
        result = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
        return result

    def get_response(self):
        url = 'https://steamcommunity.com/market/itemordershistogram/'
        payload = {
            'country': self.country,
            'language': self.language,
            'currency': self.currency,
            'item_nameid': self.item_name_id,
            'two_factor': 0,
        }
        response = requests.get(url, payload)
        return response

    def parse_price(self, response_data):
        price = {}

        highest_buy_order = response_data.get('highest_buy_order')
        if highest_buy_order:
            price['highest_buy_order'] = int(highest_buy_order) / 100
        else:
            price['highest_buy_order'] = None

        lowest_sell_order = response_data.get('lowest_sell_order')
        if lowest_sell_order:
            price['lowest_sell_order'] = int(lowest_sell_order) / 100
        else:
            price['lowest_sell_order'] = None

        price['highest_sell_order'] = response_data['graph_max_x']
        price['lowest_buy_order'] = response_data['graph_min_x']

        return price

    def buy_if_profitable(self, price):
        if self.buy_price >= price['lowest_sell_order']:
            buy_price = price['lowest_sell_order']
            self.trigger_action('buy', buy_price)

    def sell_if_profitable(self, price):
        if self.sell_price <= price['highest_buy_order']:
            sell_price = price['highest_buy_order']
            self.trigger_action('sell', sell_price)

    def trigger_action(self, action, price):
        payload = {
            'action': action,
            'price': buy_price,
            'item_name_id': self.item_name_id,
            'market_hash_name': self.market_hash_name,
        }
        print(payload)

    def run(self):
        while True:
            response = self.get_response()
            price = self.parse_price(response.json())

            now = datetime.now()
            print(f'Date: {now}. Price: {price}')

            if self.buy_price:
                self.buy_if_profitable(price)

            if self.sell_price:
                self.sell_if_profitable(price)

            sleep(5)
