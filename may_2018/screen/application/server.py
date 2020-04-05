from threading import Thread

from flask import Flask
from flask_classy import route
from flask_rest.views import BaseAPIViewSet
from flask_rest.request import get_parameters
from flask_rest.response import response
from flask_rest.exceptions import APIError
from flask_rest.application import initialize

from screen import Screen


screens = {}


class ScreenAPIViewSet(BaseAPIViewSet):
    route_base = '/api/screens/'
    model = Screen

    @route('/create', methods=['POST'])
    def create(self):
        required = ('item_name_id', 'market_hash_name')
        parameters = get_parameters(self.model.fields, required)

        instance = self.model(**parameters)
        orm.session.add(instance)
        orm.session.commit()

        thread = Thread(target=instance.run)
        screens[instance.id] = thread
        thread.start()

        data = instance.as_dict()
        return response(201, data)

    @route('/<index>/delete', methods=['DELETE'])
    def delete(self, index):
        instance = self.model.query.get(index)
        if instance:
            thread = screens.pop(instance.id)
            thread.stop()
            orm.session.delete(instance)
            orm.session.commit()
            return response(200)
        else:
            return response(404)

    @route('/status', methods=['GET'])
    def status(self):
        queryset = self.model.query
        data = {
            'count': {
                'database': queryset.count(),
                'threads': len(screens),
            },
        }
        return response(200, data)


application, orm = initialize()

@application.errorhandler(APIError)
def handle_api_error(error):
    return response(error.status_code, error=error.information)

ScreenAPIViewSet.register(application)
