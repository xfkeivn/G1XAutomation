import wx
from sim_desk.ui import images
import string
TREE_POP_MENU_ID = wx.ID_HIGHEST + 10100
from sim_desk.models.TreeModel import EVT_ADD_TO_TREE_EVENT
from sim_desk.models.TreeModel import EVT_REMOVE_FROM_TREE_EVENT
from sim_desk.models.TreeModel import EVT_UPDATE_TREE_ITEM_IMAGE
from sim_desk.models.TreeModel import EVT_UPDATE_TREE_ITEM_LABEL
class ProjectTreeCtrl( wx.TreeCtrl ):
    def __init__(self,parent,id, pos, size, style):
        wx.TreeCtrl.__init__(self, parent, id,pos, size,style)
        
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = il.Add(images.folder_collapse.GetBitmap())
        self.fldropenidx = il.Add(images.folder_expand.GetBitmap())
        self.prjidx = il.Add(images.nested_projects.GetBitmap())
        self.AssignImageList(il)
        self.il = il
        self.root = None

        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded, self)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed, self)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnBeginEdit, self)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnEndEdit, self)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        self.Bind(wx.EVT_LEFT_DOWN,self.onLeftDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_SIZE, self.OnSize)  
        self.Bind(EVT_ADD_TO_TREE_EVENT, self.addToTree)  
        self.Bind(EVT_REMOVE_FROM_TREE_EVENT, self.removeFromTree)
        self.Bind(EVT_UPDATE_TREE_ITEM_IMAGE,self.updateTreeItemImage)
        self.Bind(EVT_UPDATE_TREE_ITEM_LABEL,self.updateTreeItemLabel)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG,self.OnDrag)
        self.item_model={}
    
    def updateTreeItemImage(self,evt):
        image = evt.image
        model = evt.model
        item = self.item_model.get(model)
        index = self.il.Add(image.GetBitmap())
        self.SetItemImage(item,index,wx.TreeItemIcon_Normal)
        
    def updateTreeItemLabel(self,evt):
        label = evt.label
        model = evt.model
        item = self.item_model.get(model)
        self.SetItemText(item,label)
        
    def addToTree(self,event):
        
        parentmodel = event.parent_model
        childmodel  = event.model_to_add        
        parentitem = self.item_model.get(parentmodel)
        if parentitem is None:
            self.GetParent().console.error("The tree item does not exists, unlikely to happen")
        newitem = self.AppendItem(parentitem, childmodel.getLabel())
        
        if childmodel.getImage() is not None:
            index = self.il.Add(childmodel.getImage().GetBitmap())
            self.SetItemImage(newitem, index, wx.TreeItemIcon_Normal)
            pass
        self.SetItemData (newitem,childmodel)
        self.item_model[childmodel] = newitem
        childmodel.setTreeItem(newitem)
    
    def removeFromTree(self,event):
        model = event.model_to_remove
        #item = self.getItemByData(model)
        item = self.item_model[model]
        self.Delete(item)
        del self.item_model[model]
    
    
        

    def assignProject(self,projectmodel):
        self.DeleteAllItems()
        self.item_model.clear()
        self.root = self.AddRoot("project",self.prjidx)
        self.SetItemText(self.root,projectmodel.getLabel())
        self.SetItemData (self.root, projectmodel)
        projectmodel.project_tree = self
        self.item_model[projectmodel] = self.root
        
        
    
    def getItemByData(self,pydata,parentitem=None):
        if parentitem == None:
            parentitem = self.root
            if self.GetPyData(self.root) == pydata:
                return self.root
        item,cookie = self.GetFirstChild(parentitem)
        
        while item.IsOk():
            if self.GetPyData(item) == pydata:
                return item
            if self.GetChildrenCount(item)>0:
                citem = self.getItemByData(pydata,item)
                if citem !=None:
                    return citem
            item,cookie = self.GetNextChild(item,cookie)    

                

    def OnRightDown(self, event):
        pt = event.GetPosition();
        item, flags = self.HitTest(pt)
        if item:
            self.SelectItem(item)


    def onLeftDown(self, event):
        pt = event.GetPosition();
        item, flags = self.HitTest(pt)
        if item:
            self.SelectItem(item)
        event.Skip()


    def OnRightUp(self,event):
        pt = event.GetPosition();
        item, flags = self.HitTest(pt)
        if item:    
            model = self.GetItemData(item)
            self.ShowPopupmenu(model)

    def ShowPopupmenu(self,model):
        if len(model.getActions()) > 0:
            popup = wx.Menu()
            index = 0
            for action in model.getActions():
                item = wx.MenuItem(popup,TREE_POP_MENU_ID+index, action.name,)
                popup.Append(item)
                popup.Bind(wx.EVT_MENU,action.callable, id=item.GetId())
                index+=1
            self.PopupMenu(popup)   
    
    

    def OnBeginEdit(self, event):
        item = event.GetItem()
        if item and self.tree.GetItemText(item) == "The Root Item":
            wx.Bell()
            self.log.WriteText("You can't edit this one...\n")
            cookie = 0
            root = event.GetItem()
            (child, cookie) = self.tree.GetFirstChild(root)

            while child.IsOk():
                (child, cookie) = self.tree.GetNextChild(root, cookie)

            event.Veto()


    def OnEndEdit(self, event):
        for x in event.GetLabel():
            if x in string.digits:
                event.Veto()
                return


    def OnLeftDClick(self, event):
        pt = event.GetPosition();
        item, flags = self.HitTest(pt)
        if item:
            self.Expand(item)
            parent = self.GetItemParent(item)
            if parent.IsOk():
                #self.SortChildren(item)
                pass
        event.Skip()


    def OnSize(self, event):
        event.Skip()


    def OnItemExpanded(self, event):
        item = event.GetItem()
        if item:
            event.Skip()

    def OnItemCollapsed(self, event):
        item = event.GetItem()
        if item:
            pass

    def OnSelChanged(self, event):
        self.item = event.GetItem()
        if self.item:
            model = self.GetItemData(self.item)
            model.onActivate()       
        event.Skip()


    def OnActivate(self, event):
        if self.item:
            pass
        
        
    def OnCompareItems(self, item1, item2):
        t1 = self.GetItemText(item1)
        t2 = self.GetItemText(item2)
        if t1 < t2: return -1
        if t1 == t2: return 0
        return 1

    def OnDrag(self,evt):
        item = self.GetSelection()
        if item!=None and item.IsOk():
            itemmodel= self.GetPyData(item)
            if itemmodel.getScriptSnippet():
                data = wx.CustomDataObject("model")
                data.SetData(str(itemmodel.getScriptSnippet()))
                dropSource = wx.DropSource(self)
                dropSource.SetData(data)
                dropSource.DoDragDrop(wx.Drag_AllowMove)
            elif isinstance(itemmodel,Message):
                data = wx.CustomDataObject("message")
                data.SetData(str(itemmodel.getMessage().getID()))
                dropSource = wx.DropSource(self)
                dropSource.SetData(data)
                dropSource.DoDragDrop(wx.Drag_AllowMove)               
                
  
        
        
        
        
        
        

