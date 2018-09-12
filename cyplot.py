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
    def __init__(self, data, index=None, ylabel=None):

        self.set_data(data, index, ylabel)

        self.interaction_map()

        self.active = {}

    def enable(self, interactions):
        if isinstance(interactions, str):
            interactions = [interactions]

        for inter in interactions:
            if inter in self.interactions:
                self.active[inter] = self.interactions[inter]

        self.selection_interacts = ToggleButtons(options=self.active)

        link((self.selection_interacts, 'value'), (self.fig, 'interaction'))

        self.vbox = VBox([self.deb, self.fig, self.selection_interacts], align_self='stretch')

    def disable(self, interactions):
        # Will be implemented later
        print(interactions)

    def on(self, interaction, cb):

        if interaction == 'brush':

            def _cb(change):

                if isinstance(change.new, np.ndarray):
                    # Always x range for now

                    xr = change.new
                    yr = [None, None]
                    box = [[xr[0], yr[0]], [xr[1], yr[1]]]
                    self.deb.value = "The brushed area is {} ".format(str(box))  # , self.xlabel, str(yr),self.ylabel)
                    cb(box)
                    # brushing, multiple
                    # if not change.new:


                else:

                    box = self.active['Brush'].selected
                    self.deb.value = "The brushed area is {} ".format(str(box))  # , self.xlabel, str(yr),self.ylabel)
                    cb(box)

            if 'Multiple_Brush' in self.active:
                func = self.active['Multiple_Brush']
                func.observe(_cb, names=['selected'])

            if 'BrushX' in self.active:
                func = self.active['BrushX']
                func.observe(_cb, names=['selected'])

            if 'Fast_Brush' in self.active:
                func = self.active['Fast_Brush']
                func.observe(_cb, names=['selected'])

            if 'Brush' in self.active:
                func = self.active['Brush']
                func.observe(_cb, names=['brushing'])

        elif interaction == 'panzoom':
            def _cb(change):
                self.deb.value = "The Current Scale is {} ".format(str(change.new))
                cb(change.new)

            if "Pan_Zoom" in self.active:
                func = self.active['Pan_Zoom']
                func.observe(_cb, names=['scales'])


        elif interaction == 'selector':
            def _cb(change):
                self.deb.value = "The selected index is {} ".format(change.new)
                cb(change.new)

            if "Index_Selector" in self.active:
                func = self.active['Index_Selector']
                func.observe(_cb, names=['selected'])
        else:
            print('More interactions will be added')

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

        self.legends = [' '.join(legend) for legend in self.cols]

        if ylabel is not None:
            self.ylabel = ylabel

        elif len(self.data.columns.levels[0]) == 1:
            self.legends = [' '.join(legend[1::]) for legend in self.cols]

        else:
            self.ylabel = ''

        self.xScale = LinearScale()
        self.yScale = LinearScale()

        self.create_fig(self.data)

    def create_fig(self, ts):

        ts.sort_index(inplace=True)

        df = ts.reset_index()  # time = ts.Time

        self.xd = df[self.xlabel]
        self.yd = df[self.cols].T

        line = Lines(x=self.xd, y=self.yd, scales={'x': self.xScale, 'y': self.yScale}, labels=self.legends,
                     display_legend=True)  # axes_options=axes_options)

        x_axis = Axis(scale=self.xScale, label=self.xlabel, grid_lines='none')
        y_axis = Axis(scale=self.yScale, label=self.ylabel, orientation='vertical', grid_lines='none')

        self.fig = Figure(marks=[line], axes=[x_axis, y_axis])

        self.deb = HTML()

    def _ipython_display_(self):

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

        self.interactions['Multiple_Brush'] = multi_sel
        self.interactions['BrushX'] = br_intsel
        self.interactions['Fast_Brush'] = int_sel
        self.interactions['Brush'] = br_sel
        self.interactions['Index_Selector'] = index_sel
        self.interactions['Pan_Zoom'] = pz

        # self.deb.value = ''  # '[]'

        # deb = HTML(value='[]')

        # def test_callback(change):
        #     self.deb.value = "The selected range is {} on {} with {}".format(change.new, self.xlabel,
        #                                                                      br_intsel.selke)  # str(change.new)
        #
        # def brush_callback(change):
        #     # deb.value = str(br_sel.selected)
        #     xr = [br_sel.selected[0][0], br_sel.selected[1][0]]
        #     yr = [br_sel.selected[0][1], br_sel.selected[1][1]]
        #     self.deb.value = "The brushed area is {} on {},  {} on {}".format(str(xr), self.xlabel, str(yr),
        #                                                                       self.ylabel)

        # if cb is not None:
        #     def mycb(change):
        #         self.deb.value = str(cb(change.new))  # cb(change.new)
        #
        #     test_callback = mycb
        #     brush_callback = mycb

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

        # multi_sel.observe(test_callback, names=['brushing'])
        # br_intsel.observe(test_callback, names=['brushing'])
        # index_sel.observe(test_callback, names=['brushing'])
        # int_sel.observe(test_callback, names=['brushing'])
        #
        # br_sel.observe(brush_callback, names=['brushing'])  # 'brushing'])
        # selctedX, selectedY

        # odict = OrderedDict([('FastInterval', int_sel), ('Index', index_sel),
        #                      ('BrushX', br_intsel), ('MultiBrush', multi_sel), ('Brush', br_sel),
        #                      ('PanZoom', pz), ('None', None)])
        #
        # self.interaction_dict = odict

        # return odict

    def setScale(self, xScale=None, yScale=None):
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


def plot(data, index=None, ylabel=None):
    return Cyplot(data, index, ylabel)
