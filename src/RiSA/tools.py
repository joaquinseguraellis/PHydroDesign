"""
This module is used for frequency analysis of hydrological data.
"""

# Libraries

from .libraries import *

# Functions

def bin_file(path, func, params=None):
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
