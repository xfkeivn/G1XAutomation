"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: statusbar.py
@time: 2023/3/26 10:58
@desc:
"""


import wx

import sim_desk.ui.images
from sim_desk.models.TreeModel import TREEMODEL_STATUS_NORMAL


class StatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(3)
        # Sets the three fields to be relative widths to each other.
        self.SetStatusWidths([-2, -1, -2])
        self.sizeChanged = False
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_IDLE, self.on_idle)

        self.cb = wx.StaticBitmap(
            self, bitmap=sim_desk.ui.images.edit.GetBitmap()
        )
        # set the initial position of the checkbox
        self.reposition()

    def set_text1(self, text):
        self.SetStatusText(text, 0)

    def set_text2(self, text):
        self.SetStatusText(text, 2)

    def set_status(self, status):
        if status == TREEMODEL_STATUS_NORMAL:
            self.cb.SetBitmap(sim_desk.ui.images.edit.GetBitmap())
        else:
            self.cb.SetBitmap(sim_desk.ui.images.testrun.GetBitmap())
        self.Refresh()

    def on_size(self, evt):
        evt.Skip()
        self.reposition()  # for normal size events
        self.sizeChanged = True

    def on_idle(self, evt):
        if self.sizeChanged:
            self.reposition()

    def reposition(self):
        rect = self.GetFieldRect(1)
        rect.x += 1
        rect.y += 1
        self.cb.SetRect(rect)
        self.sizeChanged = False
