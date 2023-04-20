"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: main.py
@time: 2023/3/26 10:58
@desc:
"""

import os
import wx
from sim_desk.ui import mainframe, images
cur_file_dir = os.path.dirname(__file__)
folder = os.path.dirname(cur_file_dir)


class App(wx.App):
    def OnInit(self):
        frame = mainframe.MainFrame(None)
        frame.Maximize()
        self.SetTopWindow(frame)
        frame.Show()
        wx.UpdateUIEvent.SetUpdateInterval(1000)
        return True


app = App(0)
app.MainLoop()





