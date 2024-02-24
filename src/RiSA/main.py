from .tools import *

def f():
    return np.random.random((231, 350, 3, 48))

if __name__=='__main__':
    data = bin_file(Path('prueba'), f)