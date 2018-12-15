__author__ = "Ehsaneddin Asgari"
__license__ = "Apache 2"
__version__ = "1.0.0"
__maintainer__ = "Ehsaneddin Asgari"
__email__ = "asgari@berkeley.edu"
__project__ = "LLP - DiTaxa"
__website__ = "https://llp.berkeley.edu/ditaxa/"


from scipy import stats
from sklearn.preprocessing import normalize
import numpy as np
from sklearn.preprocessing import  normalize
import matplotlib
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.spatial.distance import pdist, squareform
from fastcluster import linkage

def get_sym_kl_rows(A):
    '''
    :param A: matrix A
    :return: Efficient implementation to calculate kl-divergence between rows in A
    '''
    norm_A=normalize(A+np.finfo(np.float64).eps, norm='l1')
    a=stats.entropy(norm_A.T[:,:,None], norm_A.T[:,None,:])
    return a+a.T

def generate_binary(N):
    return [''.join(list(b)[::-1]) for b in  ['{:0{}b}'.format(i, N) for i in range(2**N)][1::]]


def get_kl_rows(A):
    '''
    :param A: matrix A
    :return: Efficient implementation to calculate kl-divergence between rows in A
    '''
    norm_A=normalize(A+np.finfo(np.float64).eps, norm='l1')
    return stats.entropy(norm_A.T[:,:,None], norm_A.T[:,None,:])

def normalize_mat(A,norm ='l1', axis=1):
    '''

    :param A:
    :param norm:
    :param axis: 0 colum
    :return:
    '''

    return normalize(A, norm=norm, axis=axis)

def plot_histogram(A):
    A=A.flatten()
    plt.hist(A, bins=100)  # arguments are passed to np.histogram
    plt.title("Histogram with 'auto' bins")
    plt.show()


def seriation(Z,N,cur_index):
    '''
        got the code from: https://gmarti.gitlab.io/ml/2017/09/07/how-to-sort-distance-matrix.html
        input:
            - Z is a hierarchical tree (dendrogram)
            - N is the number of points given to the clustering process
            - cur_index is the position in the tree for the recursive traversal
        output:
            - order implied by the hierarchical tree Z

        seriation computes the order implied by a hierarchical tree (dendrogram)
    '''
    if cur_index < N:
        return [cur_index]
    else:
        left = int(Z[cur_index-N,0])
        right = int(Z[cur_index-N,1])
        return (seriation(Z,N,left) + seriation(Z,N,right))

def compute_serial_matrix(dist_mat,method="ward"):
    '''
        got the code from: https://gmarti.gitlab.io/ml/2017/09/07/how-to-sort-distance-matrix.html
        input:
            - dist_mat is a distance matrix
            - method = ["ward","single","average","complete"]
        output:
            - seriated_dist is the input dist_mat,
              but with re-ordered rows and columns
              according to the seriation, i.e. the
              order implied by the hierarchical tree
            - res_order is the order implied by
              the hierarhical tree
            - res_linkage is the hierarhical tree (dendrogram)

        compute_serial_matrix transforms a distance matrix into
        a sorted distance matrix according to the order implied
        by the hierarchical tree (dendrogram)
    '''
    N = len(dist_mat)
    flat_dist_mat = squareform(dist_mat)
    res_linkage = linkage(flat_dist_mat, method=method,preserve_input=True)
    res_order = seriation(res_linkage, N, N + N-2)
    seriated_dist = np.zeros((N,N))
    a,b = np.triu_indices(N,k=1)
    seriated_dist[a,b] = dist_mat[ [res_order[i] for i in a], [res_order[j] for j in b]]
    seriated_dist[b,a] = seriated_dist[a,b]

    return seriated_dist, res_order, res_linkage

def get_borders(mylist):
    val=0
    borders=[]
    for i,v in enumerate(mylist):
        if i==0:
            val=v
        else:
            if not v==val:
                borders.append(i)
                val=v
    return borders
