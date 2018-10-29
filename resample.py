import numpy as np
import random
from sklearn import linear_model
from sklearn.kernel_ridge import KernelRidge
import pandas as pd

# This should not be here
# def get_pts(p, loc):
#     idx = [loc[i] for i in range(p['pts_span'][0], p['pts_span'][1])]
#     idx.extend(p['minmax_idx'])
#     return idx

class Resample:
    def __init__(
        self,
        model=None,
        sampleFunc=None,
        sampleAttr='range'
        ):

        """
        sampleFunc: a function that should take in a 1 to n-dim intervals, 
                    number of samples to generate, and generate new samples
       
        model: a model that should take 1D input and return nD output after fitting nD pts
        
        sampleAttr: whether to sample the range space or domain space 
        """
        self.model = model if model else self.model_ 
        self.sampleFunc = sampleFunc if sampleFunc else self.sampleFunc_
        self.sampleAttr = sampleAttr
        
        self.reset()
    
    # ! Reset the data, dimensions, domain, range, clear new samples and current model
    def reset(self):
        self.X, self.Y= None, None
        self.X_, self.Y_ = None, None
        self.domain_, self.range_ = [], []
        self.dims, self.val = [], []
        self.pred = None
        self.newX_ = None

    # ! Add pts to the current model
    def add_pts(self, data=None, X=None, Y=None, dims=None, val=None):
        if X and Y:
            Y = Y.reshape(-1,1)
            pass 
        elif isinstance(data, np.ndarray):
            #if not dims or not val:
            #elif isinstance(dims,int) and isinstance(val, int):
            if type(dims) is int and type(val) is int:
                X, Y = data[:, :dims], data[:,val].reshape(-1,1)
            elif type(dims) is list and type(val) is list and type(dims[0]) is int:
                X, Y = data[:,dims], data[:, val].reshape(-1,1)
            else:
                X, Y = data[:, :-1], data[:, -1].reshape(-1,1)

        elif isinstance(data, pd.DataFrame):
            if type(dims) is int and type(val) is int:
                X, Y = data.values[:, :dims], data.values[:,val].reshape(-1,1)
            elif type(dims) is list and type(val) is list and set(dims)<set(data.columns) and set(val)<set(data.columns):
                X = data[dims].values
                Y = data[val].values.reshape(-1,1)
            else:
                X = data.values[:,:-1]
                Y = data.values[:,-1].reshape(-1,1)

        self.update_(X,Y)
    
    # ! Update the data based pts added 
    def update_(self, X, Y):
        # ! Update stored X, Y
        if self.X is None or self.Y is None:
            self.X, self.Y = X, Y
        
        elif X.shape[1] == self.X.shape[1]:
            self.X = np.vstack((self.X, X))
            self.Y = np.vstack((self.Y, Y))
        else:
            print("Data reset due to dimension mismatch")
            self.X_, self.Y_ = self.X, self.Y
            self.X, self.Y = X, Y

        # ! Update Global domain    
        _,c = self.X.shape
        xmin = np.amin(self.X, axis=0)
        xmax = np.amax(self.X, axis=0)

        self.domain_ = []
        for i in range(c):
            self.domain_.append([xmin[i],xmax[i]])
        self.domain = self.domain_[:]

        # ! Update Global range
        ymin = np.amin(self.Y)
        ymax = np.amax(self.Y)
        self.range_ = [ymin,ymax]
        self.range = self.range_[:]

    # ! Restore to previous state if data is added by accident
    def restore(self):
        self.X, self.Y = self.X_, self.Y_
        self.domain, self.range = self.domain_, self.range_

    # ! Build Model based on current points 
    def build(self):
        # print("self.x = ", self.X)
        # print("self.y = ", self.Y)
        self.pred = self.model(self.X, self.Y)

    # ! Generate number of new samples based on num
    def generate_samples(self, num=5, rebuild=False):

        if rebuild or not self.pred:
            self.build()
        
        if self.sampleAttr == 'range':
            newY = self.sampleFunc(self.range, num).reshape(-1,1)
            newX = self.pred(newY)

            # print("y to resample = ", newY)
            # print("new_x = ", newX)
        else:
            newX = self.sampleFunc(self.domain, num)

        if self.newX_ is None or self.newX_.shape[1]!=newX.shape[1]:
            self.newX_ = newX
        else:
            self.newX_ = np.vstack((self.newX_, newX))

    # ! Return new samples 
    @property
    def newsamples(self):
        return self.newX_

    # ! default model used
    def model_(self, x,y):
        clf = KernelRidge(alpha=1.0, kernel='rbf')
        clf.fit(y, x) 
        return clf.predict

    # ! default sample function
    def sampleFunc_(self, ranges, num):        
        ranges = [ranges] if not isinstance(ranges[0], list) else ranges
        dim = len(ranges)
        out = []
        for j in range(num):
            cur = []
            for i in range(dim):
                cur.append(random.uniform(ranges[i][0], ranges[i][1]))
            out.append(cur)
        return np.array(out)

    # ! CB function to update range/domain based on user's interaction 
    def change_range(self, val, dim=None):
        # ! Change the range based on selection
        if self.sampleAttr == "range":
            self.range = [val[0][0],val[1][0]]

        # ! To change domain, need to select the dimension 
        elif dim:
                d1,d2 = dim[0],dim[1]

                if d1>=0 and d1<len(self.domain):
                    if val[0][0]:
                        self.domain[d1][0] = val[0][0]
                    if val[1][0]:
                        self.domain[d1][1] = val[1][0]
                        
                if d2>=0 and d2<len(self.domain):
                    if val[0][1]:
                        self.domain[d2][0] = val[0][1]
                    if val[1][1]:
                        self.domain[d2][1] = val[1][1]


    def resample_data(self, data, num=5):
        self.reset()
        self.add_pts(data)
        # print("domain = ", self.domain)
        # print("rang = ", self.range)
        self.build()
        self.generate_samples(num=num)
        
def resample(model=None, sampleFunc=None, sampleAttr='range'):
    return Resample(model=model, sampleFunc=sampleFunc, sampleAttr=sampleAttr)