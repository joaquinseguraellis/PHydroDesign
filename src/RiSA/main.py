from .tools import *

def f():
    return np.random.random((231, 350, 3, 48))

def get():
    return bin_file(Path('prueba'), f)