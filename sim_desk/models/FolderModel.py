from sim_desk.models.TreeModel import TreeModel
import sim_desk
import wx
from sim_desk.models.TreeModel import TreeAction

class CommandResponseContainer(TreeModel):
    def __init__(self,parent):
        TreeModel.__init__(self, parent, "Command Responses")
        self.label= "Command Responses"


    def getImage(self):
        return sim_desk.ui.images.folder_collapse


class SquishContainer(TreeModel):
    def __init__(self, parent):
        TreeModel.__init__(self, parent, "Squish Names")
        self.label = "Squish Names"



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