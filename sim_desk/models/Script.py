"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: Script.py
@time: 2023/3/26 11:35
@desc:
"""
import os.path
import sys
import importlib
import executor_context
from sim_desk.models.TreeModel import TreeModel
import sim_desk.ui.images
from sim_desk.models.TreeModel import TREEMODEL_STATUS_NORMAL
from sim_desk.mgr.tag_names import *
from sim_desk.models.CommonProperty import StringProperty,BoolProperty
from sim_desk.mgr.context import SimDeskContext
from sim_desk.models.TreeModel import TreeAction
import wx
from utils import logger
from scenario import Scenario
from executor_context import ExecutorContext
SCRIPT_DOC='''
#Callback Script File
#This file is used to define the callback functions when simulation 
#The predefined callbacks are like following
#
#This will be called when the simulation is started to run
#def onStart():
#    pass
#This will be called hen the simulation is stopped
#def onStop():
#    pass
#    
# def onMessage_XXX(message):
#    when XXX message is received
#
# def onButton_XXX(evt):
#    when XXX button is clicked
#
#def onTimer_XXX():
#    do some thing
#
def onStart():
    print "The test is started"

def onStop():
    print "The test is stopped"

'''


class ScriptModel(TreeModel):
    def __init__(self,parent,script_file_path=None):
        TreeModel.__init__(self, parent, TAG_NAME_SCRIPT)
        self.label = os.path.basename(script_file_path)
        self.script_file_path = script_file_path
        pathprop = StringProperty("Path", "Path", editable=False)
        self.addProperties(pathprop)
        pathprop.setStringValue(self.script_file_path)
        pathprop.setSavable(False)
        pathprop = StringProperty("Name", "Name", editable=False)
        self.addProperties(pathprop)
        basename = os.path.splitext(os.path.basename(self.script_file_path))[0]
        pathprop.setStringValue(basename)
        pathprop = StringProperty("Alias", "Alias", editable=True)
        self.addProperties(pathprop)
        pathprop.setStringValue(basename)
        pathprop = StringProperty("Description", "Description", editable=True)
        self.addProperties(pathprop)
        self.image = sim_desk.ui.images.script
        self.getModelParent().addChild(self)
        self.model_editor = None
        pathprop = BoolProperty("Enabled", "Enabled")
        pathprop.setSavable(True)
        self.addProperties(pathprop)
        self.tree_action_list.append(TreeAction("Remove", wx.ID_HIGHEST + 1001, self.remove_self))
        self.scenario_object = None

    def set_script_file_path(self,file_path):
        self.script_file_path = file_path

    def on_activate(self):
        TreeModel.on_activate(self)
        if not executor_context.ExecutorContext().is_robot_context():
            page_stc = SimDeskContext().get_main_frame().load_script_model(self)
            if self.model_editor is None:
                if not os.path.exists(self.script_file_path):
                    with open(self.script_file_path,"w") as sf:
                        sf.close()
            self.model_editor = page_stc
            with open(self.script_file_path,"r") as file:
                all_txt = file.read()
                page_stc.SetText(all_txt)

    def get_script_editor(self):
        return self.model_editor

    def save(self):

        if self.model_editor is not None:
            text = self.model_editor.GetText()
            with open(self.script_file_path,"w") as file:
                file.write(text)

    def close(self):
        self.save()

    def register_scenario(self):
        try:
            script_file_dir = os.path.dirname(self.script_file_path)
            sys.path.append(script_file_dir)
            script_base_name = os.path.basename(self.script_file_path)
            module_name = os.path.splitext(script_base_name)[0]
            scenario_module = sys.modules.get(module_name)
            if scenario_module is not None:
                importlib.reload(scenario_module)
            else:
                __import__(module_name)
                scenario_module = sys.modules[module_name]
            for name in dir(scenario_module):
                class_obj = getattr(scenario_module, name)
                if isinstance(class_obj, type) and issubclass(class_obj, Scenario) and class_obj is not Scenario:
                    self.scenario_object = class_obj()
                    ExecutorContext().simulator.add_command_listener(self.scenario_object)
        except ImportError as err:
            logger.error("Import the scenario error " + str(err))
            return None
        else:
            return self.scenario_object

    def set_model_status(self,modelstatus):
        if self.get_script_editor() is not None:
            if modelstatus == TREEMODEL_STATUS_NORMAL:
                self.get_script_editor().SetEditable(True)
            else:
                self.get_script_editor().SetEditable(False)
        TreeModel.set_model_status(self, modelstatus)

    def remove_self(self, event):
        dlg = wx.MessageDialog(self.getProject_Tree(), 'Please Confirm to delete',
                               'Confirm to delete',
                               # wx.OK | wx.ICON_INFORMATION
                               wx.YES_NO | wx.ICON_INFORMATION
                               )
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            if self.model_editor is not None:
                SimDeskContext().get_main_frame().unload_script_model(self)
            path = self.getPropertyByName("Path").getStringValue()
            if os.path.exists(path):
                os.remove(path)
            self.remove()
        dlg.Destroy()