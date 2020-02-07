#!/usr/bin/python3
#
#  Copyright (C) 2019-2020 Angus King
#
#  zoompan.py - This file is used by SIREN.
#
#  This is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of
#  the License, or (at your option) any later version.
#
#  SIREN is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General
#  Public License along with SIREN.  If not, see
#  <http://www.gnu.org/licenses/>.
#
# Based on: https://gist.github.com/tacaswell/3144287
# and ttps://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
from mpl_toolkits.mplot3d import proj3d
#from matplotlib.lines import Line2D
#from matplotlib.collections import PathCollection
from mpl_toolkits.mplot3d.art3d import Path3DCollection


class ZoomPanX():
    def __init__(self):
        self.base_xlim = None
        self.base_ylim = None
        self.base_zlim = None
        self.xlabel = None
        self.axis = 'x'
        self.d3 = False
        self.datapoint = None
        self.tbar = None
        self.cur_xlim = None
        self.press = None
        self.month = None
        self.week = None
        self.keys = ''


    def zoom_pan(self, ax, base_scale=2., annotate=False):
        def zoom(event):
            if event.inaxes != ax:
                return
            if self.base_xlim is None:
                self.base_xlim = ax.get_xlim()
                self.base_ylim = ax.get_ylim()
                try:
                    self.base_zlim = ax.get_zlim()
                    self.d3 = True
                except:
                    self.d3 = False
            # get the current x and y limits
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            if self.d3:
                cur_zlim = ax.get_zlim()
            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location
            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print('(56)', event.button)
            # set new limits
            if self.d3:
                z_left = ydata - cur_zlim[0]
                z_right = cur_zlim[1] - ydata
            if self.axis == 'x':
                ax.set_xlim([xdata - (xdata - cur_xlim[0]) * scale_factor,
                            xdata + (cur_xlim[1] - xdata) * scale_factor])
            elif self.axis == 'y':
                ax.set_ylim([ydata - (ydata - cur_ylim[0]) * scale_factor,
                            ydata + (cur_ylim[1] - ydata) * scale_factor])
            elif self.axis == 'z':
                ax.set_zlim([ydata - (ydata - cur_zlim[0]) * scale_factor,
                            ydata + (cur_zlim[1] - ydata) * scale_factor])
            ax.figure.canvas.draw() # force re-draw

        def onPress(event):
            if self.base_xlim is None:
                self.base_xlim = ax.get_xlim()
                self.base_ylim = ax.get_ylim()
                try:
                    self.base_zlim = ax.get_zlim()
                    self.d3 = True
                except:
                    self.d3 = False
            if self.tbar._active is not None:
                return
            if event.button == 3: # reset?
                self.month = None
                self.week = None
                if self.base_xlim is not None:
                    ax.set_xlim(self.base_xlim)
                    ax.figure.canvas.draw()
                    return
            if event.inaxes != ax:
                return
            if self.axis == 'x':
                self.cur_xlim = ax.get_xlim()
                self.press = event.xdata
            elif self.axis == 'y':
                self.cur_ylim = ax.get_ylim()
                self.press = event.ydata
            elif self.axis == 'z':
                self.cur_zlim = ax.get_zlim()
                self.press = event.ydata

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.base_xlim is None:
                self.base_xlim = ax.get_xlim()
                self.base_ylim = ax.get_ylim()
                try:
                    self.base_zlim = ax.get_zlim()
                    self.d3 = True
                except:
                    self.d3 = False
            if self.press is None:
                return
            if event.inaxes != ax:
                return
            if self.axis == 'x':
                dx = event.xdata - self.press
                self.cur_xlim -= dx
                ax.set_xlim(self.cur_xlim)
            elif self.axis == 'y':
                dy = event.ydata - self.press
                self.cur_ylim -= dy
                ax.set_ylim(self.cur_ylim)
            elif self.axis == 'z':
                dz = event.ydata - self.press
                self.cur_zlim -= dz
                ax.set_zlim(self.cur_zlim)
            ax.figure.canvas.draw()

        def onKey(event):
            if event.key.lower() == 'r': # reset
                self.keys = ''
                self.month = None
                self.week = None
                if self.base_xlim is not None:
                    ax.set_xlim(self.base_xlim)
                    ax.set_ylim(self.base_ylim)
                    if self.d3:
                        if hasattr(ax, 'label'):
                            try:
                                ax.label.remove()
                            except:
                                pass
                            self.datapoint = None
                        ax.set_zlim(self.base_zlim)
                    ax.figure.canvas.draw()
                    return
            if event.key == 'pageup':
                if self.axis != 'x':
                    return
                if self.week is not None:
                    self.week -= 1
                    if self.month is None:
                        if self.week < 0:
                            self.week = 52
                        strt = self.week * 168 # 24 * 7 hours per week
                    else:
                        if self.week < 0:
                            if self.month == 1 and self.mth_xlim[2] == 1416:
                                self.week = 3
                            else:
                                self.week = 4
                        strt = self.mth_xlim[self.month] + self.week * 168
                    ax.set_xlim([strt, strt + 168])
                else:
                    if self.month is None or self.month == 0:
                        self.month = 11
                    else:
                        self.month -= 1
                    ax.set_xlim([self.mth_xlim[self.month], self.mth_xlim[self.month + 1]])
                ax.figure.canvas.draw()
            elif event.key == 'pagedown':
                if self.axis != 'x':
                    return
                if self.week is not None:
                    self.week += 1
                    if self.month is None:
                        if self.week >= 52:
                            self.week = 0
                        strt = self.week * 168 # 24 * 7 hours per week
                    else:
                        if self.week >= 5 or \
                          (self.month == 1 and self.week >= 4 and self.mth_xlim[2] == 1416):
                            self.week = 0
                        strt = self.mth_xlim[self.month] + self.week * 168
                    ax.set_xlim([strt, strt + 168])
                else:
                    if self.month is None:
                        self.month = 0
                    else:
                        if self.month >= 11:
                            self.month = 0
                        else:
                            self.month += 1
                    ax.set_xlim([self.mth_xlim[self.month], self.mth_xlim[self.month + 1]])
                ax.figure.canvas.draw()
            elif event.key.lower() == 'l':
                ax.legend().set_draggable(True)
                ax.figure.canvas.draw()
            elif event.key.lower() == 'm':
                if self.axis != 'x':
                    return
                self.keys = 'm'
                self.week = None
                if self.month is None:
                    self.month = 0
                elif self.month >= 11:
                    self.month = 0
                else:
                    self.month += 1
                ax.set_xlim([self.mth_xlim[self.month], self.mth_xlim[self.month + 1]])
                ax.figure.canvas.draw()
            elif event.key.lower() == 'w':
                if self.axis != 'x':
                    return
                self.keys = ''
                if self.week is None:
                    self.week = 0
                else:
                    self.week += 1
                if self.month is None:
                    if self.week >= 52:
                        self.week = 0
                    strt = self.week * 168 # 24 * 7 hours per week
                else:
                    if self.week >= 5 or \
                      (self.month == 1 and self.week >= 4 and self.mth_xlim[2] == 1416):
                        self.week = 0
                    strt = self.mth_xlim[self.month] + self.week * 168
                ax.set_xlim([strt, strt + 168])
                ax.figure.canvas.draw()
            elif event.key >= '0' and event.key <= '9':
                if self.axis != 'x':
                    return
                if self.keys[-2:] == 'm1':
                    self.keys = ''
                    if event.key < '3':
                        self.month = 10 + int(event.key) - 1
                    else:
                        return
                elif self.keys[-1:] == 'm':
                    if event.key == '0':
                        self.month = 0
                    else:
                        self.month = int(event.key) - 1
                    self.keys += event.key
                ax.set_xlim([self.mth_xlim[self.month], self.mth_xlim[self.month + 1]])
                ax.figure.canvas.draw()
            elif event.key.lower() == 'x':
                if self.axis != 'x':
                    self.press = None
                self.axis = 'x'
            elif event.key.lower() == 'y':
                if self.axis != 'y':
                    self.press = None
                self.axis = 'y'
            elif event.key.lower() == 'z' and self.d3:
                if self.axis != 'z':
                    self.press = None
                self.axis = 'z'

        def onPick(event):
            if not isinstance(event.artist, Path3DCollection): # just 3D picking for the moment
                return
            self.datapoint = None
            if len(event.ind) > 0:
                self.datapoint = []
                if self.d3:
                    for n in event.ind:
                        self.datapoint.append([n, event.artist._offsets3d[0][n],
                            event.artist._offsets3d[1][n], event.artist._offsets3d[2][n]])
                    msg = '{:d}: x: {:.2f} y: {:.2f} z: {:.2f}'.format(self.datapoint[0][0],
                          self.datapoint[0][1], self.datapoint[0][2], self.datapoint[0][3])
                    # If we have previously displayed another label, remove it first
                    if hasattr(ax, 'label'):
                        try:
                            ax.label.remove()
                        except:
                            pass
                    x2, y2, _ = proj3d.proj_transform(self.datapoint[0][1], self.datapoint[0][2],
                                self.datapoint[0][3], ax.get_proj())
                    ax.label = ax.annotate(msg, xy = (x2, y2), xytext = (0, 20),
                                textcoords = 'offset points', ha = 'right', va = 'bottom',
                                bbox = dict(boxstyle = 'round,pad=0.5', alpha = 0.5),
                                arrowprops = dict(arrowstyle = '->',
                                                  connectionstyle = 'arc3,rad=0'))
                ax.figure.canvas.draw()


        the_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        self.xlabel = ax.get_xlabel()
        self.title = ax.get_title()
        self.base_xlim = ax.get_xlim() # remember x base
        self.base_ylim = ax.get_ylim() # remember y base
        try:
            self.base_zlim = ax.get_zlim() # remember z base for 3D
            self.d3 = True
        except:
            self.d3 = False
        if self.base_xlim[1] == 8784: # leap year
            the_days[1] = 29
        x = 0
        self.mth_xlim = [x]
        for days in the_days:
            x += days * 24
            self.mth_xlim.append(x)
        fig = ax.get_figure() # get the figure of interest
        self.tbar = fig.canvas.toolbar # get toolbar
        # attach the call back
        # 'axis_enter_event'
        # 'axis_leave_event'
        fig.canvas.mpl_connect('button_press_event', onPress)
        fig.canvas.mpl_connect('button_release_event', onRelease)
        # 'draw_event'
        # 'figure_enter_event'
        # 'figure_leave_event'
        fig.canvas.mpl_connect('key_press_event', onKey)
        # 'key_release_event'
        fig.canvas.mpl_connect('motion_notify_event', onMotion)
        fig.canvas.mpl_connect('pick_event', onPick)
        # 'resize_event'
        fig.canvas.mpl_connect('scroll_event', zoom)
        #return the function
        return zoom
