from sim_desk.ui import images
import  pickle
from sim_desk.models.Widget import WidgetTreeItem
from sim_desk.models.widgets.MsgMonitor import MessageMonitorPanel
from sim_desk.models.widgets.Graph import GraphPanel
from sim_desk.models.widgets.wxwidgets import *
#from wx import *
import wx

class WidgetsTreeCtrl( wx.TreeCtrl ):
    def __init__(self,parent,id, pos, size, style):
        wx.TreeCtrl.__init__(self, parent, id,pos, size,style)
        
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = il.Add(images.folder_collapse.GetBitmap())
        self.fldropenidx = il.Add(images.folder_expand.GetBitmap())
        self.AssignImageList(il)
        self.il = il
        self.item_model={}
        self.root = self.AddRoot("Widgets")
        self.SetItemImage(self.root,self.fldridx,wx.TreeItemIcon_Normal)
        self.SetItemImage(self.root,self.fldropenidx,wx.TreeItemIcon_Expanded)
        
        self.addToTree(WidgetTreeItem(self,TextCtrl))
        self.addToTree(WidgetTreeItem(self,Button))
        self.addToTree(WidgetTreeItem(self,StaticText))
        self.addToTree(WidgetTreeItem(self,StaticBitmap))
        self.addToTree(WidgetTreeItem(self,Slider))
        self.addToTree(WidgetTreeItem(self,BitmapToggleButton))
        self.addToTree(WidgetTreeItem(self,LEDTextCtrl))
        self.addToTree(WidgetTreeItem(self,MessagePanel))
        self.addToTree(WidgetTreeItem(self,ListBox))
        self.addToTree(WidgetTreeItem(self,MessageMonitorPanel))
        self.addToTree(WidgetTreeItem(self,GraphPanel))
        
        self.Bind(wx.EVT_TREE_BEGIN_DRAG,self.OnDrag)
        self.Bind(wx.EVT_LEFT_DOWN,self.onLeftDown)
        
        
    def onLeftDown(self,evt):
        item,where  = self.HitTest((evt.x,evt.y))
        
        if item!=None and item.IsOk():
            self.SelectItem(item)
        evt.Skip()
        
    def OnDrag(self,evt):
        item = self.GetSelection()
        if item!=None and item!=self.root:
            widgetclassname = self.GetPyData(item).getWidgetClassName()
            namestringdata = pickle.dumps(widgetclassname, 1)
            data = wx.CustomDataObject("Widget")
            data.SetData(namestringdata)
            dropSource = wx.DropSource(self)
            dropSource.SetData(data)
            dropSource.DoDragDrop(wx.Drag_AllowMove)

    def addToTree(self,widget):
        
        newitem = self.AppendItem(self.root, widget.getLabel())
        if widget.getImage()!=None:
            index = self.il.Add(widget.getImage().GetBitmap())
            self.SetItemImage(newitem, index, wx.TreeItemIcon_Normal)
            pass
        self.SetItemData(newitem,widget)
        self.item_model[widget] = newitem
        
        
        
        
        
        

