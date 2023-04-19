from utils.singleton import Singleton


class SimDeskContext(metaclass=Singleton):
    def __init__(self):
        from sim_desk.ui.mainframe import MainFrame
        from sim_desk.models.Project import Project
        from sim_desk.ui.ImagePanel import ImagePanel
        self.__main_frame:MainFrame = None
        self.__project_model:Project = None
        self.__image_feature_panel:ImagePanel = None

    def set_image_feature_panel(self, image_feature_panel):
        self.__image_feature_panel = image_feature_panel

    def get_image_feature_panel(self):
        return self.__image_feature_panel

    def set_main_frame(self,main_frame):

        self.__main_frame = main_frame

    def get_main_frame(self):
        return self.__main_frame

    def set_project_model(self,project_model):
        self.__project_model = project_model

    def get_project_model(self):
        return self.__project_model



