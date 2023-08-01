"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: SquishNameFile.py
@time: 2023/3/26 11:35
@desc:
"""
import importlib
import os
import sys

import wx

from sim_desk.mgr.tag_names import *
from sim_desk.models.CommonProperty import (
    BoolProperty,
    EnumProperty,
    IntProperty,
    StringProperty,
)
from sim_desk.models.TreeModel import TreeAction, TreeModel
from sim_desk.ui.images import flex
from squish.squishPyServer import *


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
        name_prop = StringProperty("Name", "Name", editable=False)
        name_prop.setStringValue(name)
        name_prop.setSavable(False)
        self.addProperties(name_prop)
        object_prop = StringProperty("Object", "Object", editable=False)
        object_prop.setSavable(False)
        object_prop.setStringValue(str(name_object))
        self.addProperties(object_prop)
        alias_prop = StringProperty("Alias", "Alias", editable=True)
        alias_prop.setSavable(True)
        self.addProperties(alias_prop)
        self.tree_action_list.append(
            TreeAction("Mouse Click", wx.ID_HIGHEST + 1011, self.mouse_click)
        )

    def getImage(self):
        return flex

    def mouse_click(self, evt):
        str_value = self.getPropertyByName("Object").getStringValue()
        obj = eval(str_value)
        self.getRoot().squish_runner.mouse_click(obj)


class SquishNameFile(TreeModel):
    def __init__(self, parent, squish_file_path=None):
        TreeModel.__init__(self, parent, os.path.basename(squish_file_path))
        self.filepath = squish_file_path
        if self.filepath is not None:
            self.label = os.path.basename(self.filepath)
        self.tree_action_list.append(
            TreeAction("Remove", wx.ID_HIGHEST + 1001, self.remove_self)
        )
        path_prop = StringProperty("Path", "Path", editable=False)
        path_prop.setStringValue(self.filepath)
        path_prop.setSavable(False)
        self.addProperties(path_prop)

    def populate(self):
        names = parse_squish_name_file(self.filepath)
        for keyname, valueobj in names.items():
            sq_name = SquishName(self, keyname, valueobj)
            self.addChild(sq_name, addtotree=True)

    def from_json(self, element):
        TreeModel.from_json(self, element)

    def getImage(self):
        return flex

    def remove_self(self, event):
        dlg = wx.MessageDialog(
            self.getProject_Tree(),
            "Please Confirm to delete",
            "Confirm to delete",
            # wx.OK | wx.ICON_INFORMATION
            wx.YES_NO | wx.ICON_INFORMATION,
        )
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            path = self.getPropertyByName("Path").getStringValue()
            if os.path.exists(path):
                os.remove(path)
            self.remove()
        dlg.Destroy()
