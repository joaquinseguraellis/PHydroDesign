"""
This module is used to install and import the require libraries.
"""

import pip, sys, os, math, json, xlrd, pickle, datetime, copy, csv, getpass, shutil, platform
import matplotlib
import pkg_resources
import sklearn.metrics

import multiprocessing as mp
import time as tm

from subprocess import Popen
from collections import namedtuple
from pathlib import Path
from dateutil.relativedelta import relativedelta
from IPython.display import clear_output

try:
    import numpy as np
    import numpy.ma as ma
except:
    pip.main(['install', 'numpy'])
    import numpy as np
    import numpy.ma as ma

try:
    import pyhomogeneity
except:
    pip.main(['install', 'pyhomogeneity'])
    import pyhomogeneity

try:
    import pymannkendall
except:
    pip.main(['install', 'pymannkendall'])
    import pymannkendall

try:
    import scipy.stats as sp
    import scipy.special as ss
    import scipy
except:
    pip.main(['install', 'scipy'])
    import scipy.stats as sp
    import scipy.special as ss
    import scipy

try:
    from tqdm import tqdm
except:
    pip.main(['install', 'tqdm'])
    from tqdm import tqdm

try:
    import matplotlib.pyplot as plt
except:
    pip.main(['install', 'matplotlib'])
    import matplotlib.pyplot as plt

try:
    import xarray as xr
except:
    pip.main(['install', 'xarray'])
    import xarray as xr

try:
    import pandas as pd
except:
    pip.main(['install', 'pandas'])
    import pandas as pd

try:
    import statsmodels.api as sm
except:
    pip.main(['install', 'statsmodels'])
    import statsmodels.api as sm

try:
    import requests
except:
    pip.main(['install', 'requests'])
    import requests

try:
    import openpyxl
except:
    pip.main(['install', 'openpyxl'])
    import openpyxl

try:
    import imageio
except:
    pip.main(['install', 'imageio'])
    import imageio

try:
    import global_land_mask
except:
    pip.main(['install', 'global_land_mask'])
    import global_land_mask

try:
    import h5py
except:
    pip.main(['install', 'h5py'])
    import h5py

PROVINCES_SHP_PATH = pkg_resources.resource_filename('RiSA', 'data/shp/ne_10m_admin_1_states_provinces.shp')
COUNTRIES_SHP_PATH = pkg_resources.resource_filename('RiSA', 'data/shp/ne_10m_admin_0_countries.shp')
ARG_SHP_PATH = pkg_resources.resource_filename('RiSA', 'data/shp/argentina.shp')

clear_output()

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
