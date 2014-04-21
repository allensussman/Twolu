# perform singular value decomposition on the ratings table

import recsys.algorithm
from recsys.utils.svdlibc import SVDLIBC

recsys.algorithm.VERBOSE = True

svdlibc = SVDLIBC('ml-10M100K/ratings.dat')
svdlibc.to_sparse_matrix(sep='::', format={'col':0, 'row':1, 'value':2, 'ids': int})
svdlibc.compute(k=100)
svd = svdlibc.export()
svd.save_model('svd-10M-k100')
