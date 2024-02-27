"""
This module is used for frequency analysis of hydrological data.
"""

# Libraries

import os, pickle
import sklearn.metrics

import numpy as np

# from .libraries import *

# Functions

def test_code(f):
    """
    Tool for testing a function.
    """
    import cProfile, pstats, io
    from pstats import SortKey
    pr = cProfile.Profile()
    pr.enable()
    f()
    pr.disable()
    s = io.StringIO()
    sortby = SortKey.CUMULATIVE
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

def bin_file(
        path, func, params=None
):
    """
    This function execute func with given params and saves its return to a
    binary file with pickle. If file already exists it opens it.
    """
    if not os.path.exists(path):
        if params is not None:
            res = func(*params)
        else:
            res = func()
        with open(path, 'wb') as f:
            pickle.dump(res, f)
    else:
        with open(path, 'rb') as f:
            res = pickle.load(f)
    return res

def cut(
        data: np.ndarray, x, y, bbox,
):
    """
    Cut a numpy.array to a bbox.

    Parameters
    ----------
    data : 2-D ndarray with shape (X, Y).
        The data to cut.
    x, y : 1-D ndarray with floats of shape (X,) and (Y,) each.
        x and y coordinates.
    bbox : 1-D ndarray or list of shape (4,).
        bbox[0] : float.
            x low limit.
        bbox[1] : float.
            x high limit.
        bbox[2] : float.
            y low limit.
        bbox[3] : float.
            y high limit.

    Returns
    -------
    data : 2-D ndarray with shape (X_, Y_).
        The result of cutting data.
    x, y : 1-D ndarray with floats of shape (X,) and (Y,) each.
        The result of cutting x and y coordinates.

    Examples
    --------
    Suppose we have the 2-D narray data

    >>> import numpy as np

    >>> data = np.random.random((100, 200))
    >>> print('data shape =', data.shape)

    that has x and y coordinates

    >>> x = np.arange(800, 900)
    >>> y = np.arange(100, 300)
    >>> print('x shape =', x.shape)
    >>> print('y shape =', y.shape)
    
    and we want to cut it to the bbox list

    >>> bbox = [810, 890, 120, 250]

    we can apply the "cut" function to do it.

    >>> new_data = cut(data, x, y, bbox)
    >>> print('new_data shape =', new_data.shape)
    >>> print('x shape =', x.shape)
    >>> print('y shape =', y.shape)

    """
    data = data[x >= bbox[0], :]
    x = x[x >= bbox[0]]
    data = data[x <= bbox[1], :]
    x = x[x <= bbox[1]]
    data = data[:, y >= bbox[2]]
    y = y[y >= bbox[2]]
    data = data[:, y <= bbox[3]]
    y = y[y <= bbox[3]]
    return data, x, y

def search_loc(
        lons_, lats_, lons, lats,
):
    """
    Search for nearest coordinates from lons and lats to lons_ and lats_.
    Return a numpy.array with the index where to find those coordinates.
    """
    lons  = np.sort(lons)
    lats  = np.sort(lats)
    low_lons  = np.searchsorted(lons, lons_)-1
    high_lons = np.searchsorted(lons, lons_)
    low_lats  = np.searchsorted(lats, lats_)-1
    high_lats = np.searchsorted(lats, lats_)
    return np.array([low_lons, high_lons, low_lats, high_lats])

def inside_bbox(
        bbox, y, x,
):
    """
    Wheter or not a point is inside a square bbox limits.

    Parameters:

        - bbox : dtype=list, tuple or numpy.array.
            bbox[3] and bbox[2] are higher and lower "y" limits. bbox[1] and bbox[0] are higher and lower "x" limits.
        - y, x : coordinates, dtype=float or int.

    Returns:

        - bool : True if point (x, y) is inside square bbox limits.
    """
    return y < bbox[3] and y > bbox[2] and x < bbox[1] and x > bbox[0]

def root_mean_squared_error(obs, est):
    """
    Return the Root of the Mean Squared Error between "obs" and "est", which are the observed and estimated data.
    """
    est = est[~np.isnan(obs)]
    obs = obs[~np.isnan(obs)]
    obs = obs[~np.isnan(est)]
    est = est[~np.isnan(est)]
    return sklearn.metrics.mean_squared_error(obs, est, squared=False)

def percentage_error(obs, est, _abs=True):
    """
    Return the Percentage Error between "obs" and "est", which are the observed and estimated data.
    """
    if _abs:
        return 100 * np.abs((est - obs) / obs)
    elif ~_abs:
        return 100 * (est - obs) / obs
    else:
        raise ValueError('"_abs" must be True or False.')

def nash_coeficient(obs, est):
    """
    Return de Nash-Sutcliffe model efficiency coefficient. First the original, second the normalized and last the modified for extreme values.
    """
    NSE = 1 - np.nansum((obs - est)**2) / np.nansum((obs - np.nanmean(obs))**2)
    return [
        NSE,
        1 / (2 - NSE),
        1 - np.nansum(np.absolute(obs - est)) / np.nansum(np.absolute(obs - np.nanmean(obs))),
    ]

def minimum_lenght(arr, lenght):
    return arr[~np.isnan(arr)].shape[0] >= lenght