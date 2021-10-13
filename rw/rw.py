from tqdm import tqdm

import numpy as np
import numpy.random as rand
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
from itertools import cycle
palette = cycle(sns.color_palette())


from sklearn.neighbors import KDTree, BallTree


def cosine_sim(a, b):
    return np.inner(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def cosine_dist(a, b):
    return 1- cosine_sim(a, b)

def euclid_dist(a, b):
    return np.linalg.norm(a-b)



class MetaRW:
    def __init__(self, rw_class, n_walks, **rw_kwargs):
        self.walkers = [rw_class(**rw_kwargs) for _ in range(n_walks)]
        
    def step(self, i):
        samples = [w.step(i) for w in self.walkers]
        inds, rows, durations = list(zip(*samples))
        return inds, rows, durations
        





class RW:
    abs_min = 4
    abs_max = 15
    def __init__(self, is_2D, directory="./"):
        if is_2D:
            self.space = np.loadtxt(directory+"embeddings_tsne.tsv", delimiter="\t")
        else:
            self.space = np.loadtxt(directory+"embeddings.tsv", delimiter="\t")
        self.tree = BallTree(self.space)
        self.n = self.space.shape[0]
        
        self.meta = pd.read_csv(directory+"meta.csv")
        
        
    def sample_duration(self, row):
        secs = row.duration
        if secs < RW.abs_min:
            return 0, secs

        return self.sample_duration_normal(secs)
    
    
    def sample_duration_unif(self, secs):
        start = secs*0.3 # WADSWORTH CONSTANT
        max_length = secs - start - (secs*0.1)
        return start, rand.uniform(min(RW.abs_min, max_length), min(max_length, RW.abs_max))

        
        
    def sample_duration_normal(self, secs):
        start = secs*0.3 # WADSWORTH CONSTANT
        
        length = secs - start - (secs*0.1)
        m = (min(length, RW.abs_max) - RW.abs_min)/2
        s = rand.normal(m, scale=2)
        return start, min(RW.abs_max, abs(s)+RW.abs_min)

        
class Line2D(RW):
    def __init__(self, n_neighbours=40, hist_len=5, directory="./"):
        super().__init__(is_2D=True, directory=directory)
        
        self.init = rand.randint(self.n)
        self.cur = self.init

        self.n_neighbours = n_neighbours
        self.hist = -hist_len
        
        self.sampled = [self.cur]
        
    def get_neighbours(self, cur_index, n_neighbours=None):
        if n_neighbours is None:
            n_neighbours = self.n_neighbours
        return self.tree.query(self.space[cur_index].reshape(1, -1), n_neighbours)[1][0, 1:]
    
    
    
    
    def step(self, i):
        ref = self.sampled[0] if self.hist < 0 else self.sampled[ref_i]
        cur_dist = euclid_dist(self.space[ref], self.space[self.cur])

        
        try:
            neighs = self.get_neighbours(self.cur)
            neighs = list(filter(lambda n: n not in self.sampled, neighs))
            neighs = [n for n in neighs if euclid_dist(self.space[ref], self.space[n]) > cur_dist]
            self.cur = neighs[rand.randint(len(neighs))]
            
        except ValueError:
#             neighs = self.get_neighbours(self.cur, 3*self.n_neighbours)
#             neighs = list(filter(lambda n: n not in self.sampled, neighs))
#             neighs = [n for n in neighs if euclid_dist(self.space[ref], self.space[n]) > cur_dist]
#             self.cur = neighs[rand.randint(self.n)]

#             self.cur = rand.randint(self.n)
            self.cur = rand.choice(list(set(range(self.n)) - set(self.sampled)))
#             cur = sampled[move_back]
#             move_back -= 1
        
        cur_row = self.meta.iloc[self.cur]
        return self.cur, cur_row, self.sample_duration(cur_row)
        
        