"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: progressdlg.py
@time: 2023/3/26 10:58
@desc:
"""

import wx


class ProgressObserver(object):
    def __init__(self, frame, title, message):
        self._progressbar = wx.ProgressDialog(
            title,
            message,
            maximum=100,
            parent=frame,
            style=0 | wx.PD_APP_MODAL | wx.PD_CAN_ABORT,
        )

    def update(self, value, new_message):
        self._progressbar.Update(value, new_message)

    def notify(self):
        self._progressbar.Pulse()

    def finish(self):
        self.update(100, "")
        self.notify()
        self._progressbar.Destroy()

    def error(self, msg):
        self.finish()
