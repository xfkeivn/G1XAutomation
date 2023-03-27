import logging
import wx
import threading
logger = logging.getLogger('GX1')


class WxTextCtrlHandler(logging.Handler):
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl


    def emit(self, record):
        s = self.format(record) + '\n'
        wx.CallAfter(self.ctrl.logging, s)


class Console(wx.TextCtrl):
    def __init__(self, parent):
        wx.TextCtrl.__init__(self, parent, id=wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.NO_BORDER)
        handler = WxTextCtrlHandler(self)
        logger.addHandler(handler)
        formatter = "%(asctime)s %(levelname)s %(message)s"
        handler.setFormatter(logging.Formatter(formatter))
        self.pending_to_show = []
        self.timer = wx.Timer(self)
        self.timer.Start(50)
        self.Bind(wx.EVT_TIMER,self.on_timer)
        self.lock = threading.Lock()
        self.lines = 0
        self.lines_start_end = []
        self.total_size = 0
        self.MAX_LINES = 100
        self.removed_idx = 0

    def clear(self):
        wx.TextCtrl.Clear(self)
        self.lines = 0
        self.lines_start_end = []
        self.total_size = 0

    def __del__(self):
        self.timer.Stop()

    def on_timer(self,evt):
        self.lock.acquire()
        if len(self.pending_to_show) > 0:
            msg = "".join(self.pending_to_show)
            if self.lines > self.MAX_LINES:
                lines_to_remove = self.lines - self.MAX_LINES
                end_idx = self.lines_start_end[lines_to_remove-1][1]
                self.Remove(0, end_idx - self.removed_idx)
                self.lines_start_end = self.lines_start_end[lines_to_remove:]
                self.lines = self.MAX_LINES
                self.removed_idx = end_idx
            self.pending_to_show.clear()
            self.AppendText(msg)

        self.lock.release()

    def logging(self,text):
        self.lock.acquire()
        self.pending_to_show.append(text)
        text_len = len(text)
        self.lines_start_end.append((self.total_size,self.total_size+text_len))
        self.total_size += text_len
        self.lines += 1
        self.lock.release()





