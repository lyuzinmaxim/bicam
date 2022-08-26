# #https://mmas.github.io/least-squares-fitting-numpy-scipy
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np


# def func(x, a, b, c):
#     return a * np.exp(-b * x) + c

def func(x, a, b):
    return a + b/x

# xdata = np.linspace(1, 50, 50)
# y = func(xdata, 18, 15682)
# rng = np.random.default_rng()
# y_noise = 500 * rng.normal(size=xdata.size)
# ydata = y + y_noise

x = np.array([150., 140., 130., 120., 110., 100., 90., 80., 70., 60.])
y = np.array([89., 97., 105., 115., 127., 139., 156., 176., 201., 233])


# plt.plot(xdata, ydata, 'r-', label='data')

# popt, pcov = curve_fit(func, xdata, ydata)
popt, pcov = curve_fit(func, x, y)


print(popt, pcov)
# plt.plot(xdata, func(xdata, *pqopt), xdata, ydata, 'r-')
plt.xlabel("distance, sm")
plt.ylabel("disparity, pixel")
plt.plot(np.linspace(30, 150, 120), func(np.linspace(30, 150, 120), *popt), x, y, 'r-')

plt.show()
