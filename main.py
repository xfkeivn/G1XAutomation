"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: main.py
@time: 2023/3/26 10:58
@desc:
"""

import wx

from sim_desk.ui import mainframe


class App(wx.App):
    def OnInit(self):
        frame = mainframe.MainFrame(None)
        frame.Maximize()
        self.SetTopWindow(frame)
        frame.Show()
        wx.UpdateUIEvent.SetUpdateInterval(1000)
        return True


app = App(False)
app.MainLoop()
