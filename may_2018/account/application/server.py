from ast import literal_eval

from flask import Flask
from flask_classy import FlaskView, route
from flask_rest.response import response as render
from flask_rest.request import get_parameters
from flask_rest.application import initialize

from steamapi.api import SteamAPI


class AccountAPIViewSet(FlaskView):
    route_base = '/api/account/'

    @route('/login', methods=['POST'])
    def login(self):
        args = ('username', 'password', 'secrets')
        parameters = get_parameters(args, args)
        parameters['secrets'] = literal_eval(parameters['secrets'])
        api.login(**parameters)
        return render(200)

    @route('/status', methods=['GET'])
    def status(self):
        # TODO: Переделать
        proxy = None
        balance = None
        if not api.is_anonymous:
            balance = api.get_account_balance()
        data = {
            'username': api.username,
            'is_anonymous': api.is_anonymous,
            'balance': balance,
            'proxy': proxy,
        }
        return render(200, data)

    @route('/inventory', methods=['GET'])
    def inventory(self):
        parameters = get_parameters(('app_id',), ('app_id',))
        response = api.get_my_inventory(**parameters)

        items = []
        response_data = response.json()

        if not isinstance(response_data['rgInventory'], list):
            for index, meta in response_data['rgInventory'].items():
                key = '{}_{}'.format(meta['classid'], meta['instanceid'])
                description = response_data['rgDescriptions'][key]

                item = {
                    'asset_id': meta['id'],
                    'instance_id': meta['instanceid'],
                    'market_hash_name': description['market_hash_name'],
                    'app_id': description['appid'],
                    'type': description['type'],
                }

                if description['marketable']:
                    item['is_marketable'] = True
                else:
                    item['is_marketable'] = False

                if description['tradable']:
                    item['is_tradable'] = True
                else:
                    item['is_tradable'] = False
                items.append(item)

        return render(200, items)

    @route('/sell', methods=['POST'])
    def sell(self):
        import pdb; pdb.set_trace()
        args = ('asset_id', 'money_to_receive', 'app_id')
        parameters = get_parameters(args, args)
        # response = api.create_sell_order(parameters['asset_id'], parameters['money_to_receive'], app_id=parameters['app_id'])
        response = api.create_sell_order(
            parameters['asset_id'],
            parameters['money_to_receive'],
            app_id=parameters['app_id']
        )
        response_data = response.json()
        
        pass

    # @route('/buy', methods=['POST'])
    # def buy(self):
    #     args = ('market_hash_name', 'total_price')
    #     parameters = get_parameters(args, args)
    #


api = SteamAPI()
application, orm = initialize()
AccountAPIViewSet.register(application)
