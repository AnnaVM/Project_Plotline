import numpy as np
import numba

@numba.jit(nopython=True)
def fill_distances( D1, x, y ):
    for i in range( x.shape[0] ):
        for j in range( y.shape[0] ):
            d = 0
            for k in range( y.shape[1] ):
                d += x[i,k]**2 - y[j,k]**2
            D1[i,j] = abs( d )

@numba.jit(nopython=True)
def accumulate_distances( D0, D1 ):
    for i in range( D1.shape[0] ):
        for j in range( D1.shape[1] ):
            D1[i, j] += min( D0[i, j], D0[i, j+1], D0[i+1, j] )

def _traceback(D):
    # Pre-allocate over-sized arrays
    p = np.zeros( D.shape[0] + D.shape[1], dtype=int )
    q = np.zeros( D.shape[0] + D.shape[1], dtype=int )
    n = find_path( D, p, q )
    return( p[n::-1], q[n::-1] )
    
@numba.jit(nopython=True)
def find_path(D, p, q):
    i = D.shape[0] - 2
    j = D.shape[1] - 2
    # Counter within the arrays p and q
    n = 0
    p[0] = i
    q[0] = j
    while ((i > 0) or (j > 0)):
        if D[i,j] <= D[i, j+1] and D[i, j]<=D[i+1, j]:
            i -= 1
            j -= 1
        elif D[i, j+1] <= D[i+1, j]:
            i -= 1
        else:
            j -= 1
        n += 1
        p[n] = i
        q[n] = j
    return(n)            

def dtw(x, y):
    """
    Computes Dynamic Time Warping (DTW) of two sequences.

    :param array x: N1*M array
    :param array y: N2*M array

    Returns the minimum distance, the cost matrix, the accumulated cost matrix, and the wrap path.
    """
    assert len(x)
    assert len(y)
    r, c = len(x), len(y)
    D0 = np.zeros((r + 1, c + 1))
    D0[0, 1:] = np.inf
    D0[1:, 0] = np.inf
    D1 = D0[1:, 1:] # view
    fill_distances( D1, x, y )
    C = D1.copy()
    accumulate_distances( D0, D1 )
    if len(x)==1:
        path = np.zeros(len(y)), range(len(y))
    elif len(y) == 1:
        path = range(len(x)), np.zeros(len(x))
    else:
        path = _traceback(D0)
    return D1[-1, -1] / sum(D1.shape), C, D1, path


## def _traceback(D):
##     i, j = array(D.shape) - 2
##     p, q = [i], [j]
##     while ((i > 0) or (j > 0)):
##         tb = argmin((D[i, j], D[i, j+1], D[i+1, j]))
##         if (tb == 0):
##             i -= 1
##             j -= 1
##         elif (tb == 1):
##             i -= 1
##         else: # (tb == 2):
##             j -= 1
##         p.insert(0, i)
##         q.insert(0, j)
##     return array(p), array(q)
