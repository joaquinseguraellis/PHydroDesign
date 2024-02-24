from .tools import *
from importlib.resources import files

def f():
    return np.random.random((231, 350, 3, 48))

def get():
    return bin_file(files('.output').joinpath('prueba'), f)