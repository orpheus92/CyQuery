import pandas as pd
import numpy as np

from bqplot import DateScale, LinearScale, Axis, Lines, Scatter, Bars, Hist, Figure
from bqplot.interacts import (
    FastIntervalSelector, IndexSelector, BrushIntervalSelector,
    BrushSelector, MultiSelector, LassoSelector, PanZoom, HandDraw
)
from traitlets import link

from ipywidgets import ToggleButtons, VBox, HTML


class Cyplot:
    def __init__(self, ts, index=None, ylabel=None):

        if not isinstance(ts, pd.DataFrame):
            print("You need to give df as input")  
            return
        elif ts.index.name is not None:
            self.ts = ts
        elif index is not None:
            self.ts = ts.set_index(index)
        else:
            print("You need to specify index for DF")
            return 

        self.plot_ts(self.ts, ylabel)
        
        self.create_inter()
    
    
    def plot_ts(self, ts, yl):
        self.xl = ts.index.name

        yls = list(ts)

        # Right now Assume lowest level in hierarchy is the legend
        if yl is not None:
            self.yl = yl
            self.lbs = [j[-1] for j in yls]

        else:
            cols = len(yls)
            hier = len(yls[0])
        
            # THIS MIGHT BE CHANGED LATER
            self.yl = yls[0]
                    
            self.lbs = [j[-1] for j in yls]
        
        # Default Linear Scale
        self.xScale = LinearScale()
        self.yScale = LinearScale()
        
        ts.sort_index(inplace=True)
        self.df = ts.reset_index() # time = ts.Time
        
        self.xd = self.df[self.xl]
        self.yd = self.df[self.lbs].T

        line = Lines(x = self.xd,y = self.yd, scales = {'x': self.xScale, 'y': self.yScale},labels=self.lbs,display_legend=True)# axes_options=axes_options)

        xax = Axis(scale=self.xScale, label=self.xl, grid_lines='none')
        yax = Axis(scale=self.yScale, label=self.yl, orientation='vertical', grid_lines='none')

        self.fig = Figure(marks=[line], axes=[xax,yax])
        
        
    def create_inter(self, xScale=None, yScale=None, mark=None, fig=None):
        
        xScale = self.xScale if xScale is None else xScale
        yScale = self.yScale if yScale is None else yScale
        fig = self.fig if fig is None else fig
        mark = fig.marks if mark is None else mark

        multi_sel = MultiSelector(scale=xScale, marks=mark)
        br_intsel = BrushIntervalSelector(scale=xScale, marks=mark)
        index_sel = IndexSelector(scale=xScale, marks=mark)
        int_sel = FastIntervalSelector(scale=xScale, marks=mark)

        # Hand Draw might be added later
        # hds = [HandDraw(lines=line) for line in mark]
        
        pz = PanZoom(scales={'x': [xScale], 'y': [yScale]})

        deb = HTML()
        deb.value = '[]'
        
        def test_callback(change):
            deb.value = str(change.new)
    
        multi_sel.observe(test_callback, names=['selected'])
        br_intsel.observe(test_callback, names=['selected'])
        index_sel.observe(test_callback, names=['selected'])
        int_sel.observe(test_callback, names=['selected'])
        
    
        from collections import OrderedDict
        
        odict = OrderedDict([('FastIntervalSelector', int_sel), ('IndexSelector', index_sel),
                             ('BrushIntervalSelector', br_intsel), ('MultiSelector', multi_sel), 
                             ('PanZoom', pz), ('None', None)])
        
        #         for ind, hd in enumerate(hds):
        #             odict['HandDraw'+str(ind)] = hd 
            
        selection_interacts = ToggleButtons(options=odict)

        link((selection_interacts, 'value'), (fig, 'interaction'))
        
        self.vbox = VBox([deb, fig, selection_interacts], align_self='stretch')
    

        
    def setScale(self,xScale=None, yScale=None):
        if xScale is not None:
            self.xScale = xScale
        if yScale is not None:
            self.yScale = yScale
        