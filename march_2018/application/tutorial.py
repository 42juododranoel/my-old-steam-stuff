import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

x = np.linspace(0,2*np.pi,100)
y = np.sin(x) + np.random.random(100) * 0.4
yhat = savgol_filter(y, 51, 3)  # window size 51, polynomial order 3

plt.plot(x,y)
plt.plot(x,yhat, color='red')
plt.show()
