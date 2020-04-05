import pickle
from datetime import datetime, timedelta

import numpy
import pandas
from scipy.misc import derivative
import scipy.integrate as integrate
from scipy.interpolate import interp1d
from scipy.signal import argrelextrema
from matplotlib import pyplot
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc


def get_trend(y):
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

    result = {
        'dfdx': dfdx,
        'dfdx_pos': dfdx_pos,
        'dfdx_neg': dfdx_neg,
        's_dfdx_pos': s_dfdx_pos,
        's_dfdx_neg': s_dfdx_neg,
        's_dfdx_diff': None,
        'direction': None,
    }
    if s_dfdx_pos > s_dfdx_neg:
        result['s_dfdx_diff'] = s_dfdx_pos - s_dfdx_neg
        result['direction'] = 1
    elif s_dfdx_pos < s_dfdx_neg:
        result['s_dfdx_diff'] = s_dfdx_neg - s_dfdx_pos
        result['direction'] = -1
    else:
        result['s_dfdx_diff'] = 0
        result['direction'] = 0

    return result


def get_extremas(x, y):
    minima_indexes = argrelextrema(numpy.array(y), numpy.less)[0]
    maxima_indexes = argrelextrema(numpy.array(y), numpy.greater)[0]
    result = {
        'minima': {'x': [], 'y': []},
        'maxima': {'x': [], 'y': []},
        'last': None
    }
    to_iterate = (
        ('minima', minima_indexes),
        ('maxima', maxima_indexes),
    )
    for name, indexes in to_iterate:
        for index in indexes:
            result[name]['x'].append(x[index])
            result[name]['y'].append(y[index])

    if result['minima']['x'][-1] < result['maxima']['x'][-1]:
        result['last'] = 1
    elif result['minima']['x'][-1] > result['maxima']['x'][-1]:
        result['last'] = -1
    else:
        result['last'] = 0

    return result


def find_peaks(method, y, args=None, kwargs=None):
    if method == 'argrelextrema':
        from scipy.signal import argrelextrema
        indexes = argrelextrema(
            numpy.array(y),
            numpy.greater
        )[0]

    elif method == 'peakutils':
        import peakutils.peak
        indexes = peakutils.peak.indexes(
            numpy.array(y),
            thres=10.0/max(y),
            min_dist=5
        )

    elif method == 'cwt':
        from scipy.signal import find_peaks_cwt
        indexes = find_peaks_cwt(
            y,
            numpy.arange(1, 10)
        )

    elif method == 'peakdetect':
        import peakdetect
        peaks = peakdetect.peakdetect(
            numpy.array(y),
            lookahead=2,
            delta=2
        )
        indexes = [index for index, value in peaks[0]]

    elif method == 'findpeaks':
        from find_peaks import detect_peaks
        indexes = detect_peaks(y, 1.0)

    return indexes


