import pandas as pd
import numpy as np

from bqplot import DateScale, LinearScale, OrdinalScale, Axis, Lines, Scatter, Bars, Hist, Figure
from bqplot.interacts import (
    FastIntervalSelector, IndexSelector, BrushIntervalSelector,
    BrushSelector, MultiSelector, LassoSelector, PanZoom, HandDraw
)
from traitlets import link
from collections import OrderedDict
from IPython.display import display
from ipywidgets import ToggleButtons, VBox, HTML


class Cyplot:
    def __init__(self, data, index=None, ylabel=None, interaction=None, cb=None):
        
        self.set_data(data, index, ylabel)
        
        self.create_fig(self.data)
        
        # self.enable, self.disable, 
        # self.on
        
        
        self.create_plot(interaction, cb)
    
        
    def set_data(self, data, index, ylabel):
        
        if isinstance(data, pd.Series):
            self.data = data
            
        elif isinstance(data, pd.DataFrame):
            # Pandas DataFrame
                
            if index is not None:
                self.data = data.set_index(index)
            else:
                self.data = data
        else:
            print("The input data type is not supported")

        
        self.xlabel = self.data.index.name if self.data.index.name is not None else "index"
        
        self.cols = list(self.data)

        self.ylabel = ylabel if ylabel is not None else self.cols[0][0]

        self.legends = [' '.join(legend) for legend in self.cols]
        
        self.xScale = LinearScale()
        self.yScale = LinearScale()
        
    
    def create_fig(self, ts):
        
        ts.sort_index(inplace=True)
        
        df = ts.reset_index() # time = ts.Time
        
        self.xd = df[self.xlabel]
        self.yd = df[self.cols].T

        
        line = Lines(x = self.xd,y = self.yd, scales = {'x': self.xScale, 'y': self.yScale},labels=self.legends, display_legend=True)# axes_options=axes_options)

        x_axis = Axis(scale=self.xScale, label=self.xlabel, grid_lines='none')
        y_axis = Axis(scale=self.yScale, label=self.ylabel, orientation='vertical', grid_lines='none')

        self.fig = Figure(marks=[line], axes=[x_axis,y_axis])
        
    
    def create_plot(self, interaction=None, cb=None):# xScale=None, yScale=None, mark=None, fig=None):
        
        xScale = self.xScale #  if xScale is None else xScale
        yScale = self.yScale #  if yScale is None else yScale
        fig = self.fig # if fig is None else fig
        mark = fig.marks # if mark is None else mark

        self.deb = HTML()
        self.default_inter(cb) #xScale, yScale, fig, mark, deb)

        if interaction is None: 
            odict = self.interaction_dict
        else:
            # Interaction is given 
            odict = OrderedDict()
            if isinstance(interaction, list):
                for inter in interaction:
                    if inter in self.interaction_dict:
                        odict[inter] = self.interaction_dict[inter]
            else:
                if interaction in self.interaction_dict:
                    odict[interaction] = self.interaction_dict[interaction]
                    
        selection_interacts = ToggleButtons(options=odict)

        link((selection_interacts, 'value'), (fig, 'interaction'))
        
        self.vbox = VBox([self.deb, fig, selection_interacts], align_self='stretch')
    
    def __display__(self):
        # Not Able to Figure Out
        
        print("display")
        # return 5#self.fig
        display(self.fig)
        # return 1
    
    def default_inter(self, cb):#, xScale, yScale, fig, mark, deb):
        
        xScale = self.xScale #  if xScale is None else xScale
        yScale = self.yScale #  if yScale is None else yScale
        fig = self.fig # if fig is None else fig
        mark = fig.marks # if mark is None else mark
        
        
        multi_sel = MultiSelector(scale=xScale, marks=mark)
        br_intsel = BrushIntervalSelector(scale=xScale, marks=mark)
        index_sel = IndexSelector(scale=xScale, marks=mark)
        int_sel = FastIntervalSelector(scale=xScale, marks=mark)
        
        br_sel = BrushSelector(x_scale=xScale, y_scale=yScale, marks=mark, color='red')

        # Hand Draw might be added later
        # hds = [HandDraw(lines=line) for line in mark]
        
        pz = PanZoom(scales={'x': [xScale], 'y': [yScale]})

        self.deb.value = ''#'[]'
        
        # deb = HTML(value='[]')
        
        def test_callback(change):
            self.deb.value = "The selected range is {} on {} with {}".format(change.new, self.xlabel, br_intsel.selke)#str(change.new)
    
        def brush_callback(change):
            #deb.value = str(br_sel.selected)
            xr = [br_sel.selected[0][0],br_sel.selected[1][0]]
            yr = [br_sel.selected[0][1],br_sel.selected[1][1]]
            self.deb.value = "The brushed area is {} on {},  {} on {}".format(str(xr),self.xlabel,str(yr), self.ylabel)

        
        if cb is not None:
            def mycb(change):
                
                self.deb.value = str(cb(change.new))# cb(change.new)
                
            test_callback = mycb
            brush_callback = mycb
        
        #         multi_sel.observe(test_callback, names=['selected'])
        #         br_intsel.observe(test_callback, names=['brushing'])#'selected'])
        #         index_sel.observe(test_callback, names=['selected'])
        #         int_sel.observe(test_callback, names=['selected'])

        #         br_sel.observe(brush_callback, names=['selected'])#'brushing'])
        #         # selctedX, selectedY
        
        
        # Initialize Selector
        # Initialize CB
        # Observe
        
        # Can listen to many traitlets here 
        # General one, brushing 
        # Other selected, color, line_width ..., selected_x, selected_y 
        
        multi_sel.observe(test_callback, names=['brushing'])
        br_intsel.observe(test_callback, names=['brushing'])
        index_sel.observe(test_callback, names=['brushing'])
        int_sel.observe(test_callback, names=['brushing'])
        
        br_sel.observe(brush_callback, names=['brushing'])#'brushing'])
        # selctedX, selectedY
        
        
        odict = OrderedDict([('FastInterval', int_sel), ('Index', index_sel),
                             ('BrushX', br_intsel), ('MultiBrush', multi_sel), ('Brush', br_sel),
                             ('PanZoom', pz), ('None', None)])
        
        self.interaction_dict = odict
        
        # return odict
    
    def setScale(self,xScale=None, yScale=None):
        if xScale is not None:
            self.xScale = xScale
        if yScale is not None:
            self.yScale = yScale
    
    def show(self):
        # self.fig?
        return self.vbox
    
    def show_ref(self):
        # self.fig?
        return self.fig

        
    def connect(self, fig=None, vbox=None):
        # Connect fig / vbox?
        
        if fig is not None:
            fig = self.fig
        if vbox is not None:
            vbox = self.vbox
    