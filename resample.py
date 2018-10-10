import numpy as np
import random
from sklearn import linear_model
from sklearn.kernel_ridge import KernelRidge
import pandas as pd

def get_pts(p, loc):
    idx = [loc[i] for i in range(p['pts_span'][0], p['pts_span'][1])]
    idx.extend(p['minmax_idx'])
    return idx

class Resample:
    def __init__(self, data=None, x=None, y=None, pred_method="inverse_kernel_ridge", sample_func=None):
        
        # if no get_sample function is given, use random sampling 
        if sample_func is None:
            self.func = self.resample
        else:
            self.func = sample_func
        
        self.vals = []
        self.x = []
        self.p = pred_method

        if data is not None:
            if isinstance(data, pd.DataFrame):
                x = data.values[:,:-1]
                y = data.values[:,-1].reshape(-1,1)
            elif isinstance(data, np.ndarray):
                x = data[:,:-1]
                y = data[:,-1].reshape(-1,1)

        if x is not None and y is not None:
            if self.p == "inverse_kernel_ridge":
                self.interp(x,y) # [] # This would be combined with regulus later
            elif self.p == "bounding_box": 
                self.xrange = None
                self.compute_range(x,y)
            else:
                # print("method for generating new samples not recognized")
                raise ValueError('method for generating new samples not recognized')

    def cb(self, val, dim=None):
        # dim should be a list that specify the dimension for brushed area

        if self.p == "inverse_kernel_ridge":
            self.yrange = [val[0][0],val[1][0]]            
            
        elif self.p == "bounding_box": 
            if self.xrange is None:
                self.xrange = self.xrange_[:]
            if dim:
                d1,d2 = dim[0],dim[1]

                if d1>=0 and d1<len(self.xrange):
                    self.xrange[d1] = [val[0][0],val[1][0]]
                
                if d2>=0 and d2<len(self.xrange):
                    self.xrange[d2] = [val[0][1],val[1][1]]

    def get_input(self):
        if self.p == "inverse_kernel_ridge":
            y = np.array(self.vals)
            y = y.reshape(-1,1)
            return self.preds(y)

        elif self.p == "bounding_box": 

            return np.array(self.x)

    def add_samples(self, num=None):
        if num is None:
            num = 1
        # use random sample for now
 
        if self.p == "inverse_kernel_ridge":
            if (not hasattr(self, "yrange")) or self.yrange[0] is None or self.yrange[1] is None:
                self.yrange = self.yrange_
            # Generate y
            for i in range(num):    
                self.vals.append(self.func(self.yrange))

        elif self.p == "bounding_box": 
            # Fill None with Global range
            for c in range(len(self.xrange)):
                if self.xrange[c][0] is None:
                    self.xrange[c][0] = self.xrange_[c][0]    
                if self.xrange[c][1] is None:
                    self.xrange[c][1] = self.xrange_[c][1]
            # Generate input     
            for i in range(num):    
                self.x.append([self.func(x) for x in self.xrange])

    # Will put random sampler here for simplicity
    def resample(self, cur_range):
        return random.uniform(cur_range[0], cur_range[1])

    def interp(self, x,y):
        # Here will compute linear regression for each dimension and use them to predict x (Inverse)
        # dims = data.shape[1]-1

        # gloabl yrange         
        ymin = np.amin(y)
        ymax = np.amax(y)
        self.yrange_ = [ymin,ymax]

        clf = KernelRidge(alpha=1.0, kernel='rbf')
        clf.fit(y, x) 
        self.preds = clf.predict

    def compute_range(self, x,y):

        _,c = x.shape
        xmin = np.amin(x, axis=0)
        xmax = np.amax(x, axis=0)

        # Global xrange 
        self.xrange_ = []
        for i in range(c):
            self.xrange_.append([xmin[i],xmax[i]])
            



        