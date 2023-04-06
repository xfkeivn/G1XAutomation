import os
from sim_desk import constant
import json
from utils.singleton import Singleton
KEY_PROJECT_HISTORIES = "ProjectHistories"
KEY_INSTALLED_DRIVERS="InstalledDrivers"
KEY_DEFAULT_PERSPECTIVE = "DefaultPerspective"
KEY_PERSPECTIVES = "Perspectives"


class AppConfig(metaclass=Singleton):
    def __init__(self):
        self.appconfig={}
        userdir = os.path.expanduser("~")
        self.appdir = os.path.join(userdir, constant.APPNAME)
        self.driverdir = os.path.join(self.appdir, constant.DRIVER_FOLDER_NAME)
        if not os.path.exists(self.appdir):
            os.makedirs(self.appdir)
            os.makedirs(self.driverdir)
            
        self.app_config_file = os.path.join(self.appdir, constant.APP_CONFIG_FILE_NAME)
        if not os.path.exists(self.app_config_file):
            self.save()
        configfile = open(self.app_config_file,"r")
        self.appconfig = json.load(configfile)
        configfile.close()
        
    def save(self):
        with open(self.app_config_file,"w") as configfile:
            json.dump(self.appconfig,configfile)
            configfile.close()
    
    def getAppConfigDir(self):
        return self.appdir
    def getDriverDir(self):
        return self.driverdir
    
    def getProjectHistoryList(self):
        validateprojectlist = []
        projecthistories = self.appconfig.get(KEY_PROJECT_HISTORIES)
        if projecthistories == None:
            projecthistories = []
        #check the project still exists
        for history in projecthistories: 
            if os.path.exists(history):
                validateprojectlist.append(os.path.normpath(history))
        #update the appconfig
        self.appconfig[KEY_PROJECT_HISTORIES] = validateprojectlist
        return validateprojectlist

    def addProjectHistory(self,projectdir):
        projectdir = os.path.normpath(projectdir)
        projectlist = self.getProjectHistoryList()
        if projectdir in projectlist:
            projectlist.remove(projectdir)
        projectlist.append(projectdir)
        if len(projectlist) >= constant.APP_CONFIG_PROJECT_HISTORY_MAX:
            projectlist.pop(0)
        self.appconfig[KEY_PROJECT_HISTORIES] = projectlist
    
    

        
        
        
        
        