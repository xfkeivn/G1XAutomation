'''
@author: Administrator
'''
from dvtfront_py.models.TreeModel import TreeModel, TREEMODEL_STATUS_NORMAL
from dvtfront_py.models import TagName
import dvtfront_py.ui.images
import wx
from lxml import etree
import pickle
from dvtfront_py.models.TreeModel import TreeAction
from dvtfront_py.models.CommonProperty import StringProperty
from dvtfront_py.runtime.runtimecore import format_widget_operation
from dvtfront_py.runtime.runtimecore import format_widget_callback
import inspect


class WidgetTreeItem(TreeModel):

    def __init__(self, parent, wx_widget, label=None, image=None):
        TreeModel.__init__(self, parent, TagName.TAG_NAME_WIDGET)
        self.wx_widget_class = wx_widget
        self.label = wx_widget.__name__
        if image == None:
            self.image = dvtfront_py.ui.images.widget
        from dvtfront_py.models.WidgetFactory import WidgetFactory
        WidgetFactory().register_widget(wx_widget)

    def getWidgetClassName(self):
        return self.wx_widget_class.__name__

    
EDIT_MOVE = 0
EDIT_RESIZE_Y = 1
EDIT_RESIZE_X = 2   



class WidgetCallback(TreeModel):

    def __init__(self, modelparent, eventtype,callbackname,helpstr=wx.EmptyString):
        TreeModel.__init__(self, modelparent, TagName.TAG_NAME_WIDGET_CALLBACK)
        self.image = dvtfront_py.ui.images.callback
        self.callbackname = callbackname
        self.eventtype = eventtype
        self.label = self.callbackname
        help = StringProperty('help',"help",helpstr,editable=False)
        help.setSavable(False)
        self.addProperties(help)       
    def getScriptSnippet(self):
        return format_widget_callback(self.getModelParent(),self.callbackname)
        

class WidgetOperation(TreeModel):

    def __init__(self, modelparent,operation):
        TreeModel.__init__(self, modelparent, TagName.TAG_NAME_WIDGET_OPERATION)
        self.image = dvtfront_py.ui.images.func
        self.operation = operation
        self.label = operation.__name__
        (args, varargs, keywords, defaults) = inspect.getargspec(operation)
        self.args = args[1:]
        operationdoc = wx.EmptyString
        if operation.__doc__:
            operationdoc = operation.__doc__
            operationdoc = operationdoc.strip()
            operationdoc = ' '.join(operationdoc.split("\n"))
        help = StringProperty('help',"help",operationdoc,editable=False)
        help.setSavable(False)
        self.addProperties(help)
    def getScriptSnippet(self):
        code = format_widget_operation(self.getModelParent(),self.operation)
        return code    


MENU_ID_COPY = wx.ID_HIGHEST +1

