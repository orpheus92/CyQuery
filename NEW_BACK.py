import pandas as pd
import numpy as np

from bqplot import DateScale, LinearScale, OrdinalScale, Axis, Lines, Scatter, Bars, Hist, Figure
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
    def __init__(self, data, index=None, ylabel=None):

        self.set_data(data, index, ylabel)

        self.interaction_map()

        self.enabled = []

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
                    # for e in self.enabled:
                    e = self.enabled[i]
                    if self.interactions[e]['order'] > self.interactions[inter]['order']:
                        self.enabled.insert(i, inter)
                        break
                    i = i + 1
                if inter not in self.enabled:  # i==0 or i ==n:
                    self.enabled.append(inter)

        if change:
            self.updatebuttons(self.enabled)

    def updatebuttons(self, enabled):

        ops = self.get_input(enabled)

        # Keep try of current selected part

        oldind = -1

        y = getattr(self, "selection_interacts", None)

        if y is not None:
            oldind = self.selection_interacts.index
            if self.old_enabled[oldind] in self.enabled:
                ind = self.enabled.index(self.old_enabled[oldind])
            else:
                print("Before manually change IDX\n")
                print(self.fig.interaction)
                # self.fig.interaction = None
                with self.fig.hold_trait_notifications():
                    # hold_trait_notifications()
                    self.selection_interacts.index = self.old_enabled.index(self.enabled[0])
                print("After index change due removal")
                print(self.old_enabled.index(self.enabled[0]))
                # unlink((self.selection_interacts, 'value'), (self.fig, 'interaction'))
                # self.link[0].observe(self._update_target, names=self.source[1])
                # self.link[0].observe(self._update_source, names=self.target[1])
                print("REMOVE CURRENT INTER")
                # self.link.source[0].unobserve(self.link._update_target, names=self.link.source[1])
                # self.link.target[0].unobserve(self.link._update_source, names=self.link.target[1])
                self.link.unlink()

                # self.fig.interaction = None
                print("After Remove", type(self.fig.interaction), self.fig.interaction)
                ind = 0
        else:
            oldind = -1

        self.selection_interacts = ToggleButtons(**ops)
        # print(self.selection_interacts.index)
        # self.selection_interacts.value gives the current interaction (the one that is clicked)

        print("Defaut selection interacts :")
        print(self.selection_interacts.value)

        if oldind != -1:
            self.selection_interacts.index = ind
            # self.fig.interaction = self.selection_interacts.value

        print("Before link happend\n", self.fig.interaction)
        print("\n ========== \n", self.selection_interacts.value)

        self.fig.interaction = None

        # with dpdown.hold_trait_notifications():

        self.link = link((self.selection_interacts, 'value'), (self.fig, 'interaction'))

        box_layout = Layout(display='flex',
                            flex_flow='column',
                            align_items='stretch')  # ,
        # border='solid',
        # width='50%')

        self.vbox = VBox([self.selection_interacts, self.fig, self.deb, self.deb2], layout=box_layout)

    def get_input(self, enabled):
        ops = {}
        ops['options'] = OrderedDict()
        ops['tooltips'] = []
        ops['icons'] = []
        ops['style'] = {'button_width': '40px'}  # ,#,'description_width':'0px'},
        ops['description'] = 'interaction'  # ,
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
                func = self.interactions[interaction]['selector']  # ['selector']
                func.observe(cb, names=[self.interactions[interaction]['watch']])

            else:
                print("Can't turn on {}".format(interaction))

        # elif isinstance(interaction,list):
        #     num = len(interaction)
        #     for i in range(num):
        #         if cb is not None:
        #             self.on(interaction[i], cb[i])
        #         else:
        #             self.on(interaction[i], None)
        #
        # elif isinstance(interaction, dict):
        #     for k in interaction:
        #         self.on(k, interaction[k])
        #     # print('Each interaction has a cb')
        #
        # if interaction == 'brush':
        #
        #     def _cb(change):
        #
        #         if isinstance(change.new, np.ndarray):
        #             # Always x range for now
        #
        #             xr = change.new
        #             yr = [None, None]
        #             box = [[xr[0], yr[0]], [xr[1], yr[1]]]
        #             self.deb.value = "The brushed area is {} ".format(str(box))  # , self.xlabel, str(yr),self.ylabel)
        #             # self.deb2.value = "The selected indices are {} ".format(
        #             #     str(self.fig.marks[0].selected))  # , self.xlabel, str(yr),self.ylabel)
        #             self.deb2.value = str(change)
        #
        #             cb(box)
        #             # brushing, multiple
        #             # if not change.new:
        #         else:
        #
        #             box = self.interactions['brush']['selector'].selected # self.enabled['brush'].selected
        #             self.deb.value = "The brushed area is {} ".format(str(box))  # , self.xlabel, str(yr),self.ylabel)
        #             self.deb2.value = "The selected indices are {} ".format(
        #                 str(self.fig.marks[0].selected))  # , self.xlabel, str(yr),self.ylabel)
        #
        #             cb(box)
        #

    def set_data(self, data, index, ylabel, add=False):

        # add decide whether draw figure on top

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

    def add_data(self, data):
        self.set_data(data, add=True)

    def create_fig(self, ts):

        ts.sort_index(inplace=True)

        df = ts.reset_index()  # time = ts.Time

        self.xd = df[self.xlabel]
        self.yd = df[self.cols].T

        # line_style
        # {‘solid’, ‘dashed’, ‘dotted’, ‘dash_dotted’} – Line style.

        line = Lines(x=self.xd, y=self.yd, scales={'x': self.xScale, 'y': self.yScale}, labels=self.legends,
                     display_legend=True, line_style='solid', marker='circle', selected_style={'opacity': '1'},
                     unselected_style={'opacity': '0.2'})  # enable_hover=True)  # axes_options=axes_options)

        x_axis = Axis(scale=self.xScale, label=self.xlabel, grid_lines='none')
        y_axis = Axis(scale=self.yScale, label=self.ylabel, orientation='vertical', grid_lines='none')

        margin = dict(top=0, bottom=30, left=50, right=50)

        self.fig = Figure(marks=[line], axes=[x_axis, y_axis], legend_location='top-right',
                          fig_margin=margin)  # {'top':50,'left':60})

        self.deb = HTML()
        self.deb2 = HTML()

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

        # def cb1(change):
        #
        # def cb2(change):
        #
        # def cb3(change):

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

        # self.deb.value = ''  # '[]'

        # deb = HTML(value='[]')
        # Reset added jere ????
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

    def internal_cb(self):
        print("????????????")

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

    def save(self, filename):
        self.fig.save_png(filename)


def plot(data, index=None, ylabel=None):
    return Cyplot(data, index, ylabel)
