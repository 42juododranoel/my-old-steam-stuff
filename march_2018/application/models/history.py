import pickle
from datetime import datetime, timedelta

import numpy
import pandas
import sqlalchemy as orm
from sqlalchemy.orm import relationship

from steam.utils import get_text_between
from models.utils import get_trend, get_extremas
from core.database import transaction, BaseModel
from core.graph import BaseGraph


class History(BaseModel, BaseGraph):
    __tablename__ = 'histories'
    id = orm.Column(orm.BigInteger, primary_key=True)

    screen_id = orm.Column(orm.BigInteger, orm.ForeignKey('screens.id'))
    screen = relationship('Screen', back_populates='histories')

    data = orm.Column(orm.types.JSON)

    created_at = orm.Column(orm.DateTime)

    def __init__(self, screen_id, response_text):
        self.screen_id = screen_id

        self.data = self.parse_response_to_data(response_text)
        self.frames = {'original': self.parse_data_to_frame(self.data)}
        self.frames['daily'] = self.get_daily_frame()
        self.frames['month'] = self.get_month_frame()
        self.frames['week'] = self.get_week_frame()

        self.statistics = {key: {} for key in ['daily', 'month', 'week']}
        self.shortcuts = {key: {} for key in ['daily', 'month', 'week']}
        self.created_at = datetime.now()

    @property
    def url(self):
        name = self.screen.market_hash_name
        replace = [(' ', '%20'), ("'", '%27'), ('(', '%28'), (')', '%29')]
        for before, after in replace:
            name = name.replace(before, after)
        url = f'https://steamcommunity.com/' \
            f'market/listings/{self.screen.api.market.app_id}/{name}'
        return url

    @staticmethod
    def parse_response_to_data(response_text):
        # TODO: try/except
        history = eval(get_text_between(response_text, 'var line1=', ';'))
        #
        pattern = '%b %d %Y %H: +0'
        data = {'date': [], 'price': [], 'count': []}
        for date, price, count in history:
            timestamp = datetime.strptime(date, pattern).timestamp()
            data['date'].append(timestamp)
            data['price'].append(price)
            data['count'].append(int(count))
        return data

    @staticmethod
    def parse_data_to_frame(data):
        data_copy = data.copy()
        index = data_copy.pop('date')
        index = [datetime.fromtimestamp(t) for t in index]
        frame = pandas.DataFrame(data_copy, index=index)
        return frame

    def get_daily_frame(self):
        return self.frames['original'].resample('D').mean()

    def get_month_frame(self):
        return self.crop(self.frames['original'], days_count=31)

    def get_week_frame(self):
        return self.crop(self.frames['original'], days_count=7)

    def analyze_daily_frame(self):
        frame_name = 'daily'
        frame = self.frames[frame_name].copy()
        statistics = self.statistics[frame_name].copy()

        frame, stats = self.analyze_mean(frame, 'price', '168h')
        statistics.update(stats)

        # TODO: Поискать хороший показатель для rolling
        frame, stats = self.analyze_trend(frame, 'price_mean_168h')
        statistics.update(stats)

        self.frames[frame_name] = frame
        self.statistics[frame_name].update(statistics)
        trend = self.statistics[frame_name]['price_mean_168h_trend']
        self.shortcuts[frame_name]['trend'] = trend

    def analyze_month_frame(self):
        frame_name = 'month'
        frame = self.frames[frame_name].copy()
        statistics = self.statistics[frame_name].copy()

        frame, stats = self.analyze_mean(frame, 'price', '168h')
        statistics.update(stats)

        frame, stats = self.analyze_trend(frame, 'price_mean_168h')
        statistics.update(stats)

        frame, stats = self.analyze_mean(frame, 'price', '4h')
        statistics.update(stats)

        frame, stats = self.analyze_extremas(
            frame, 'price_mean_4h', 'argrelextrema'
        )
        statistics.update(stats)

        frame, stats = self.analyze_deviation(frame, 'price', '24h')
        statistics.update(stats)

        self.frames[frame_name] = frame
        self.statistics[frame_name].update(statistics)
        trend = self.statistics[frame_name]['price_mean_168h_trend']
        self.shortcuts[frame_name]['trend'] = trend

    def analyze_week_frame(self):
        frame_name = 'week'
        frame = self.frames[frame_name].copy()
        statistics = self.statistics[frame_name].copy()

        frame, stats = self.analyze_mean(frame, 'price', '168h')
        statistics.update(stats)

        # TODO: Поискать хороший показатель для rolling
        frame, stats = self.analyze_trend(frame, 'price_mean_168h')
        statistics.update(stats)

        self.frames[frame_name] = frame
        self.statistics[frame_name].update(statistics)
        trend = self.statistics[frame_name]['price_mean_168h_trend']
        self.shortcuts[frame_name]['trend'] = trend

    def analyze(self):
        self.analyze_daily_frame()
        self.analyze_month_frame()
        self.analyze_week_frame()

        self.days_count = self.frames['daily'].shape[0]

        self.daily_trend = self.shortcuts['daily']['trend']
        self.month_trend = self.shortcuts['month']['trend']
        self.week_trend = self.shortcuts['week']['trend']
