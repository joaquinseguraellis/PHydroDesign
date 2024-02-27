"""
This module is used to install and import the require libraries.
"""

import pip, sys, os, xlrd, pickle, datetime
import copy, csv, getpass, shutil, platform
import pkg_resources
import sklearn.metrics

import multiprocessing as mp
import time as tm
import scipy.stats as sp

from pathlib import Path
from IPython.display import clear_output

try:
    import numpy as np
    import numpy.ma as ma
except:
    pip.main(['install', 'numpy'])
    import numpy as np
    import numpy.ma as ma


del pip

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
