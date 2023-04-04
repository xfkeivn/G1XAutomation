from sim_desk.models.CommonProperty import StringProperty
from sim_desk.models.CommonProperty import EnumProperty
from sim_desk.models.CommonProperty import BoolProperty
from sim_desk.models.CommonProperty import IntProperty
from sim_desk.models.TreeModel import TreeModel
from sim_desk.mgr.tag_names import *
from sim_desk.models.TreeModel import TreeAction
import os
import wx
from sim_desk.ui.images import flex
import importlib
import sys
from squish.squish_lib import *


def parse_squish_name_file(name_file):
    squish_names = {}
    start_dir = os.path.dirname(name_file)
    if start_dir not in sys.path:
        sys.path.insert(0, start_dir)

    name_file = os.path.basename(name_file)
    name = os.path.splitext(os.path.normpath(name_file))[0]
    __import__(name)
    module = sys.modules[name]
    for name in dir(module):
        obj = getattr(module, name)
        if type(obj) is dict and name != "__builtins__":
            squish_names[name] = obj
    return squish_names


class SquishName(TreeModel):
    def __init__(self, parent, name, name_object):
        TreeModel.__init__(self, parent, name)
        pathprop = StringProperty("Name", "Name", editable=False)
        pathprop.setStringValue(name)
        pathprop.setSavable(False)
        self.addProperties(pathprop)
        pathprop = StringProperty("Object", "Object", editable=False)
        pathprop.setSavable(False)
        pathprop.setStringValue(str(name_object))
        self.addProperties(pathprop)
        pathprop = StringProperty("Alias", "Alias", editable=True)
        pathprop.setSavable(True)
        self.addProperties(pathprop)

    def getImage(self):
        return flex


class SquishNameFile(TreeModel):
    def __init__(self, parent, squish_file_path=None):
        TreeModel.__init__(self, parent, os.path.basename(squish_file_path))
        self.filepath = squish_file_path
        if self.filepath is not None:
            self.label = os.path.basename(self.filepath)
        self.tree_action_list.append(TreeAction("Remove", wx.ID_HIGHEST + 1001, self.remove_self))
        pathprop = StringProperty("Path", "Path", editable=False)
        pathprop.setStringValue(self.filepath)
        pathprop.setSavable(False)
        self.addProperties(pathprop)

    def populate(self):
        names = parse_squish_name_file(self.filepath)
        for keyname,valueobj in names.items():
            sq_name = SquishName(self,keyname,valueobj)
            self.addChild(sq_name,addtotree=True)

    def from_json(self,element):
        TreeModel.from_json(self,element)


    def getImage(self):
        return flex

    def remove_self(self, event):
        dlg = wx.MessageDialog(self.getProject_Tree(), 'Please Confirm to delete',
                               'Confirm to delete',
                               # wx.OK | wx.ICON_INFORMATION
                               wx.YES_NO | wx.ICON_INFORMATION
                               )
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            self.remove()
        dlg.Destroy()
