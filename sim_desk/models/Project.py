import executor_context
from sim_desk.models.FolderModel import CommandResponseContainer,SquishContainer,MTICommandContainer,DAQIOContainer,ImageProcessingContainer, ScenarioPyContainer
import os
from sim_desk.mgr.appconfig import AppConfig
from utils import logger
import json
import copy
from sim_desk.models.CommandResponse import *
from sim_desk.mgr.tag_names import *
from serial.tools.list_ports import comports
from sim_desk.mgr.context import SimDeskContext
import executor_context

class Project(TreeModel):
    def __init__(self, projectname):
        TreeModel.__init__(self, None, "Project")
        self.project_dir = None
        self.project_file = None
        self.label = projectname
        self.default_perspective = None
        self.perspectives = {}
        prop_location = StringProperty("Location", "Location", "", editable=False)
        prop_location.setSavable(False)
        self.addProperties(prop_location)
        self._com_port_list = self.__enum_com_ports()
        prop_comport = EnumProperty("COM", "COM", 0,None,self._com_port_list,list(range(len(self._com_port_list))))
        self.addProperties(prop_comport)
        self.project_config_backup = {}
        self.loading_error = None
        self.project_config ={}
        self.project_config.setdefault('Project', {})
        self.project_config['Project']['name'] = self.label
        self.project_config['Project']['last_perspective'] = None
        self.squish_container: SquishContainer = None
        self.image_processing_container: ImageProcessingContainer = None
        self.scenario_py_container: ScenarioPyContainer = None
        if not executor_context.ExecutorContext().is_robot_context():
            SimDeskContext().set_project_model(self)

    def __enum_com_ports(self):
        comPorts = comports()
        return [comPort.name for comPort in comPorts]

    def getProjectDir(self):
        return self.project_dir

    def on_activate(self):
        TreeModel.on_activate(self)
        # childmodel = self.getChildByTag(TagName.TAG_NAME_SCRIPT)

    def init(self, project_dir):
        parts = project_dir.split("\\")
        self.project_dir = "\\\\".join(parts)
        self.project_file = os.path.join(self.project_dir, "project.json")
        self.label = os.path.basename(self.project_dir)
        self.getPropertyByName('Location').setStringValue(self.project_file)
        model = CommandResponseContainer(self)
        self.addChild(model)
        generator = ResponseModelGenerator(model)
        generator.create_command_response_models()
        self.squish_container = SquishContainer(self)
        self.addChild(self.squish_container)
        model = MTICommandContainer(self)
        self.addChild(model)
        model = DAQIOContainer(self)
        self.addChild(model)
        model = ScenarioPyContainer(self)
        self.scenario_py_container = model
        self.addChild(model)
        model = ImageProcessingContainer(self)
        self.image_processing_container = model
        self.addChild(model)

    def __load_json(self, project_dir):
        if not os.path.exists(project_dir):
            raise Exception("The project does not exists")
        self.init(project_dir)

        with open(self.project_file, 'rb') as pfile:
            self.project_config = json.load(pfile)
        self.project_config_backup = copy.deepcopy(self.project_config)

        self.project_config.setdefault('Project',{})
        self.project_config['Project']['name'] = self.label
        return self.project_config

    def open(self, project_dir):

        self.__load_json(project_dir)
        self.default_perspective = self.project_config['Project']['last_perspective']
        try:
            self.from_json(self.project_config['Project'])
            self.on_activate()
        except Exception as err:
            logger.error(err)

    def create(self, projectname, project_folder_dir):
        self.project_dir = os.path.join(project_folder_dir, projectname)
        self.init(self.project_dir)

        os.makedirs(self.project_dir)
        os.makedirs(os.path.join(self.project_dir, TAG_NAME_FOLDER_TESTLIBS))
        os.makedirs(os.path.join(self.project_dir, TAG_NAME_FOLDER_DOCUMENT))
        os.makedirs(os.path.join(self.project_dir, TAG_NAME_FOLDER_TESTCASES))
        os.makedirs(os.path.join(self.project_dir, TAG_NAME_FOLDER_TEST_REPORT))
        os.makedirs(os.path.join(self.project_dir, TAG_NAME_FOLDER_TESTASSET))
        self.project_config = {}
        self.project_config.setdefault('Project',{})
        self.project_config['Project']['name'] = self.label
        self.project_config['Project']['last_perspective'] = None

        with open(self.project_file, "w") as configfile:
            json.dump(self.project_config, configfile)
            configfile.close()
        self.save()
        self.on_activate()
        return True

    def close(self):
        TreeModel.close(self)
        AppConfig().addProjectHistory(self.project_dir)
        self.is_Dirty = False

    def to_json(self):
        json_result = TreeModel.to_json(self)
        self.project_config['Project'].update(json_result)

    def save(self):
        TreeModel.save(self)
        self.to_json()
        if self.isDirty():
            with open(self.project_file, "w") as configfile:
                json.dump(self.project_config, configfile)
                configfile.close()
        self.setDirty(False)

    def from_json(self,element):
        TreeModel.from_json(self,element)

    def saveDefaultPerspective(self, perspective):
        self.project_config['Project']['last_perspective'] = perspective
        self.default_perspective = perspective


    def getDefaultPerspective(self):
        return self.default_perspective


    def set_model_status(self, modelstatus):
        # if modelstatus == TREEMODEL_STATUS_RUNTIME:
        #     self.getProject_Tree().Enable(False)
        #     self.getProperties_Tree().Enable(False)
        # elif modelstatus == TREEMODEL_STATUS_NORMAL:
        #     self.getProject_Tree().Enable(True)
        #     self.getProperties_Tree().Enable(True)
        TreeModel.set_model_status(self, modelstatus)

