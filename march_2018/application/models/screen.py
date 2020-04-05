from datetime import datetime

import pandas
import sqlalchemy as orm
from sqlalchemy.orm import relationship

from core.signals import ItemSignals
from core.database import transaction, BaseModel
from models.price import Price
from models.history import History


class Screen(BaseModel):
    __tablename__ = 'screens'
    id = orm.Column(orm.BigInteger, primary_key=True)

    item_name_id = orm.Column(orm.BigInteger)
    market_hash_name = orm.Column(orm.Text)

    prices = relationship('Price', back_populates='screen')
    histories = relationship('History', back_populates='screen')

    created_at = orm.Column(orm.DateTime)

    def __init__(self, item_name_id, market_hash_name,
                 api=None, application=None):
        self.item_name_id = item_name_id
        self.market_hash_name = market_hash_name
        self.created_at = datetime.now()

        self.application = application
        self.logger = application.logger
        self.database = application.database
        self.session = application.session
        self.api = api

        self.history = None
        self.strategy = None

    def __str__(self):
        return f'#{self.item_name_id} ("{self.market_hash_name}")'

    def get_action(self):
        self.logger.debug('Choosing next action')
        if not self.history:
            return self.analyze_history, [], {}
        elif not self.strategy:
            return self.choose_strategy, [], {}
        else:
            return self.strategy.get_next_action, [], {}

    def analyze_history(self):
        self.logger.debug('Analyzing history')

        history = self.get_history()
        self.session.add(history)
        self.session.commit()

        history.analyze()
        history.frame = history.frames['daily']
        history.dump()
        input()

    def get_price(self):
        # TODO: response.json() may return trash
        response = self.api.market.get_price_histogram(self.item_name_id)
        price = Price(self.id, response.json(), self.api.market.currency)
        return price

    def get_history(self):
        # TODO: response.json() may return trash
        response = self.api.market.get_price_history(self.market_hash_name)
        history = History(self.id, response.text)
        return history
