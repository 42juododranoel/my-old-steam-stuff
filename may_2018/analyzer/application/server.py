from ast import literal_eval

from flask import Flask, request
from flask_classy import FlaskView, route
from flask_rest.views import BaseAPIViewSet
from flask_rest.response import response
from flask_rest.request import get_parameters
from flask_rest.application import initialize

from steamapi.api import SteamAPI
from history import History


application, orm = initialize()

api = SteamAPI()


def find_profitable_price(history, mode):
    from datetime import datetime, timedelta
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    recent_prices = []
    for index in history.statistics['month']['price_mean_4h_argrelextrema_extrema'][mode][::-1]:
        if history.frames['month'].index[index] < week_ago:
            break
        recent_prices.append(history.frames['month']['price'][index])

    return sum(recent_prices) / len(recent_prices)


class AnalyzerAPIViewSet(FlaskView):
    route_base = '/api/analyzer/'

    @route('/analyze', methods=['GET'])
    def analyze(self):
        args = ('item_name_id', 'market_hash_name')
        parameters = get_parameters(args, args)

        xresponse = api.get_price_history(parameters['market_hash_name'])
        history = History(api.market['app_id'], parameters['market_hash_name'], xresponse.text)
        history.analyze()
        buy_price = find_profitable_price(history, 'minimas')
        sell_price = find_profitable_price(history, 'maximas')
        data = {
            'trend': history.statistics['daily']['price_mean_168h_trend'].value,
            'deviation': history.statistics['month']['price_std_24h'],
            'link': history.url,
            'buy_price': buy_price,
            'sell_price': sell_price,
        }
        return response(200, data)


AnalyzerAPIViewSet.register(application)
