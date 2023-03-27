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
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        self.cb = wx.StaticBitmap(self, bitmap=sim_desk.ui.images.edit.GetBitmap())
        # set the initial position of the checkbox
        self.Reposition()

        
    def SetText1(self,text):
        self.SetStatusText(text,0)

    def SetText2(self,text):
        self.SetStatusText(text,2)
    
    def SetStatus(self,status):
        if status == TREEMODEL_STATUS_NORMAL:
            self.cb.SetBitmap(sim_desk.ui.images.edit.GetBitmap())
        else:
            self.cb.SetBitmap(sim_desk.ui.images.testrun.GetBitmap())
        self.Refresh()
            
        

    def OnSize(self, evt):
        evt.Skip()
        self.Reposition()  # for normal size events
        self.sizeChanged = True


    def OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()


    # reposition the checkbox
    def Reposition(self):
        rect = self.GetFieldRect(1)
        rect.x += 1
        rect.y += 1
        self.cb.SetRect(rect)
        self.sizeChanged = False