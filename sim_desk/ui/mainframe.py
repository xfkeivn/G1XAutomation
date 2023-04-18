import threading

import wx
import os
from sim_desk import constant
from sim_desk.mgr.context import SimDeskContext
from sim_desk.mgr.appconfig import AppConfig
from sim_desk.ui.propertygrid import PropertyGridPanel
from sim_desk.ui.project_tree import ProjectTreeCtrl
from sim_desk.ui.wizards.NewProjectWizard import NewProjectWizard as NPW
from sim_desk.models.Project import Project
from sim_desk.models.TreeModel import *
from sim_desk.ui.scrip_editor import PythonSTC
from BackPlaneSimulator import BackPlaneSimulator as BPS
from sim_desk.ui.screenframe import MyScrolledPanel
from sim_desk.ui.ImagePanel import *
from sim_desk.ui.console import Console
import executor_context
import subprocess
try:
    from agw import aui
except ImportError:  # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui
from sim_desk.ui import statusbar, images
from squish.squish_lib import *
from squish.squish_proxy import *
ID_NewProject = wx.ID_HIGHEST + 1
ID_ImportProject = wx.ID_HIGHEST + 2
ID_ExportProject = wx.ID_HIGHEST + 3
ID_ViewProjects = wx.ID_HIGHEST + 4
ID_ViewConsole = wx.ID_HIGHEST + 5
ID_ViewProperties = wx.ID_HIGHEST + 6
ID_CustomizeToolbar = wx.ID_HIGHEST + 20
ID_SampleItem = wx.ID_HIGHEST + 21
ID_SaveProject = wx.ID_HIGHEST + 22
ID_StartTest = wx.ID_HIGHEST + 26
ID_StopTest = wx.ID_HIGHEST + 27
ID_ClearLog = wx.ID_HIGHEST + 29
ID_ScreenShot = wx.ID_HIGHEST + 30
ID_Robot = wx.ID_HIGHEST + 31
ID_FirstLastestProject = wx.ID_HIGHEST + 40


