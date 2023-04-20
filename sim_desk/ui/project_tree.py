import wx
from sim_desk.ui import images
import string
from sim_desk.models.TreeModel import EVT_ADD_TO_TREE_EVENT
from sim_desk.models.TreeModel import EVT_REMOVE_FROM_TREE_EVENT
from sim_desk.models.TreeModel import EVT_UPDATE_TREE_ITEM_IMAGE
from sim_desk.models.TreeModel import EVT_UPDATE_TREE_ITEM_LABEL
from sim_desk.models.CommandResponse import FieldNumberModel, CommandResponseModel
from utils import logger

TREE_POP_MENU_ID = wx.ID_HIGHEST + 10100


class ProjectTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, id, pos, size, style):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style)

        isz = (16, 16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldr_idx = il.Add(images.folder_collapse.GetBitmap())
        self.fldr_open_idx = il.Add(images.folder_expand.GetBitmap())
        self.prj_idx = il.Add(images.nested_projects.GetBitmap())
        self.AssignImageList(il)
        self.il = il
        self.root = None

        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_item_expanded, self)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_item_collapsed, self)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed, self)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.on_begin_edit, self)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.on_end_edit, self)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activate, self)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_lef_dclick)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(EVT_ADD_TO_TREE_EVENT, self.add_2_tree)
        self.Bind(EVT_REMOVE_FROM_TREE_EVENT, self.remove_from_tree)
        self.Bind(EVT_UPDATE_TREE_ITEM_IMAGE, self.update_tree_item_image)
        self.Bind(EVT_UPDATE_TREE_ITEM_LABEL, self.update_tree_item_label)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_drag)
        self.item_model = {}

    def update_tree_item_image(self, evt):
        image = evt.image
        model = evt.model
        item = self.item_model.get(model)
        index = self.il.Add(image.GetBitmap())
        self.SetItemImage(item, index, wx.TreeItemIcon_Normal)

    def update_tree_item_label(self, evt):
        label = evt.label
        model = evt.model
        item = self.item_model.get(model)
        self.SetItemText(item, label)

    def add_2_tree(self, event):

        parent_model = event.parent_model
        child_model = event.model_to_add
        parent_item = self.item_model.get(parent_model)
        if parent_item is None:
            self.GetParent().console.error("The tree item does not exists, unlikely to happen")
        new_item = self.AppendItem(parent_item, child_model.getLabel())

        if child_model.getImage() is not None:
            index = self.il.Add(child_model.getImage().GetBitmap())
            self.SetItemImage(new_item, index, wx.TreeItemIcon_Normal)
            pass
        self.SetItemData(new_item, child_model)
        self.item_model[child_model] = new_item
        child_model.setTreeItem(new_item)

    def remove_from_tree(self, event):
        model = event.model_to_remove
        item = self.item_model[model]
        self.Delete(item)
        del self.item_model[model]

    def assign_project(self, project_model):
        self.DeleteAllItems()
        self.item_model.clear()
        self.root = self.AddRoot("project", self.prj_idx)
        self.SetItemText(self.root, project_model.getLabel())
        self.SetItemData(self.root, project_model)
        project_model.project_tree = self
        self.item_model[project_model] = self.root

    def get_item_by_data(self, pydata, parent_item=None):
        if parent_item is None:
            parent_item = self.root
            if self.GetPyData(self.root) == pydata:
                return self.root
        item, cookie = self.GetFirstChild(parent_item)

        while item.IsOk():
            if self.GetPyData(item) == pydata:
                return item
            if self.GetChildrenCount(item) > 0:
                c_item = self.get_item_by_data(pydata, item)
                if c_item is not None:
                    return c_item
            item, cookie = self.GetNextChild(item, cookie)

    def on_right_down(self, event):
        pt = event.GetPosition();
        item, flags = self.HitTest(pt)
        if item:
            self.SelectItem(item)

    def on_left_down(self, event):
        pt = event.GetPosition();
        item, flags = self.HitTest(pt)
        if item:
            self.SelectItem(item)
        event.Skip()

    def on_right_up(self, event):
        pt = event.GetPosition();
        item, flags = self.HitTest(pt)
        if item:
            model = self.GetItemData(item)
            self.show_popup_menu(model)

    def show_popup_menu(self, model):
        if len(model.getActions()) > 0:
            popup = wx.Menu()
            index = 0
            for action in model.getActions():
                item = wx.MenuItem(popup, TREE_POP_MENU_ID + index, action.name, )
                popup.Append(item)
                popup.Bind(wx.EVT_MENU, action.callable, id=item.GetId())
                index += 1
            self.PopupMenu(popup)

    def on_begin_edit(self, event):
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

    def on_end_edit(self, event):
        for x in event.GetLabel():
            if x in string.digits:
                event.Veto()
                return

    def on_lef_dclick(self, event):
        pt = event.GetPosition();
        item, flags = self.HitTest(pt)
        if item:
            self.Expand(item)
            parent = self.GetItemParent(item)
            itemmodel = self.GetItemData(item)
            if isinstance(itemmodel, FieldNumberModel):
                logger.info(itemmodel.get_parameter_name()[0])
            if parent.IsOk():
                # self.SortChildren(item)
                pass
        event.Skip()

    def on_size(self, event):
        event.Skip()

    def on_item_expanded(self, event):
        item = event.GetItem()
        if item:
            event.Skip()

    def on_item_collapsed(self, event):
        item = event.GetItem()
        if item:
            pass

    def on_sel_changed(self, event):
        self.item = event.GetItem()
        if self.item:
            model = self.GetItemData(self.item)
            model.on_activate()
        event.Skip()

    def on_activate(self, event):
        if self.item:
            pass

    def OnCompareItems(self, item1, item2):
        t1 = self.GetItemText(item1)
        t2 = self.GetItemText(item2)
        if t1 < t2: return -1
        if t1 == t2: return 0
        return 1

    def on_drag(self, evt):
        item = self.GetSelection()
        if item is not None and item.IsOk():
            itemmodel = self.GetItemData(item)
            if isinstance(itemmodel, CommandResponseModel) or isinstance(itemmodel, FieldNumberModel):
                snippet = itemmodel.get_script_snippet()
                if snippet != "":
                    data = wx.TextDataObject("model")
                    data.SetText(snippet)
                    dropSource = wx.DropSource(self)
                    dropSource.SetData(data)
                    dropSource.DoDragDrop(wx.Drag_AllowMove)
