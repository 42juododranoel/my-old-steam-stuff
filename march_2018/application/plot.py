from matplotlib import pyplot
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc

from core.graph import BaseGraph


class History(BaseGraph):
    def plot(self):
        figure, axes = pyplot.subplots(4, sharex=True)

        self.plot_simple(axes[0], self.frame.index, self.frame['price'])


        # self.plot_simple(axes[0], self.frame.index, self.frame['price'])
        # self.plot_extremas_helper(axes[0], 'price', 'daily', 'argrelextrema')
        #
        # self.plot_simple(axes[1], self.frame.index, self.frame['price'])
        # self.plot_extremas_helper(axes[1], 'price', 'small', 'peakutils')
        #
        # self.plot_simple(axes[2], self.frame.index, self.frame['price'])
        # self.plot_extremas_helper(axes[2], 'price', 'cwt')
        #
        # self.plot_simple(axes[3], self.frame.index, self.frame['price'])
        # self.plot_extremas_helper(axes[3], 'price', 'peakdetect')

        pyplot.show()


#
# def find_profitable_price(mode):
#     from datetime import datetime, timedelta
#     now = datetime.now()
#     week_ago = now - timedelta(days=7)
#     recent_prices = []
#     for index in self.stats['price_peakdetect_extrema'][mode][::-1]:
#         if self.frame.index[index] < week_ago:
#             break
#         recent_prices.append(self.frame['price'][index])
#
#     return sum(recent_prices) / len(recent_prices)
#
# buy_price = find_profitable_price('minimas')
# sell_price = find_profitable_price('maximas')


if __name__ == '__main__':
    g = History()
    g.load()
    g.plot()