def plot_data_frame(pickle):
    frame = pandas.read_pickle(pickle)

    def draw_redline(axis):
        values = [0 for i in range(frame.shape[0])]
        axis.plot(frame.index, values, ls='--', color='red')

    def plot_extremas(label, axis, title=None, redline=False):
        result = get_extremas(frame.index, frame[label])
        axis.scatter(result['minima']['x'], result['minima']['y'], color='green')
        axis.scatter(result['maxima']['x'], result['maxima']['y'], color='orange')
        if redline:
            draw_redline(axis)
        axis.set_title(title)

    def plot_candlestick(label, axis, title=None, redline=False):
        frame_ohlc = frame[label].resample('D').ohlc()
        frame_ohlc.reset_index(inplace=True)
        frame_ohlc['index'] = frame_ohlc['index'].map(mdates.date2num)
        axis.xaxis_date()
        candlestick_ohlc(axis, frame_ohlc.values, colorup='green')
        if redline:
            draw_redline(axis)
        axis.set_title(title)

    def plot_simple(labels, axis, title=None, redline=False):
        for label in labels:
            axis.plot(frame.index, frame[label])
        if redline:
            draw_redline(axis)
        axis.set_title(title)

    figure, axes = pyplot.subplots(6, sharex=True)
    # plot_simple(['price_mean_4h'], axes[0], 'Price')
    # plot_extremas('price_mean_4h', axes[0], 'Price and extremas')

    # plot_simple(['price', 'price_mean_4h'], axes[1], 'Price mean')

    # plot_simple(['price_168h_dfdx'], axes[2], 'Price derivative', redline=True)

    # plot_simple(['price_std_24h'], axes[3], 'Price deviation')

    x = frame.index
    y = frame['price']

    indexes = find_peaks('argrelextrema', y)
    axes[0].plot(x, y)
    axes[0].scatter(
        [frame.index[i] for i in indexes],
        [frame['price'][i] for i in indexes],
        color='red'
    )

    indexes = find_peaks('peakutils', y)
    axes[1].plot(x, y)
    axes[1].scatter(
        [frame.index[i] for i in indexes],
        [frame['price'][i] for i in indexes],
        color='red'
    )

    indexes = find_peaks('cwt', y)
    axes[2].plot(x, y)
    axes[2].scatter(
        [frame.index[i] for i in indexes],
        [frame['price'][i] for i in indexes],
        color='red'
    )

    indexes = find_peaks('peakdetect', y)
    axes[3].plot(x, y)
    axes[3].scatter(
        [frame.index[i] for i in indexes],
        [frame['price'][i] for i in indexes],
        color='red'
    )

    indexes = find_peaks('findpeaks', y)
    axes[4].plot(x, y)
    axes[4].scatter(
        [frame.index[i] for i in indexes],
        [frame['price'][i] for i in indexes],
        color='red'
    )

    from scipy.signal import argrelmax
    indexes = argrelmax(numpy.array(y))[0]
    axes[5].plot(x, y)
    axes[5].scatter(
        [frame.index[i] for i in indexes],
        [frame['price'][i] for i in indexes],
        color='red'
    )





    # import numpy as np
    # from scipy.signal import savgol_filter

    # x = frame.index
    # y = frame['price']
    #
    # import numpy as np
    #
    # import peakutils.peak
    # print('Detect peaks with minimum height and distance filters.')
    # indexes = peakutils.peak.indexes(np.array(y),
    #     thres=7.0/max(y), min_dist=2)
    # print('Peaks are: %s' % (indexes))
    # axes[1].plot(x, y)
    # axes[1].scatter(
    #     [frame.index[i] for i in indexes],
    #     [frame['price'][i] for i in indexes],
    #     color='red'
    # )

    #
    # from scipy import signal
    # yhat = savgol_filter(y, 25, 3)  # window size 51, polynomial order 3
    # axes[1].plot(x, y)
    # # axes[1].plot(x, yhat, color='orange')
    # peakind = signal.find_peaks_cwt(y, np.arange(1,10))
    # axes[1].scatter(
    #     [frame.index[i] for i in peakind],
    #     [frame['price'][i] for i in peakind],
    #     color='red'
    #
    # )

    # # yhat = savgol_filter(y, 25, 3)  # window size 51, polynomial order 3
    # axes[1].plot(x, y)
    # # axes[1].plot(x, yhat, color='red')
    #
    # ext = get_extremas(x, y)
    # axes[1].scatter(ext['maxima']['x'], ext['maxima']['y'], color='green')
    # axes[1].scatter(ext['minima']['x'], ext['minima']['y'], color='red')
    # for x, y in zip(ext['maxima']['x'], ext['maxima']['y']):
    #     print(x, frame['price'].rolling('2h').std()[x])

    # import numpy as np
    # import scipy.fftpack
    #
    # x = [i for i in range(len(frame.index))]
    # N = len(x)
    # y = frame['price']
    #
    # w = scipy.fftpack.rfft(y)
    # f = scipy.fftpack.rfftfreq(N, x[1]-x[0])
    # spectrum = w**2
    #
    # cutoff_idx = spectrum < (spectrum.max()/5)
    # w2 = w.copy()
    # w2[cutoff_idx] = 0
    #
    # y2 = scipy.fftpack.irfft(w2)
    #
    # axes[1].plot(frame.index, y)
    # axes[1].plot(frame.index, y2, color='red')


    #
    #
    # import pdb; pdb.set_trace()

    # figure1 = pyplot.figure()
    # axis = figure1.add_subplot(111)
    # plot_candlestick('price', axis, 'Price candlestick')


    # plot_candlestick('price', axes[0], 'asdawd')


    pyplot.show()

    # --- --- --- #

    # import numpy as np
    #
    # # compute sigmoid nonlinearity
    # def sigmoid(x):
    #     output = 1/(1+np.exp(-x))
    #     return output
    #
    # # convert output of sigmoid function to its derivative
    # def sigmoid_output_to_derivative(output):
    #     return output*(1-output)
    #
    # # input dataset
    # X = np.array([  [0,1],
    #                 [0,1],
    #                 [1,0],
    #                 [1,0] ])
    #
    # # output dataset
    # y = np.array([[0,0,1,1]]).T
    #
    # # seed random numbers to make calculation
    # # deterministic (just a good practice)
    # np.random.seed(1)
    #
    # # initialize weights randomly with mean 0
    # synapse_0 = 2*np.random.random((2,1)) - 1
    #
    # for iter in range(10000):
    #     # forward propagation
    #     layer_0 = X
    #     layer_1 = sigmoid(np.dot(layer_0,synapse_0))
    #
    #     # how much did we miss?
    #     layer_1_error = layer_1 - y
    #
    #     # multiply how much we missed by the
    #     # slope of the sigmoid at the values in l1
    #     layer_1_delta = layer_1_error * sigmoid_output_to_derivative(layer_1)
    #     synapse_0_derivative = np.dot(layer_0.T,layer_1_delta)
    #
    #     # update weights
    #     synapse_0 -= synapse_0_derivative
    #
    # print("Output After Training:")
    # print(layer_1)



    # import numpy as np
    # import random
    #
    # # m denotes the number of examples here, not the number of features
    # def gradientDescent(x, y, theta, alpha, m, numIterations):
    #     xTrans = x.transpose()
    #     for i in range(0, numIterations):
    #         hypothesis = np.dot(x, theta)
    #         loss = hypothesis - y
    #         # avg cost per example (the 2 in 2*m doesn't really matter here.
    #         # But to be consistent with the gradient, I include it)
    #         cost = np.sum(loss ** 2) / (2 * m)
    #         # print("Iteration %d | Cost: %f" % (i, cost))
    #         # avg gradient per example
    #         gradient = np.dot(xTrans, loss) / m
    #         # update
    #         theta = theta - alpha * gradient
    #     return theta
    #
    #
    # def genData(numPoints, bias, variance):
    #     x = np.zeros(shape=(numPoints, 2))
    #     y = np.zeros(shape=numPoints)
    #     # basically a straight line
    #     for i in range(0, numPoints):
    #         # bias feature
    #         x[i][0] = 1
    #         x[i][1] = i
    #         # our target variable
    #         y[i] = (i + bias) + random.uniform(0, 1) * variance
    #     return x, y
    #
    # # gen 100 points with a bias of 25 and 10 variance as a bit of noise
    # x, y = genData(100, 25, 10)
    # m, n = np.shape(x)
    # numIterations= 100000
    # alpha = 0.0005
    # theta = np.ones(n)
    # theta = gradientDescent(x, y, theta, alpha, m, numIterations)
    # print(theta)
    #
    # import pdb; pdb.set_trace()
    #
    # figure, axes = pyplot.subplots(2, sharex=True)

    # axis = axes[0]
    # axis.plot([i[1] for i in x], y)

    # pyplot.show()


    # --- --- --- #





if __name__ == '__main__':
    plot_data_frame('storage/frame.pickle')
