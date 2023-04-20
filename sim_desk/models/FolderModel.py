"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: FolderModel.py
@time: 2023/3/26 11:35
@desc:
"""
from sim_desk.models.TreeModel import TreeModel
import sim_desk
from sim_desk.models.ImageModel import *
import shutil
from sim_desk.models.SquishNameFile import *
from sim_desk.models.Script import *
from sim_desk.mgr.tag_names import *
from utils import logger
python_file_wildcard = "Script File (*.py)|*.py"
image_file_wildcard = "Image File (*.png)|*.png"

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
            wildcard=python_file_wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.path.exists(path):
                if self.isAllready(path):
                    wx.MessageDialog(None, "Name file Already exists", "Name file not added", wx.OK).ShowModal()
                    return
                abs_path = self.copy_to_project_local_folder(path)
                squish_name_file = SquishNameFile(self, abs_path)
                self.addChild(squish_name_file)
                squish_name_file.populate()


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


class ImageProcessingContainer(TreeModel):
    def __init__(self, parent):
        TreeModel.__init__(self, parent, "Image Features")
        self.label = "Image Features"
        self.tree_action_list.append(
            TreeAction("Import Image File", wx.ID_HIGHEST + 2000, self.import_image_file))

    def get_image_object(self, image_alias):
        for child in self.getModelChildren():
            if child.getPropertyByName("Alias").getStringValue() == image_alias:
                return child
        raise Exception(f"The image alias {image_alias} is not found ")

    def get_feature_rect(self, image_alias,rect_alias):
        image_object = self.get_image_object(image_alias)
        for rect in image_object.getModelChildren():
            alias = rect.getPropertyByName("Alias").getStringValue()
            if alias == rect_alias:
                return eval(rect.getPropertyByName("Region").getStringValue())
        raise Exception(f"The rect alias {rect_alias} is not  found ")


    def getImage(self):
        return sim_desk.ui.images.folder_collapse

    def from_json(self,element):
        if element.get('sub_models') is not None:
            for name, module in element['sub_models'].items():
                abs_path = module['properties']['Path']['value']
                image_model = ImageModel(self, abs_path)
                self.addChild(image_model)
        TreeModel.from_json(self,element)

    def import_image_file(self,evt):
        dlg = wx.FileDialog(
            self.getProject_Tree(), message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=image_file_wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.path.exists(path):
                if self.isAllready(path):
                    wx.MessageDialog(None, "Name file Already exists", "Name file not added", wx.OK).ShowModal()
                    return
                self.import_it(path);

    def import_to_asset(self,path):
        abs_path = self.copy_to_project_local_folder(path)
        image_model = ImageModel(self, abs_path)
        self.addChild(image_model)
        image_model.populate()


class ScenarioPyContainer(TreeModel):
    def __init__(self, parent):
        TreeModel.__init__(self, parent, "Scenarios Script")
        self.label = "Scenarios Script"
        self.tree_action_list.append(
            TreeAction("Add a new scenario script file", wx.ID_HIGHEST + 1000, self.add_new))
        self.tree_action_list.append(
            TreeAction("Import a new scenario script file", wx.ID_HIGHEST + 1000, self.import_scenario_file))

    def getImage(self):
        return sim_desk.ui.images.folder_collapse

    def from_json(self,element):
        if element.get('sub_models') is not None:
            for name, module in element['sub_models'].items():
                abs_path = module['properties']['Path']['value']
                script_model = ScriptModel(self, abs_path)
            TreeModel.from_json(self,element)

    def import_scenario_file(self,event):
        dlg = wx.FileDialog(
            self.getProject_Tree(), message="Choose a file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=python_file_wildcard,
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if os.path.exists(path):
                if self.isAllready(path):
                    wx.MessageDialog(None, "Name file Already exists", "Name file not added", wx.OK).ShowModal()
                    return
                abs_path = self.copy_to_project_local_folder(path)
                ScriptModel(self,abs_path)

    def add_new(self,event):
        dlg = wx.TextEntryDialog(self.getProject_Tree(),"Please input a script name","Script Name(.py)")
        if dlg.ShowModal() == wx.ID_OK:
            txt:str = dlg.GetValue()
            assets_folder = os.path.join(self.getRoot().getProjectDir(), TAG_NAME_FOLDER_TESTASSET)
            script_file_name = os.path.join(assets_folder,txt)
            scriptmodel = ScriptModel(self,script_file_name)
            current_path = os.path.dirname(__file__)
            class_name:str = txt.rstrip(".py")
            root_path = os.path.join(current_path,"../..")
            template_file = os.path.join(root_path,"scenario_template.py")
            with open(template_file,"r") as template_file:
                txt = template_file.read()
                txt = txt.replace("{{Scenario_Name}}",class_name.capitalize())
                with open(script_file_name,"w") as script_file:
                    script_file.write(txt)

    def start_all_scenarios(self):
        for sce in self.getModelChildren():
            name = sce.getPropertyByName('Alias').getStringValue()
            self.start_scenario(name)

    def stop_all_scenarios(self):
        for sce in self.getModelChildren():
            name = sce.getPropertyByName('Alias').getStringValue()
            self.stop_scenario(name)

    def start_scenario(self,scenario_name):
        for sce in self.getModelChildren():
            if sce.getPropertyByName('Alias').getStringValue() == scenario_name:
                if sce.getPropertyByName('Enabled').getStringValue() == "True":
                    obj = sce.register_scenario()
                    if obj is not None:
                        obj.start_scenario()
                        logger.info(f'The scenario {scenario_name} is started')
                else:
                    logger.warn(f'The scenario {scenario_name} is disabled in the configuration')
                    break

    def stop_scenario(self, scenario_name):
        for sce in self.getModelChildren():
            if sce.getPropertyByName('Alias').getStringValue() == scenario_name:
                if sce.getPropertyByName('Enabled').getStringValue() == "True":
                    if sce.scenario_object is not None:
                        sce.scenario_object.stop_scenario()
                        logger.info(f'The scenario {scenario_name} is stopped')
                else:
                    logger.warn(f'The scenario {scenario_name} is disabled in the configuration')
                    break

