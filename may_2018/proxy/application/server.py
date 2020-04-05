from flask import Flask
from flask_classy import route
from flask_rest.views import BaseAPIViewSet
from flask_rest.request import get_parameters
from flask_rest.response import response
from flask_rest.exceptions import APIError
from flask_rest.application import initialize

from proxy import Proxy


class ProxyAPIViewSet(BaseAPIViewSet):
    route_base = '/api/proxies/'
    model = Proxy

    @route('/reserve', methods=['POST'])
    def reserve(self):
        queryset = self.model.query \
            .filter_by(status=self.model.STATUS_VACANT)

        instance = queryset.first()
        if instance:
            instance.status = instance.STATUS_RESERVED
            orm.session.add(instance)
            orm.session.commit()

            data = instance.as_dict()
            return response(200, data)
        else:
            return response(404)

    @route('/<index>/release', methods=['POST'])
    def release(self, index):
        instance = self.model.query.get(index)
        if instance:
            instance.status = instance.STATUS_VACANT
            orm.session.add(instance)
            orm.session.commit()

            data = instance.as_dict()
            return response(200, data)
        else:
            return response(404)

    @route('/status', methods=['GET'])
    def status(self):
        queryset = self.model.query
        data = {
            'total': queryset.count(),
            'reserved':
                queryset.filter_by(status=self.model.STATUS_RESERVED).count(),
            'vacant':
                queryset.filter_by(status=self.model.STATUS_VACANT).count(),
        }
        return response(200, data)


application, orm = initialize()

@application.errorhandler(APIError)
def handle_api_error(error):
    return response(error.status_code, error=error.information)

ProxyAPIViewSet.register(application)
