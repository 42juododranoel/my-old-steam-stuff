import pickle
from enum import IntEnum
from datetime import datetime, timedelta

import numpy
import pandas
import peakutils
from scipy.misc import derivative
import scipy.integrate as integrate
from scipy.interpolate import interp1d
from scipy.signal import argrelextrema
from scipy.signal import find_peaks_cwt
from matplotlib import pyplot
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc

from external.peakdetect import peakdetect


class TrendSignals(IntEnum):
    DOWN = -1
    NO = 0
    UP = 1


class ExtremaSignals(IntEnum):
    MIN = -1
    NO = 0
    MAX = 1


class BaseGraph:
    def __init__(self):
        self.frames = {}
        self.statistics = {}

    # --- Frame helpers --- #

    @property
    def pickle(self):
        return f'storage/frame.pickle'

    def dump(self):
        with open(self.pickle, 'wb') as file:
            pickle.dump(self.frame, file)

    def load(self):
        self.frame = pandas.read_pickle(self.pickle)

    @staticmethod
    def crop(frame, days_count):
        border = datetime.now() - timedelta(days=days_count)
        return frame.loc[border:].copy()

    # --- Analyze --- #

    @staticmethod
    def analyze_trend(frame, column):
        y = frame[column]
        x = range(len(y))
        f = interp1d(x, y, bounds_error=False)

        x_fake = numpy.arange(0.0, len(x), 1.0)
        dfdx = derivative(f, x_fake, dx=1e-6)
        dfdx[0] = dfdx[1]
        dfdx[-1] = dfdx[-2]

        dfdx_pos = []
        dfdx_neg = []
        for value in dfdx:
            if value > 0:
                dfdx_pos.append(value)
                dfdx_neg.append(0)
            elif value < 0:
                dfdx_pos.append(0)
                dfdx_neg.append(abs(value))
            else:
                dfdx_pos.append(0)
                dfdx_neg.append(0)

        f_dfdx_pos = interp1d(x, dfdx_pos, bounds_error=False)
        f_dfdx_neg = interp1d(x, dfdx_neg, bounds_error=False)

        s_dfdx_pos, error = integrate.quad(f_dfdx_pos, x[0], x[-1])
        s_dfdx_neg, error = integrate.quad(f_dfdx_neg, x[0], x[-1])

        frame[f'{column}_dfdx'] = dfdx
        frame[f'{column}_dfdx_pos'] = dfdx_pos
        frame[f'{column}_dfdx_neg'] = dfdx_neg
        stats = {}
        if s_dfdx_pos > s_dfdx_neg:
            stats[f'{column}_s_dfdx_diff'] = s_dfdx_pos - s_dfdx_neg
            stats[f'{column}_trend'] = TrendSignals.UP
        elif s_dfdx_pos < s_dfdx_neg:
            stats[f'{column}_s_dfdx_diff'] = s_dfdx_neg - s_dfdx_pos
            stats[f'{column}_trend'] = TrendSignals.DOWN
        else:
            stats[f'{column}_s_dfdx_diff'] = 0
            stats[f'{column}_trend'] = TrendSignals.NO

        return frame, stats

    @staticmethod
    def analyze_extremas(frame, column, method):
        y = numpy.array(frame[column])

        if method == 'argrelextrema':
            minimas = argrelextrema(y, numpy.less, order=3)[0]
            maximas = argrelextrema(y, numpy.greater, order=3)[0]

        elif method == 'peakutils':
            threshold = 0.15
            distance = 4
            maximas = peakutils.peak.indexes(
                y, thres=threshold, min_dist=distance
            )
            minimas = peakutils.peak.indexes(
                -1 * y, thres=threshold, min_dist=distance
            )

        elif method == 'cwt':
            maximas = find_peaks_cwt(y, numpy.arange(1, 5))
            minimas = find_peaks_cwt(-1 * y, numpy.arange(1, 5))

        elif method == 'peakdetect':
            peaks = peakdetect(y, lookahead=2, delta=2)
            maximas = [index for index, value in peaks[0]]
            minimas = [index for index, value in peaks[1]]

        label = f'{column}_{method}_extrema'
        stats = {label: {'minimas': minimas, 'maximas': maximas}}
        return frame, stats

    @staticmethod
    def analyze_deviation(frame, column, interval):
        rolling = frame[column].rolling(interval)
        label = f'{column}_std_{interval}'
        frame[label] = rolling.std()
        stats = {label: frame[label].mean()}
        return frame, stats

    @staticmethod
    def analyze_mean(frame, column, interval):
        rolling = frame[column].rolling(interval)
        label = f'{column}_mean_{interval}'
        frame[label] = rolling.mean()
        return frame, {}

    def analyze(self):
        pass

    # --- Plot --- #

    @staticmethod
    def plot_line(axis, x, y_height=0, color=None, title=None):
        y = [y_height for i in range(x_length)]
        axis.plot(x, y, ls='--', color=color)
        axis.set_title(title)

    @staticmethod
    def plot_simple(axis, x, y, color=None, title=None):
        axis.plot(x, y, color=color)
        axis.set_title(title)

    @staticmethod
    def plot_scatter(axis, x, y, color=None, title=None):
        axis.scatter(x, y, color=color)
        axis.set_title(title)

    @staticmethod
    def plot_candlestick(axis, frame, label, title=None):
        frame_ohlc = frame[label].resample('D').ohlc()
        frame_ohlc.reset_index(inplace=True)
        frame_ohlc['index'] = frame_ohlc['index'].map(mdates.date2num)
        axis.xaxis_date()
        candlestick_ohlc(axis, frame_ohlc.values, colorup='green')
        axis.set_title(title)

    def plot_extremas_helper(self, axis, column, frame_name, method):
        label = f'{column}_{method}_extrema'
        minima_ids = self.statistics[frame_name][label]['minimas']
        maxima_ids = self.statistics[frame_name][label]['maximas']
        for indexes in [minima_ids, maxima_ids]:
            x = []
            y = []
            for index in indexes:
                x.append(self.frames[frame_name].index[index])
                y.append(self.frames[frame_name][column][index])
            self.plot_scatter(axis, x, y)

    def plot(self):
        pass
