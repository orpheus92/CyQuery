import pandas as pd
import numpy as np

from bqplot import DateScale, LinearScale, OrdinalScale, Axis, Lines, Scatter, Bars, Hist, Figure, ColorScale, ColorAxis
from bqplot.interacts import (
    FastIntervalSelector, IndexSelector, BrushIntervalSelector,
    BrushSelector, MultiSelector, LassoSelector, PanZoom, HandDraw
)
from traitlets import link  # , unlink
from collections import OrderedDict
from IPython.display import display
from ipywidgets import ToggleButtons, VBox, HTML, Layout
from bqplot.toolbar import Toolbar


class Cyplot:
    def __init__(self, data, index=None, ylabel=None, enable=None, debug=False, ptype=None, dims=None):
        self.debug = debug

        self.ptype = ptype
        
        self.dims = dims
        
        self.set_data(data, index, ylabel)

        self.interaction_map()

        self.enabled = []

        self.cbs = {}

        def cb0(change):
            # Internal cb for changing interaction in fig
            # print(change.new)
            self.cur_inter = change.new

        self.cb0 = cb0
        if enable is not None:
            
            self.enable(enable)

    def enable(self, interactions):
        self.old_enabled = self.enabled[:]

        if isinstance(interactions, str):
            interactions = [interactions]
        change = False
        for inter in interactions:
            if inter in self.interactions and inter not in self.enabled:
                change = True
                n = len(self.enabled)
                i = 0
                while (i < n):
                    e = self.enabled[i]
                    if self.interactions[e]['order'] > self.interactions[inter]['order']:
                        self.enabled.insert(i, inter)
                        break
                    i = i + 1
                if inter not in self.enabled:
                    self.enabled.append(inter)

        if change:
            self.updatebuttons(self.enabled)

    def updatebuttons(self, enabled):

        ops = self.get_input(enabled)

        # Keep try of current selected part
        # 　oldind = -1

        y = getattr(self, "selection_interacts", None)

        if y is not None:
            oldind = self.selection_interacts.index
            if self.old_enabled[oldind] in self.enabled:
                ind = self.enabled.index(self.old_enabled[oldind])
            else:
                # Current Inter is removed 
                # print("Before manually change IDX\n")
                # print(self.fig.interaction)
                # self.fig.interaction = None
                # with self.fig.hold_trait_notifications():
                #     # hold_trait_notifications()
                #     self.selection_interacts.index = self.old_enabled.index(self.enabled[0])
                # print("After index change due removal")
                # print(self.old_enabled.index(self.enabled[0]))
                # unlink((self.selection_interacts, 'value'), (self.fig, 'interaction'))
                # self.link[0].observe(self._update_target, names=self.source[1])
                # self.link[0].observe(self._update_source, names=self.target[1])
                print("REMOVE CURRENT INTER")
                # self.link.source[0].unobserve(self.link._update_target, names=self.link.source[1])
                # self.link.target[0].unobserve(self.link._update_source, names=self.link.target[1])
                self.link.unlink()
                oldind = -1
                # self.fig.interaction = None
                # print("After Remove", type(self.fig.interaction), self.fig.interaction)
                ind = 0
        else:
            oldind = -1

        self.selection_interacts = ToggleButtons(**ops)
        # print(self.selection_interacts.index)     
        # self.selection_interacts.value gives the current interaction (the one that is clicked)
        # print("Defaut selection interacts :")
        # print(self.selection_interacts.value)

        if oldind != -1:
            self.selection_interacts.index = ind
            # self.fig.interaction = self.selection_interacts.value

        # print("Before link happend\n", self.fig.interaction)
        # print("\n ========== \n", self.selection_interacts.value)

        self.fig.interaction = None

        # with dpdown.hold_trait_notifications():

        # with self.fig.hold_trait_notifications():

        # THERE SHOULD BE A CB HERE INSTEAD OF LINK

        self.fig.observe(self.cb0, names='interaction')

        self.link = link((self.selection_interacts, 'value'), (self.fig, 'interaction'))

        box_layout = Layout(display='flex',
                            flex_flow='column',
                            align_items='stretch')  # ,
        # border='solid',
        # width='50%')

        if self.debug:
            self.vbox = VBox([self.selection_interacts, self.fig, self.deb], layout=box_layout)            
        else:
            self.vbox = VBox([self.selection_interacts, self.fig], layout=box_layout)
        # self.vbox = VBox([self.selection_interacts, self.fig], layout=box_layout)

    def get_input(self, enabled):
        ops = {}
        ops['options'] = OrderedDict()
        ops['tooltips'] = []
        ops['icons'] = []
        ops['style'] = {'button_width': '40px'}  # ,#,'description_width':'0px'},
        ops['description'] = 'Interaction: '  # ,
        ops['layout'] = Layout(justify_content='flex-start',
                               margin='0px 0px 0px 0px')  # margin)#justify-content='fkex-end'

        for i in enabled:
            ops['options'].update({self.interactions[i]['order'] * ' ': self.interactions[i]['selector']})
            ops['tooltips'].append(self.interactions[i]['tooltip'])
            ops['icons'].append(self.interactions[i]['icon'])

        return ops

    def disable(self, interactions):

        self.old_enabled = self.enabled[:]

        if isinstance(interactions, str):
            interactions = [interactions]

        change = False

        for inter in interactions:
            if inter in self.enabled:
                change = True
                self.enabled.remove(inter)
            else:
                print('Could not disable ', inter)

        if change:
            self.updatebuttons(self.enabled)

    def on(self, interaction, cb):
        if isinstance(interaction, str):
            if interaction in self.enabled:
                if cb is not None:
                    self.cbs[interaction] = cb
                else:
                    if interaction in self.cbs:
                        del self.cbs[interaction]
            else:
                print("Can't turn on {}".format(interaction))

    def set_data(self, data, index, ylabel, add=False):

        
        self.xScale = LinearScale()
        #self.xScale.min, self.xScale.max = self.data.index.min(), self.data.index.max() # min=self.data.index.min(),max=self.data.index.max()
        self.xScale.allow_padding = False
        
        self.yScale = LinearScale()
        self.yScale.allow_padding = False
        
        # add decide whether draw figure on top
        if self.ptype == 'PCA':
            from sklearn.decomposition import IncrementalPCA
            ipca = IncrementalPCA(n_components=2, batch_size=3)
            # data.values
            if index is not None:
                Y = data[index].values
                xlist = list(data)#.columns
                xlist.remove(index)
                X = data[xlist].values
                
            else:
                X = data.values[:,:-1]
                Y = data.values[:,-1]
                
            ipca.fit(X)
            pca_data = ipca.transform(X)
            self.colors = Y
            
            cols = ['component1','component2']


            df = pd.DataFrame(pca_data, columns=cols)
            self.data = df#.set_index('component1')
            self.cols = ['component2']
            self.xlabel = 'component1'
            self.ylabel = 'component2'
            
            self.create_fig(self.data)
            
            return
        
        if isinstance(data, pd.Series):
            self.data = data

        elif isinstance(data, pd.DataFrame):
            # Pandas DataFrame
            if self.dims is not None and len(self.dims)>1:
                
                self.data = data[self.dims[0:2]]#.set_index(self.dims[0])
                self.colors = data.values[:,-1] if len(self.dims)==2 else data[self.dims[2]].values
                self.data.index.name = self.dims[0]

            elif index is not None:
                self.data = data.set_index(index)
            else:
                self.data = data
        else:
            print("The input data type is not supported")

        self.xlabel = self.data.index.name if self.data.index.name is not None else "index"
        
        self.cols = list(self.data) if self.dims is None else self.dims[1]
        
        
        # self.legends = [' '.join(legend) for legend in self.cols] if self.dims is None else self.dims[1:]

        y = getattr(self.data.columns, "levels", None)
        
        # Depends on dims/ylabel/level
        if ylabel is not None:
            self.ylabel = ylabel

        elif y is None:
            # One level 
            # self.legends
            self.ylabel = '' 
            if self.dims is not None and len(self.dims)>1:
                self.ylabel = self.dims[1]
                
        elif len(self.data.columns.levels[0]) == 1:
            self.legends = [' '.join(legend[1::]) for legend in self.cols]
            self.ylabel = self.data.columns.levels[0][0]
        else:
            self.ylabel = ''
        
        self.create_fig(self.data)

    def add_data(self, data, index=None, ylabel=None):
        # compare new data with existing data
        if isinstance(data, pd.Series) and isinstance(self.data, pd.Series):
            # concatenate
            if data.name == self.data.name:
                data = data.append(self.data, ignore_index=True)
                self.set_data(data, index, ylabel)
                # combine to dataframe
            elif (data.index == self.data.index).all():
                self.set_data(pd.concat([data, self.data]), index, ylabel)
            else:
                print("Could not combine two data series w/o same index and same column")

        elif isinstance(data, pd.DataFrame) and isinstance(self.data, pd.DataFrame):
            if (data.columns == self.data.columns).all():
                data = data.append(self.data, ignore_index=True)
                self.set_data(data, index, ylabel)

            elif ((data.index == self.data.index).all()) and (data.columns != self.data.columns).any():
                self.set_data(pd.concat([data, self.data], axis=1, join_axes=[data.index]), index, ylabel)
            else:
                print("Could not combine two dataframes w/o same index and same column")

        else:
            print("Could not combine two data of different types")

    def create_fig(self, ts):
        
        if self.ptype != 'PCA' and self.dims == None:
            ts.sort_index(inplace=True)
            df = ts.reset_index()  # time = ts.Time
        
        else:
            df = ts
        self.xd = df[self.xlabel] #  if self.dims == None else df[self.dims[0]]
        self.yd = df[self.cols].T

        if self.ptype =='PCA' or self.dims is not None:
            
            pplt = Scatter(x=self.xd.values.ravel(), y=self.yd.values.ravel(), scales={'x': self.xScale, 'y': self.yScale, 'color': ColorScale(scheme='YlOrRd')}, color = self.colors, default_size=32)#labels=self.legends,
                         #display_legend=True, line_style='solid', stroke_width = 0, marker = 'circle')
            # elif self.dims is not None:
            
        
        elif not self.ptype:
            pplt = Lines(x=self.xd, y=self.yd, scales={'x': self.xScale, 'y': self.yScale}, labels=self.legends,
                         display_legend=True, line_style='solid', stroke_width = 0, marker = 'circle')
        
        else: 
            pplt = Lines(x=self.xd, y=self.yd, scales={'x': self.xScale, 'y': self.yScale}, labels=self.legends,
                         display_legend=True, line_style='solid', selected_style={'opacity': '1'}, unselected_style={'opacity': '0.2'})  # enable_hover=True)  # axes_options=axes_options) 
            
        x_axis = Axis(scale=self.xScale, label=self.xlabel, grid_lines='none')
        y_axis = Axis(scale=self.yScale, label=self.ylabel, orientation='vertical', grid_lines='none')
        c_axis = ColorAxis(scale=ColorScale(scheme='YlOrRd'), orientation='vertical', side='right')

        print(type(pplt))
        axis = [x_axis, y_axis, c_axis] if isinstance(pplt, Scatter) else [x_axis, y_axis]
        
        if self.debug:
            margin = dict(top=0, bottom=40, left=50, right=50)
        else:
            margin = dict(top=0, bottom=50, left=50, right=50)

        self.fig = Figure(marks=[pplt], axes=axis, legend_location='top-right',
                          fig_margin=margin)  # {'top':50,'left':60})
        
        if self.debug:
            self.deb = HTML()
        # self.deb2 = HTML()
        y = getattr(self, "vbox", None)
        if y is not None:
            box_layout = Layout(display='flex',
                                flex_flow='column',
                                align_items='stretch')
            if self.debug:
                self.vbox = VBox([self.selection_interacts, self.fig, self.deb], layout=box_layout)            
            else:
                self.vbox = VBox([self.selection_interacts, self.fig], layout=box_layout)


    def _ipython_display_(self):

        if len(self.enabled) == 0:
            display(self.fig)
        else:
            display(self.vbox)

    def interaction_map(self):  # , xScale, yScale, fig, mark, deb):

        self.interactions = {}

        xScale = self.xScale  # if xScale is None else xScale
        yScale = self.yScale  # if yScale is None else yScale
        fig = self.fig  # if fig is None else fig
        mark = fig.marks  # if mark is None else mark

        multi_sel = MultiSelector(scale=xScale, marks=mark)
        br_intsel = BrushIntervalSelector(scale=xScale, marks=mark)
        index_sel = IndexSelector(scale=xScale, marks=mark)
        int_sel = FastIntervalSelector(scale=xScale, marks=mark)
        br_sel = BrushSelector(x_scale=xScale, y_scale=yScale, marks=mark, color='red')
        pz = PanZoom(scales={'x': [xScale], 'y': [yScale]})

        def cb1(change):
            if len(change.new) > 1:
                xr = change.new
                yr = [None, None]
                box = [[xr[0], yr[0]], [xr[1], yr[1]]]
                y = getattr(self, "cbs", None)

                if y is not None:
                    for k in self.cbs:
                        if 'brush' in k:
                            if self.debug:
                                self.deb.value = str(box)
                            cb = self.cbs[k]
                            cb(box)
                    #if 'brush' in self.cbs:
                    #    cb = self.cbs['brush']
                    #    cb(box)
            else:
                y = getattr(self, "cbs", None)
                if y is not None:
                    if 'bar' in self.cbs:
                        cb = self.cbs['bar']
                        cb(change.new)

        def cb2(change):
            box = self.interactions['brush']['selector'].selected
            y = getattr(self, "cbs", None)

            if y is not None:
                if 'brush' in self.cbs:
                    if self.debug:
                        self.deb.value = str(box)
                    cb = self.cbs['brush']
                    cb(box)

        def cb3(change):
            newscales = change.new
            y = getattr(self, "cbs", None)

            if y is not None:
                if 'panzoom' in self.cbs:
                    cb = self.cbs['panzoom']
                    cb(newscales['x'], newscales['y'])

        multi_sel.observe(cb1, names=['selected'])
        br_intsel.observe(cb1, names=['selected'])  # 'selected'])
        index_sel.observe(cb1, names=['selected'])
        int_sel.observe(cb1, names=['selected'])
        br_sel.observe(cb2, names=['brushing'])  # 'brushing'])
        pz.observe(cb3, names=['scales'])  # 'brushing'])

        self.interactions['brushes'] = {}
        self.interactions['brushes']['selector'] = multi_sel
        self.interactions['brushes']['icon'] = 'th-large'
        self.interactions['brushes']['tooltip'] = 'Multiple Brushes'
        self.interactions['brushes']['order'] = 0  # '   '
        self.interactions['brushes']['watch'] = 'selected'

        self.interactions['brush_x'] = {}
        self.interactions['brush_x']['selector'] = br_intsel
        self.interactions['brush_x']['icon'] = 'arrows-h'
        self.interactions['brush_x']['tooltip'] = 'Horizontal Brush'
        self.interactions['brush_x']['order'] = 1  # '     '
        self.interactions['brush_x']['watch'] = 'selected'

        self.interactions['brush_fast'] = {}
        self.interactions['brush_fast']['selector'] = int_sel
        self.interactions['brush_fast']['icon'] = 'exchange'
        self.interactions['brush_fast']['tooltip'] = 'Fast Brush'
        self.interactions['brush_fast']['order'] = 3  # '      '
        self.interactions['brush_fast']['watch'] = 'selected'

        self.interactions['brush'] = {}
        self.interactions['brush']['selector'] = br_sel
        self.interactions['brush']['icon'] = 'retweet'
        self.interactions['brush']['tooltip'] = 'Brush'
        self.interactions['brush']['order'] = 4  # '       '
        self.interactions['brush']['watch'] = 'brushing'

        self.interactions['bar'] = {}
        self.interactions['bar']['selector'] = index_sel
        self.interactions['bar']['icon'] = 'mouse-pointer'
        self.interactions['bar']['tooltip'] = 'Single Slider'
        self.interactions['bar']['order'] = 5  # ' '
        self.interactions['bar']['watch'] = 'selected'

        self.interactions['panzoom'] = {}
        self.interactions['panzoom']['selector'] = pz
        self.interactions['panzoom']['icon'] = 'arrows'
        self.interactions['panzoom']['tooltip'] = 'Pan Zoom'
        self.interactions['panzoom']['order'] = 6  # ''
        self.interactions['panzoom']['watch'] = 'scales'

        # Initialize Selector
        # Initialize CB
        # Observe

        # Can listen to many traitlets here
        # General one, brushing
        # Other selected, color, line_width ..., selected_x, selected_y

    def setScale(self, xScale=None, yScale=None):
        if xScale is not None:
            self.xScale = xScale
        if yScale is not None:
            self.yScale = yScale

    def show(self):
        if len(self.enabled) == 0:
            display(self.fig)
        else:
            display(self.vbox)

    def get_fig(self):
        return self.fig

    def connect(self, fig=None, vbox=None):

        if fig is not None:
            fig = self.fig
        if vbox is not None:
            vbox = self.vbox

    def save(self, filename):
        self.fig.save_png(filename)


def plot(data, index=None, ylabel=None,enable=None,debug=False,ptype=None,dims=None):
    return Cyplot(data, index=index, ylabel=ylabel,enable=enable,debug=debug,ptype=ptype,dims = dims)