class MainFrame(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        SimDeskContext().set_main_frame(self)
        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.SetIcon(images.main.GetIcon())
        self.sb = statusbar.StatusBar(self)
        self.SetStatusBar(self.sb)
        self.screen_window = None
        self.process = None
        self.notebook = None
        self.screen_image = None
        self.BuildPanes()
        self.CreateMenuBar()
        self.BindEvents()
        self.active_project = None
        self.squish_runner = None
        self.__fast_open_projects_list = []
        self.appconfig = AppConfig()
        self.SetTitle("G1X Simulator Control Desk")
        self.feature_detection_panel = None
        self.append_projects_to_fast_open(self.appconfig.getProjectHistoryList())
        # when the ui is all done, set the IO to Console
        self.bps = BPS()
        self.squish_runner = None

        self.init()
        self._mgr.Update()
        executor_context.ExecutorContext().set_gui_context(self)


    def init(self):
        projecthistories = self.appconfig.getProjectHistoryList()
        # Open Latest Project
        if len(projecthistories) > 0:
            lastprojectdir = projecthistories[-1]
            self.OpenProject(lastprojectdir)
        self.__onNormalState()
        if self.active_project is None:
            self.tb.EnableTool(ID_StartTest, False)
            self.tb.EnableTool(ID_StopTest, False)

    def CreateMenuBar(self):

        mb = wx.MenuBar()
        self.file_menu = wx.Menu()
        file_menu = self.file_menu
        file_menu.Append(ID_NewProject, "New")
        file_menu.Append(ID_ImportProject, "Import")
        # file_menu.Append(ID_ExportProject, "Export")
        file_menu.Append(wx.ID_EXIT, "Exit")
        view_menu = wx.Menu()
        view_menu.Append(ID_ViewProjects, "Show Projects")
        view_menu.Append(ID_ViewConsole, "Show Console")
        view_menu.Append(ID_ViewProperties, "Show Properties")
        view_menu.AppendSeparator()
        view_menu.Append(ID_ClearLog, "Clear Log")
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "About...")
        mb.Append(file_menu, "&File")
        mb.Append(view_menu, "&View")
        mb.Append(help_menu, "&Help")

        self.SetMenuBar(mb)

    def BuildPanes(self):

        self.SetMinSize(wx.Size(400, 300))
        tb1 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                             agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW)
        tb1.AddSimpleTool(ID_NewProject, "New Project", images.NewProject.GetBitmap())
        tb1.AddSimpleTool(ID_SaveProject, "Save Project", images.save_edit.GetBitmap())
        tb1.AddSimpleTool(ID_ImportProject, "Import Project", images.Import.GetBitmap())
        tb1.AddSeparator()
        tb1.AddSimpleTool(ID_ViewProjects, "ViewProject", images.viewproj.GetBitmap())
        tb1.AddSimpleTool(ID_ViewProperties, "ViewProperties", images.viewprop.GetBitmap())
        tb1.AddSimpleTool(ID_ViewConsole, "ViewConsole", images.viewconsole.GetBitmap())
        tb1.AddSeparator()
        tb1.AddSimpleTool(ID_StartTest, "StartTest", images.run.GetBitmap())
        tb1.AddSimpleTool(ID_StopTest, "StopTest", images.stop.GetBitmap())
        tb1.AddSeparator()
        tb1.AddSimpleTool(ID_ScreenShot, "ScreenShot", images.camera.GetBitmap())
        tb1.Realize()
        tb1.AddSimpleTool(ID_Robot, "Start RIDE", images.robot.GetBitmap())
        tb1.Realize()
        self.tb = tb1
        self._mgr.AddPane(self.CreateProjectTreeCtrl(), aui.AuiPaneInfo().
                          Name("ProjectExplorer").Caption("Project Explorer").
                          Left().Layer(2).MinimizeButton(True).Icon(images.viewproj.GetBitmap()))
        self._mgr.AddPane(self.CreatePropertyGrid(), aui.AuiPaneInfo().
                          Name("Properties").Caption("Properties").
                          Left().Layer(2).Position(1).MinimizeButton(True).Icon(images.viewprop.GetBitmap()))
        self._mgr.AddPane(self.CreateConsoleCtrl(), aui.AuiPaneInfo().Name("Console").Caption("Console").
                          Bottom().MinimizeButton(True).Icon(images.viewconsole.GetBitmap()))

        self._mgr.AddPane(self.CreateNotebook(), aui.AuiPaneInfo().Name("Desk").Caption("Desk").
                          Centre().CloseButton(False).CaptionVisible(False))
        self._mgr.AddPane(tb1, aui.AuiPaneInfo().Name("tb1").Caption("Big Toolbar").ToolbarPane().Top())
        self.original_perspective = self._mgr.SavePerspective()

    def clearlog(self, evt):
        self.console.clear()

    def append_projects_to_fast_open(self, project_dir_list):
        for projectdir in project_dir_list:
            projectdir = os.path.normpath(projectdir)
            if projectdir not in self.__fast_open_projects_list:
                if len(self.__fast_open_projects_list) == 0:
                    self.file_menu.AppendSeparator()
                self.file_menu.Append(ID_FirstLastestProject + len(self.__fast_open_projects_list),
                                      os.path.basename(projectdir))
                self.__fast_open_projects_list.append(projectdir)

    def add_to_center_panel(self, window):
        self._mgr.AddPane(window,
                          aui.AuiPaneInfo().Name(str(window.getLabel())).Centre().MaximizeButton(True).PaneBorder(
                              True).Caption(str(window.getLabel())))
        self._mgr.Update()
        return window

    def BindEvents(self):
        self.Bind(wx.EVT_MENU, self.OnNewProject, id=ID_NewProject)
        self.Bind(wx.EVT_MENU, self.OnSaveProject, id=ID_SaveProject)
        self.Bind(wx.EVT_MENU, self.OnImportProject, id=ID_ImportProject)
        self.Bind(wx.EVT_MENU, self.onScreenShot, id = ID_ScreenShot)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(EVT_MODEL_DIRTYSTATE_CHANGE_EVENT, self.onDirtyStateChanged)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnNotebookPageClose)
        self.Bind(wx.EVT_MENU_RANGE, self.onOpenProject, id=ID_FirstLastestProject, id2=ID_FirstLastestProject + 7)
        self.Bind(wx.EVT_MENU, self.onStart, id=ID_StartTest)
        self.Bind(wx.EVT_MENU, self.onStop, id=ID_StopTest)
        self.Bind(wx.EVT_MENU, self.on_start_robot, id=ID_Robot)
        self.Bind(wx.EVT_MENU, self.clearlog, id=ID_ClearLog)

    def __del__(self):
        pass

    @property
    def squisher(self):
        return self.squish_runner

    def on_start_robot(self, evt):
        # Activate the virtual environment
        venv_path = os.path.join(os.path.dirname(__file__),"../../venv")
        activate_script = os.path.join(venv_path, 'Scripts', 'activate.bat')
        subprocess.call(activate_script, shell=True)

        # Start the subprocess using the virtual environment's Python interpreter
        python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
        subprocess.Popen([python_path, os.path.join(venv_path,'Scripts','ride.py')])

    def onStart(self, evt):
        self.SetWindowStyle(wx.CAPTION | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX | wx.RESIZE_BORDER)
        com_port_val = self.active_project.getPropertyByName("COM").getStringValue()
        result = self.bps.start(com_port_val)
        enabled_squish = self.active_project.squish_container.getPropertyByName("Enabled")
        if result and enabled_squish.getStringValue() == "True":
            ip_prop = self.active_project.squish_container.getPropertyByName("IP")
            aut_prop = self.active_project.squish_container.getPropertyByName("AUT")
            private_key = self.active_project.squish_container.getPropertyByName("PrivateKey")
            if ip_prop and aut_prop:
                ip_address = ip_prop.getStringValue()
                aut_name = aut_prop.getStringValue()
                private_key_file = private_key.getStringValue()
                self.squish_runner = SquishProxy(ip_address,private_key_file,aut_name)
                self.squish_runner.create_proxy()
                self.squish_runner.connect()
                self.active_project.squish_runner = self.squish_runner
                self.screen_window.start()
                #self.timer.Start(500)
        self.active_project.scenario_py_container.start_all_scenarios()
        if result:
            self.__onRuntimeState()

    def __onRuntimeState(self):
        if self.active_project:
            self.active_project.set_model_status(TreeModel.TREEMODEL_STATUS_RUNTIME)

        toolcount = self.tb.GetToolCount()
        for toolindex in range(toolcount):
            tool = self.tb.FindToolByIndex(toolindex)
            self.tb.EnableTool(tool.GetId(), False)
        self.tb.EnableTool(ID_ScreenShot, True)
        self.tb.EnableTool(ID_StopTest, True)
        self.sb.SetText1("Project is running")
        #self.sb.SetStatus(TreeModel.TREEMODEL_STATUS_RUNTIME)
        self.GetMenuBar().EnableTop(0, False)
        self.GetMenuBar().EnableTop(1, False)
        self.GetMenuBar().EnableTop(2, False)
        self.tb.Realize()

    def __onNormalState(self):
        if self.active_project:
            self.active_project.set_model_status(TREEMODEL_STATUS_NORMAL)
            toolcount = self.tb.GetToolCount()
            for toolindex in range(toolcount):
                tool = self.tb.FindToolByIndex(toolindex)
                self.tb.EnableTool(tool.GetId(), True)
                if tool.GetId() == ID_SaveProject:
                    self.tb.EnableTool(ID_SaveProject, self.active_project.isDirty())
        self.tb.EnableTool(ID_StopTest, False)
        self.sb.SetText1("Project is Editing")
        self.sb.SetStatus(TREEMODEL_STATUS_NORMAL)
        self.GetMenuBar().EnableTop(0, True)
        self.GetMenuBar().EnableTop(1, True)
        self.GetMenuBar().EnableTop(2, True)
        self.tb.EnableTool(ID_ScreenShot, False)
        self.tb.Realize()

    def onStop(self, evt):
        self.active_project.scenario_py_container.stop_all_scenarios()
        self.screen_window.stop()
        if self.bps.stop():
            self.__onNormalState()
            self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER)
        if self.squish_runner:
            self.squish_runner.disconnect()


    def onScreenShot(self,evt):
        dirname = os.path.dirname(__file__)
        screenshot_folder = os.path.join(dirname,"../screenshot")
        if self.squish_runner:
            name = time.strftime('%Y%b%d_%H_%M_%S.png', time.localtime())
            full_path_name = os.path.join(screenshot_folder,name)
            self.squish_runner.screen_save(full_path_name)

    def OnPaneClose(self, evt):
        # print "close pane"
        evt.Skip()

    def OnNotebookPageClose(self, evt):
        # print "close pane"
        evt.Skip()

    def showPane(self, evt):
        id = evt.Id
        if id == ID_ViewProjects:
            self._mgr.ShowPane(self._mgr.GetPaneByName("ProjectExplorer").window, True)
        elif id == ID_ViewConsole:
            self._mgr.ShowPane(self._mgr.GetPaneByName("Console").window, True)
        elif id == ID_ViewProperties:
            self._mgr.ShowPane(self._mgr.GetPaneByName("Properties").window, True)

    def removePage(self, name):
        panel = self._mgr.GetPaneByName(name)
        if panel:
            self._mgr.ClosePane(panel)
            self._mgr.DetachPane(panel.window)
            self._mgr.Update()

    def onDirtyStateChanged(self, evt):
        self.tb.EnableTool(ID_SaveProject, evt.dirtystate)
        self.tb.Realize()

    def OnSaveProject(self, evt):
        if self.active_project:
            perspective_default = self._mgr.SavePerspective()
            self.active_project.saveDefaultPerspective(perspective_default)
            self.active_project.save()
            self.tb.EnableTool(ID_SaveProject, False)
            self.tb.Realize()

    def OnClose(self, event):

        if self.__Close_Active_Project() is False:
            event.Veto()
            return
        self._mgr.UnInit()
        self.appconfig.save()
        event.Skip()

    def OnImportProject(self, event):
        dlg = wx.FileDialog(
            self, message="Choose a project file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="Project file (project.xml)|*.json",
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR
        )

        if dlg.ShowModal() == wx.ID_OK:
            projectpath = dlg.GetPath()
            prjdir = os.path.dirname(projectpath)
            self.OpenProject(prjdir)

    def onOpenProject(self, evt):
        index = evt.Id - ID_FirstLastestProject
        projectdir = self.__fast_open_projects_list[index]
        self.OpenProject(projectdir)
        self.__onNormalState()

    def add_new_notebook_page(self, ctrl,page_name):
        return self.notebook.AddPage(ctrl,page_name)

    def load_script_model(self,model):
        filename = os.path.basename(model.script_file_path)
        page_count = self.notebook.GetPageCount()
        page_exists = False
        page_stc = None
        for idx in range(page_count):
            txt = self.notebook.GetPageText(idx)
            if filename == txt:
                self.notebook.SetSelection(idx)
                page_stc = self.notebook.GetPage(idx)
                page_exists = True
                break
        if page_exists is False:
            page_stc = PythonSTC(self.notebook,wx.ID_ANY)
            idx = self.add_new_notebook_page(page_stc,filename)
            self.notebook.SetSelection(idx)
        return page_stc


    def DoUpdate(self):

        self._mgr.Update()
        self.Refresh()

    def OnEraseBackground(self, event):

        event.Skip()

    def OnSize(self, event):

        event.Skip()

    def OnUpdateUI(self, event):
        pass


    def GetStartPosition(self):

        x = 20
        pt = self.ClientToScreen(wx.Point(0, 0))
        return wx.Point(pt.x + x, pt.y + x)

    def OnExit(self, event):

        self.Close(True)

    def OnAbout(self, event):

        msg = "This Is The About Dialog Of G1X Sim Desk.\n\n" + \
              "Author: Kevin Xu @ 25 March 2023\n\n" + \
              "Please Report Any Bug/Requests Of Improvements\n" + \
              "To Me At The Following Adresses:\n\n" + \
              "xuf@bsci.com\n" + \
              "Welcome To G1X Sim Desk " + constant.APPVERSION + "!!"

        dlg = wx.MessageDialog(self, msg, "G1X Simulator Desktop About",
                               wx.OK | wx.ICON_INFORMATION)

        dlg.ShowModal()
        dlg.Destroy()

    def assignProject(self, projectmodel):
        self.projecttree.assignProject(projectmodel)
        self.propertygridpanel.assignProject(projectmodel)
        self.active_project.console = self.console

    def OnNewProject(self, event):
        if self.__Close_Active_Project():
            newwizard = NPW(self)
            if newwizard.run():
                projectname, projectdir = newwizard.getProjectName(), newwizard.getProjectDir()
                if not os.path.exists(os.path.join(projectdir, projectname)):
                    self.active_project = Project(projectname)
                    self.active_project.saveDefaultPerspective(self._mgr.SavePerspective())
                    self.assignProject(self.active_project)
                    self.active_project.create(projectname, projectdir)
                    self.active_project.setDirty()
                    self.tb.EnableTool(ID_SaveProject, False)
                    self.tb.EnableTool(ID_StartTest, True)
                    self.tb.EnableTool(ID_StopTest, False)
                    self._mgr.LoadPerspective(self.original_perspective)
                    self.SetTitle("GX1 Simulator Desktop --" + self.active_project.getLabel())
                else:
                    wx.MessageBox("The project already exist, please check!")

    def OpenProject(self, projectdir):
        if self.__Close_Active_Project():
            projectname = os.path.basename(projectdir)
            self.active_project = Project(projectname)
            self.assignProject(self.active_project)
            self.active_project.open(projectdir)
            defaultperspecitve = self.active_project.getDefaultPerspective()

            if defaultperspecitve:
                self._mgr.LoadPerspective(defaultperspecitve)
            else:
                self._mgr.LoadPerspective(self.original_perspective)

            self.tb.EnableTool(ID_StartTest, True)
            self.tb.EnableTool(ID_StopTest, False)
            self.tb.EnableTool(ID_SaveProject, False)
            self.SetTitle("GX1 Simulator Desktop --" + self.active_project.getLabel())
            # self.__onNormalState()

    def __Close_Active_Project(self):

        if self.active_project is None:
            return True
        dlg = wx.MessageDialog(self, 'Please Confirm to Save the project, Yes to Change, No not save the change ',
                               'Confirm to Close',
                               # wx.OK | wx.ICON_INFORMATION
                               wx.YES_NO | wx.ICON_INFORMATION | wx.CANCEL
                               )
        result = dlg.ShowModal()

        if result == wx.ID_CANCEL:
            return False
        if result == wx.ID_YES:
            perspective_default = self._mgr.SavePerspective()
            self.active_project.saveDefaultPerspective(perspective_default)
            self.active_project.save()
            self.active_project.close()
        elif result == wx.ID_NO:
            self.active_project.close()
        self.append_projects_to_fast_open([self.active_project.project_dir])
        return True

    def ShowPageInCentrePane(self, panel_label):
        panel = self._mgr.GetPaneByName(panel_label)
        if panel is not None:
            notebooks = self._mgr.GetNotebooks()
            is_in_notebook = False
            if len(notebooks) != 0:
                for notebook in notebooks:
                    pagecount = notebook.GetPageCount()
                    for i in range(pagecount):
                        page = notebook.GetPage(i)
                        if page == panel.window:
                            notebook.SetSelection(i)
                            is_in_notebook = True
                            break
            if is_in_notebook is False:
                self._mgr.DetachPane(panel.window)
                self.add_to_center_panel(panel.window)

    def CreateConsoleCtrl(self):
        self.console = Console(self)
        return self.console

    def CreateProjectTreeCtrl(self):

        self.projecttree = ProjectTreeCtrl(self, -1, wx.Point(0, 0), wx.Size(200, 250),
                                           wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
        return self.projecttree

    def CreatePropertyGrid(self):
        self.propertygridpanel = PropertyGridPanel(self, wx.ID_ANY)

        return self.propertygridpanel

    def CreateNotebook(self):
        client_size = self.GetClientSize()
        ctrl = aui.AuiNotebook(self, -1, wx.Point(client_size.x, client_size.y), wx.Size(430, 200))

        arts = [aui.AuiDefaultTabArt, aui.AuiSimpleTabArt, aui.VC71TabArt, aui.FF2TabArt,
                aui.VC8TabArt, aui.ChromeTabArt]
        self.screen_window = MyScrolledPanel(self)
        self.feature_detection_panel = ImagePanel(self)
        ctrl.AddPage(self.screen_window, "Screen")
        ctrl.AddPage(self.feature_detection_panel, "Image Features")
        SimDeskContext().set_image_feature_panel(self.feature_detection_panel)
        # create the notebook off-window to avoid flicker
        self.notebook = ctrl
        return ctrl

#
