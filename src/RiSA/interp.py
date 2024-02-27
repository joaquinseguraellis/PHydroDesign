"""

"""

# Libraries

import os, pickle, copy
import scipy
import pykrige

import numpy as np

# Functions

# Classes

class IDW_Grid_Interpolation:
    """
    Inverse distance weighting interpolation for regular gridded data.
    Initiate the class with:
    - x, y (1D numpy.array or list): coordinates of gridded data.
    - x_, y_ (int or float): coordinates where interpolation is needed.
    - power (int or float): power for the equation, 1 and 2 are usually used.
    https://en.wikipedia.org/wiki/Inverse_distance_weighting
    """

    def __init__(self, x, y, x_, y_, power):
        self.x, self.y = x, y
        self.p = (x_, y_)
        x, y = np.meshgrid(self.x, self.y)
        self.get_d(x, y, x_, y_)
        self.get_w(power)

    def get_d(self, x, y, x_, y_):
        """
        
        """
        self.d = ((x - x_)**2 + (y - y_)**2)**0.5

    def get_w(self, power):
        """
        
        """
        self.w = self.d**-power

    def get_u(self, u):
        """
        
        """
        if np.any(self.tolerance):
            return u[self.tolerance][0]
        else:
            w = copy.deepcopy(self.w)
            w[np.isnan(u)] = np.nan
            return np.nansum(w * u) / np.nansum(w)
    
    def interp(self, grid_data, tolerance=0.001, axes=None):
        """
        
        """
        self.tolerance = self.d <= tolerance
        if axes is not None:
            grid_data = np.transpose(grid_data, axes)
        return np.array([self.get_u(_) for _ in grid_data])

class RegularGridInterpolator:
    """
    
    """

    def __init__(self, points, values, method) -> None:
        self.interps = np.array([
            scipy.interpolate.RegularGridInterpolator(points, _, method)
                for _ in values
        ])
    
    def interp(self, x, y):
        """
        
        """
        return np.array([_([x, y])[0] for _ in self.interps])