from datetime import datetime

import sqlalchemy as orm
from sqlalchemy.orm import relationship

from core.database import transaction, BaseModel


class Price(BaseModel):
    __tablename__ = 'prices'

    id = orm.Column(orm.BigInteger, primary_key=True)

    screen_id = orm.Column(orm.BigInteger, orm.ForeignKey('screens.id'))
    screen = relationship('Screen', back_populates='prices')

    lowest_sell_order = orm.Column(orm.Float)
    highest_sell_order = orm.Column(orm.Float)
    lowest_buy_order = orm.Column(orm.Float)
    highest_buy_order = orm.Column(orm.Float)

    currency_id = orm.Column(orm.Integer)

    created_at = orm.Column(orm.DateTime)

    def __init__(self, screen_id, json, currency_id):
        self.screen_id = screen_id
        self.currency_id = currency_id
        self.created_at = datetime.now()

        highest_buy_order = json.get('highest_buy_order')
        if highest_buy_order:
            self.highest_buy_order = int(highest_buy_order) / 100
        else:
            self.highest_buy_order = None

        lowest_sell_order = json.get('lowest_sell_order')
        if lowest_sell_order:
            self.lowest_sell_order = int(lowest_sell_order) / 100
        else:
            self.lowest_sell_order = None

        self.highest_sell_order = json['graph_max_x']
        self.lowest_buy_order = json['graph_min_x']
