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





