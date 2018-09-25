# Put here temperarily, will be removed later
import numpy as np
import random
from sklearn import datasets, linear_model
from sklearn.kernel_ridge import KernelRidge
import pandas as pd

def get_pts(p, loc):
    idx = [loc[i] for i in range(p['pts_span'][0], p['pts_span'][1])]
    idx.extend(p['minmax_idx'])
    return idx

class Resample:
    def __init__(self, data, cb=None):
        
        self.box = None
        self.func = self.resample
        #self.box = []
        self.vals = []
        self.interp(data)# [] # This would be combined with regulus later
        
    def cb(self, val):
        self.box = val
    
    def get_input(self):
        
        y = np.array(self.vals)
        y = y.reshape(-1,1)
        # y = np.expand_dims(y, axis=1)
        return self.preds(y)
    
    def add_samples(self, num=None):
        if num is None:
            num = 1
        # use random sample for now 
        if self.box is None:
            print("No range selected!")
        elif self.func is None:
            print("No sample function specified!")
        else:
            for i in range(num):
                self.vals.append(self.func(self.box))
            
            self.box = None
        
    def sample_func(self, func):
        # Sample method, analytic function for now
        self.func = func
    
    
    # Will put random sampler here for simplicity
    def resample(self, box):
        # a axis is y. y axix is x
        yrange = [box[0][0],box[1][0]]  # x axis 
        xrange = [box[0][1],box[1][1]]  # y axis 
        # if xrange[0] is None:
        if yrange[0] is not None:
            return random.uniform(yrange[0], yrange[1])
            
        # Not sure what to do if no yrange is given 
        # self.func(self.data)
        
    def interp(self, data=None, y=None, x=None):
        # Here will compute linear regression for each dimension and use them to predict x (Inverse)
        # dims = data.shape[1]-1
        if data is not None:
            if isinstance(data, pd.DataFrame):
                x = data.values[:,:-1]
                y = data.values[:,-1].reshape(-1,1)
        
        clf = KernelRidge(alpha=1.0, kernel='rbf')

        clf.fit(y, x)
        
        self.preds = clf.predict
        