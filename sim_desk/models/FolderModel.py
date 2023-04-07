from sim_desk.models.TreeModel import TreeModel
import sim_desk
import wx
from sim_desk.models.TreeModel import TreeAction
import os
import shutil
from sim_desk.models.SquishNameFile import *
from sim_desk.mgr.tag_names import *
name_file_wildcard = "Name File (*.py)|*.py"
import json

class CommandResponseContainer(TreeModel):
    def __init__(self,parent):
        TreeModel.__init__(self, parent, "Command Responses")
        self.label= "Command Responses"

    def getImage(self):
        return sim_desk.ui.images.folder_collapse


class SquishContainer(TreeModel):
    def __init__(self, parent):
        TreeModel.__init__(self, parent, TAG_NAME_SQUISH_NAMES_CONTAINER)
        self.label = TAG_NAME_SQUISH_NAMES_CONTAINER
        pathprop = StringProperty("IP", "IP", editable=True)
        pathprop.setStringValue("192.168.80.130")
        pathprop.setSavable(True)
        self.addProperties(pathprop)
        pathprop = StringProperty("AUT", "AUT", editable=True)
        pathprop.setStringValue("gx1")
        pathprop.setSavable(True)
        self.addProperties(pathprop)
        pathprop = StringProperty("PrivateKey", "PrivateKey", editable=True)
        pathprop.setStringValue(r"C:\Users\xuf\.ssh\bsci")
        pathprop.setSavable(True)
        self.addProperties(pathprop)
        pathprop = BoolProperty("Enabled", "Enabled")
        pathprop.setSavable(True)
        self.addProperties(pathprop)

        self.tree_action_list.append(TreeAction("Import Squish Name Files", wx.ID_HIGHEST + 1000, self.import_squish_names))

    def getActions(self):
        return TreeModel.getActions(self)

    def get_all_name_mapping(self):
        name_mapping = {}
        for file_child_model in self.children_models:
            for name_child_model in file_child_model.children_models:
                obj = name_child_model.getPropertyByName("Object").getStringValue()
                alias = name_child_model.getPropertyByName("Alias").getStringValue()
                name_mapping[alias] = eval(obj)
        return name_mapping

    def from_json(self,element):
        for name, module in element['sub_models'].items():
            abs_path = module['properties']['Path']['value']
            squish_name_file = SquishNameFile(self, abs_path)
            self.addChild(squish_name_file)
            squish_name_file.populate()

        TreeModel.from_json(self,element)

    def import_squish_names(self, event):
        dlg = wx.FileDialog(
            self.getProject_Tree(), message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=name_file_wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.path.exists(path):
                if self.__isAllready(path):
                    wx.MessageDialog(None, "Name file Already exists", "Name file not added", wx.OK).ShowModal()
                    return
                abs_path = self.copy_to_project_local_folder(path)
                squish_name_file = SquishNameFile(self, abs_path)
                self.addChild(squish_name_file)
                squish_name_file.populate()

    def __isAllready(self,absname):
        for dbcmodel in self.getModelChildren():
            if dbcmodel.getLabel() == os.path.exists(absname):
                return True
        return False

    def copy_to_project_local_folder(self,src):
        dirtocopy = os.path.join(self.getRoot().getProjectDir(), TAG_NAME_FOLDER_TESTASSET)
        abs_path = os.path.join(dirtocopy,os.path.basename(src))
        shutil.copy(src,abs_path)
        return abs_path

    def getImage(self):
        return sim_desk.ui.images.folder_collapse


class MTICommandContainer(TreeModel):
    def __init__(self, parent):
        TreeModel.__init__(self, parent, "MTI Commands")
        self.label = "MTI Commands"


    def getImage(self):
        return sim_desk.ui.images.folder_collapse


class DAQIOContainer(TreeModel):
    def __init__(self, parent):
        TreeModel.__init__(self, parent, "DAQ IOs")
        self.label = "DAQ IOs"



    def getImage(self):
        return sim_desk.ui.images.folder_collapse