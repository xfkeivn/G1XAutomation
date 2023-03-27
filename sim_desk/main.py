'''
Created on 2018-3-20

@author: Administrator
'''
import os
curfile_dir = os.path.dirname(__file__)
folder = os.path.dirname(curfile_dir)
import wx
from sim_desk.ui import mainframe, images


class App(wx.App):
    def OnInit(self):
        #bmp = images.splashscreen.GetBitmap()
        #wx.SplashScreen(bmp,  wx.SPLASH_CENTER_ON_SCREEN | wx.SPLASH_TIMEOUT,  1000,  None)  
        #wx.Yield()  
        frame = mainframe.MainFrame(None)
        frame.Maximize()
        self.SetTopWindow(frame)
        frame.Show()
        wx.UpdateUIEvent.SetUpdateInterval(1000)  # Overhead of updating menus was too much.  Change to update every N milliseconds.
        return True
app = App(0)
app.MainLoop()