class WidgetOnPanel(TreeModel):
    def __init__(self, modelparent, image=None):
        TreeModel.__init__(self, modelparent, TagName.TAG_NAME_WIDGET)
        self.widget_type_name = self.__class__.__name__
        if image == None:self.image = dvtfront_py.ui.images.widget
        self.last_pos = None
        self.name = modelparent.getTempName(self.widget_type_name)
        self.label = self.name
        self.getModelParent().addChild(self)
        self.populate()
        self.tree_action_list.append(TreeAction("Remove", wx.ID_HIGHEST + 1000, self.RemoveSelf))
        self.addProperties(StringProperty('name', 'name', self.name))
        typeprop = StringProperty('type', 'type', self.widget_type_name, editable=False)
        typeprop.setSavable(False)
        self.addProperties(typeprop)
        self.selected = False
        self.edit_status = None
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST,self.onCaptureLost)
        self.defaultcousor = self.GetCursor()
    
    def updateProperty(self, wxprop):
        prop = TreeModel.updateProperty(self, wxprop)
        if prop.getName() == 'name':
            newname = wxprop.GetValue()
            self.name = newname
            self.setModelLabel(self.name)
        return prop
        
    def onCaptureLost(self,evt):
        #self.ReleaseMouse()
        self.last_pos = None
        self.edit_status = None
        self.SetCursor(self.defaultcousor)
        
    def getWidgetTypeName(self):
        return self.widget_type_name
                
    def __createWidgetObject(self):
        return self.widgetclass(self, -1)
        
    def BindEvent(self):
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.Bind(wx.EVT_MOTION, self.onMove)
        self.Bind(wx.EVT_CONTEXT_MENU,self.onContextMenu)
        self.Bind(wx.EVT_MENU,self.onCopy,id=MENU_ID_COPY)
    
    def onCopy(self,evt):
        self.getModelParent().addCopyPasteContext(self)
        
    def onContextMenu(self,evt):
        menu = wx.Menu()
        menu.Append(MENU_ID_COPY,"Copy")
        if len(self.getActions()) > 0:
            index = 0
            for action in self.getActions():
                item = wx.MenuItem(menu,action.eventid, action.name)
                menu.AppendItem(item)
                menu.Bind(wx.EVT_MENU,action.callable, id=item.GetId())
                index+=1
        self.PopupMenu(menu)
        
    def unBindEvent(self):
        self.Unbind(wx.EVT_LEFT_DOWN, handler=self.onLeftDown)
        self.Unbind(wx.EVT_LEFT_UP, handler=self.onLeftUp)
        self.Unbind(wx.EVT_MOTION, handler=self.onMove)
        self.Unbind(wx.EVT_CONTEXT_MENU,handler=self.onContextMenu)
        self.Unbind(wx.EVT_MENU,handler = self.onCopy)
        
    def onLeftDown(self, evt):
        self.CaptureMouse()
        self.last_pos = (evt.x , evt.y)
        self.onActivate()
        self.edit_status = self.__checkRegion(evt.x, evt.y)
        #evt.Skip()
        
    def onLeftUp(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
 
        self.last_pos = None
        self.edit_status = None
        self.SetCursor(self.defaultcousor)
        #evt.Skip()

    def __checkRegion(self, x, y):
        widgetsize = self.GetSize()
        
        xanchorsize = widgetsize.x*0.3
        yanchorsize = widgetsize.y*0.3
        move_region = wx.Rect(0, 0, widgetsize.x - xanchorsize, widgetsize.y - yanchorsize)
        move_x_region = wx.Rect(widgetsize.x - xanchorsize, 0, xanchorsize, widgetsize.y)
        move_y_region = wx.Rect(0, widgetsize.y - yanchorsize, widgetsize.x, yanchorsize)

        if move_x_region.Contains(x, y):
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))
            return EDIT_RESIZE_X
        if move_y_region.Contains(x, y):
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENS))
           
            return EDIT_RESIZE_Y
        if move_region.Contains(x, y):
            self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            return EDIT_MOVE

    def onMove(self, evt):
        if True:
            x= wx.GetMousePosition().x
            y= wx.GetMousePosition().y
            self.__checkRegion(evt.x, evt.y)
            if self.last_pos and self.edit_status == EDIT_MOVE:

                delta_x = x - self.last_pos[0]
                delta_y = y - self.last_pos[1]
                # self.SetPosition((orgin_x+delta_x,orgin_y+delta_y))
                mx,my = self.GetParent().ScreenToClient((delta_x, delta_y))
                if mx<5:
                    mx = 5
                if my<5:
                    my = 5
                self.Move((mx,my))
                self.__update_the_scrolled_window()
                self.GetParent().RefreshWidget(self)
                self.setDirty(True)
            elif self.last_pos and self.edit_status == EDIT_RESIZE_Y:
                delta_y = evt.y - self.last_pos[1]            
                orgin_w, orgin_h = self.GetSize()
                self.SetSize((orgin_w, orgin_h + delta_y))
                self.last_pos = (evt.x, evt.y)
                self.__update_the_scrolled_window()  
                self.GetParent().RefreshWidget(self)
                self.setDirty(True)
            elif self.last_pos and self.edit_status == EDIT_RESIZE_X:
                delta_x = evt.x - self.last_pos[0]            
                orgin_w, orgin_h = self.GetSize()
                self.SetSize((orgin_w + delta_x, orgin_h))
                self.last_pos = (evt.x, evt.y)
                self.__update_the_scrolled_window()  
                self.GetParent().RefreshWidget(self)
                self.setDirty(True)
        #evt.Skip()
            
    def __update_the_scrolled_window(self):
        scrolledwin = self.GetParent()
        scrolledwin.CalcuateSize()

    def from_xml(self, widget):
        TreeModel.from_xml(self, widget)
        self.name = widget.get('name')
        self.label = self.name
        pos = widget.get('pos')
        size = widget.get('size')
        if pos:
            self.SetPosition(pickle.loads(pos))
        if size:
            self.SetSize(pickle.loads(size))
    
    def to_xml(self):
        
        pos = self.GetPosition()
        pos = self.getModelParent().CalcUnscrolledPosition(pos) 
        size = self.GetSize()
        element = etree.Element(TagName.TAG_NAME_WIDGET, attrib={'name':self.name, 'widget_type_name':self.widget_type_name, 'pos':pickle.dumps(pos), 'size':pickle.dumps(size)})
        element.append(TreeModel.to_xml(self))
        return element

    def RemoveSelf(self, event):
        dlg = wx.MessageDialog(self.getProject_Tree(), 'Please Confirm to delete',
                               'Confirm to delete',
                               # wx.OK | wx.ICON_INFORMATION
                               wx.YES_NO | wx.ICON_INFORMATION
                               )
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            self.remove()
            self.GetParent().RemoveWidget(self)
        dlg.Destroy()
        

    def Select(self):
        self.selected = True


    def UnSelect(self):
        self.selected = False

    def onActivate(self):
        TreeModel.onActivate(self)
        parentmodel = self.getModelParent()
        parentmodel.SelectWidget(self)
        #self.getProject_Tree().GetParent().ShowPageInCentrePane(panel_label)          
        self.getProject_Tree().SelectItem(self.tree_item)
        
    def bind(self,callback):
        for child in self.getModelChildren():
            if isinstance(child,WidgetCallback):
                if child.callbackname == callback.callbackname:
                    self.Bind(child.eventtype,callback)
                    

    def unbind(self,callback):
        for child in self.getModelChildren():
            if isinstance(child,WidgetCallback):
                if child.callbackname == callback.callbackname:
                    self.Unbind(child.eventtype,handler=callback.callbackfun)
    
    def populate(self):
        pass
    def set_model_status(self,modelstatus):
        if modelstatus == TREEMODEL_STATUS_NORMAL:
            self.BindEvent()
            self.SetCursor(self.defaultcousor)
        else:
            self.unBindEvent()
            self.SetCursor(self.defaultcousor)     
        TreeModel.set_model_status(self, modelstatus)  
        
    def copy(self,parent):
        from . import WidgetFactory
        newwidget = WidgetFactory.WidgetFactory().createWidgetOnPanel(parent, self.__class__.__name__)              
        for prop in self.getProperties():
            if prop.getName()!="name":
                newprop = newwidget.getPropertyByName(prop.getName())
                if newprop!=None:
                    newprop.setStringValue(prop.getStringValue())
        newwidget.updateWidgetOutlooking()
        return newwidget
    
    def updateWidgetOutlooking(self):
        pass
    
          
        