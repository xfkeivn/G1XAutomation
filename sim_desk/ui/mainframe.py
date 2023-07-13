"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: mainframe.py
@time: 2023/3/26 10:58
@desc:
"""
import os

import executor_context
import setting
import wx
from BackPlaneSimulator import BackPlaneSimulator as Bps
from gx_communication.comport import SERIAL_PIPE, SERIAL_PORT
from sim_desk import constant
from sim_desk.mgr.appconfig import AppConfig
from sim_desk.models.Project import Project
from sim_desk.models.TreeModel import *
from sim_desk.ui.console import Console
from sim_desk.ui.ImagePanel import *
from sim_desk.ui.progressdlg import ProgressObserver
from sim_desk.ui.project_tree import ProjectTreeCtrl
from sim_desk.ui.propertygrid import PropertyGridPanel
from sim_desk.ui.screenframe import MyScrolledPanel
from sim_desk.ui.script_editor import PythonSTC
from sim_desk.ui.wizards.NewProjectWizard import NewProjectWizard as Npw

try:
    from agw import aui
except ImportError:  # if it's not there locally, try the wxPython lib.
    import wx.lib.agw.aui as aui

from sim_desk.ui import images, statusbar
from squish.squish_lib import *
from squish.squish_proxy import *
from utils.utilities import get_python_exe_path, get_screen_shot_home_folder

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
ID_latest_Project = wx.ID_HIGHEST + 40
NOTE_PAGE_NAME_IMAGE_FEATURE = "Image Features"


class MainFrame(wx.Frame):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        title="",
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER,
    ):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        SimDeskContext().set_main_frame(self)
        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.SetIcon(images.main.GetIcon())
        self.sb = statusbar.StatusBar(self)
        self.SetStatusBar(self.sb)
        self.screen_window = None
        self.process = None
        self.notebook: aui.AuiNotebook = None
        self.property_grid_panel = None
        self.original_perspective = None
        self.file_menu = None
        self.screen_image = None
        self.tb = None
        self.build_panes()
        self.create_menubar()
        self.bind_events()
        self.active_project = None
        self.squish_runner = None
        self.__fast_open_projects_list = []
        self.appconfig = AppConfig()
        self.SetTitle("G1X Simulator Control Desk")
        self.feature_detection_panel = None
        self.append_projects_to_fast_open(
            self.appconfig.getProjectHistoryList()
        )
        # when the ui is all done, set the IO to Console
        self.bps = Bps()
        self.squish_started = False
        self.squish_runner = None
        self.init()
        self._mgr.Update()
        executor_context.ExecutorContext().set_gui_context(self)
        self.on_save_project(None)
        self.progress_dialog = None

    def init(self):
        project_histories = self.appconfig.getProjectHistoryList()
        # Open Latest Project
        if len(project_histories) > 0:
            last_project_dir = project_histories[-1]
            self.open_project(last_project_dir)
        self.__on_normal_state()
        if self.active_project is None:
            self.tb.EnableTool(ID_StartTest, False)
            self.tb.EnableTool(ID_StopTest, False)

    def create_menubar(self):
        mb = wx.MenuBar()
        self.file_menu = wx.Menu()
        file_menu = self.file_menu
        file_menu.Append(ID_NewProject, "New")
        file_menu.Append(ID_ImportProject, "Import")
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

    def build_panes(self):
        self.SetMinSize(wx.Size(400, 300))
        tb1 = aui.AuiToolBar(
            self,
            -1,
            wx.DefaultPosition,
            wx.DefaultSize,
            agwStyle=aui.AUI_TB_DEFAULT_STYLE | aui.AUI_TB_OVERFLOW,
        )
        tb1.AddSimpleTool(
            ID_NewProject,
            "New Project",
            images.NewProject.GetBitmap(),
            short_help_string="New Project",
        )
        tb1.AddSimpleTool(
            ID_SaveProject,
            "Save Project",
            images.save_edit.GetBitmap(),
            short_help_string="Save Project",
        )
        tb1.AddSimpleTool(
            ID_ImportProject,
            "Import Project",
            images.Import.GetBitmap(),
            short_help_string="Import Project",
        )
        tb1.AddSeparator()
        tb1.AddSimpleTool(
            ID_ViewProjects,
            "ViewProject",
            images.viewproj.GetBitmap(),
            short_help_string="Show Project",
        )
        tb1.AddSimpleTool(
            ID_ViewProperties,
            "ViewProperties",
            images.viewprop.GetBitmap(),
            short_help_string="Show Properties",
        )
        tb1.AddSimpleTool(
            ID_ViewConsole,
            "ViewConsole",
            images.viewconsole.GetBitmap(),
            short_help_string="Show Console",
        )
        tb1.AddSeparator()
        tb1.AddSimpleTool(
            ID_StartTest,
            "StartTest",
            images.run.GetBitmap(),
            short_help_string="Start Manual Test",
        )
        tb1.AddSimpleTool(
            ID_StopTest,
            "StopTest",
            images.stop.GetBitmap(),
            short_help_string="Stop Manual Test",
        )
        tb1.AddSeparator()
        tb1.AddSimpleTool(
            ID_ScreenShot,
            "ScreenShot",
            images.camera.GetBitmap(),
            short_help_string="Take Screenshot",
        )
        tb1.Realize()
        tb1.AddSimpleTool(
            ID_Robot,
            "Start RIDE",
            images.robot.GetBitmap(),
            short_help_string="Start RIDE",
        )
        tb1.Realize()
        self.tb = tb1
        self._mgr.AddPane(
            self.create_project_treectrl(),
            aui.AuiPaneInfo()
            .Name("ProjectExplorer")
            .Caption("Project Explorer")
            .Left()
            .Layer(2)
            .MinimizeButton(True)
            .Icon(images.viewproj.GetBitmap()),
        )
        self._mgr.AddPane(
            self.create_property_grid(),
            aui.AuiPaneInfo()
            .Name("Properties")
            .Caption("Properties")
            .Left()
            .Layer(2)
            .Position(1)
            .MinimizeButton(True)
            .Icon(images.viewprop.GetBitmap()),
        )
        self._mgr.AddPane(
            self.create_console_ctrl(),
            aui.AuiPaneInfo()
            .Name("Console")
            .Caption("Console")
            .Bottom()
            .MinimizeButton(True)
            .Icon(images.viewconsole.GetBitmap()),
        )

        self._mgr.AddPane(
            self.create_notebook(),
            aui.AuiPaneInfo()
            .Name("Desk")
            .Caption("Desk")
            .Centre()
            .CloseButton(False)
            .CaptionVisible(False),
        )
        self._mgr.AddPane(
            tb1,
            aui.AuiPaneInfo()
            .Name("tb1")
            .Caption("Big Toolbar")
            .ToolbarPane()
            .Top(),
        )
        self.original_perspective = self._mgr.SavePerspective()

    def clear_log(self, evt):
        self.console.clear()

    def append_projects_to_fast_open(self, project_dir_list):
        for project_dir in project_dir_list:
            project_dir = os.path.normpath(project_dir)
            if project_dir not in self.__fast_open_projects_list:
                if len(self.__fast_open_projects_list) == 0:
                    self.file_menu.AppendSeparator()
                self.file_menu.Append(
                    ID_latest_Project + len(self.__fast_open_projects_list),
                    os.path.basename(project_dir),
                )
                self.__fast_open_projects_list.append(project_dir)

    def add_to_center_panel(self, window):
        self._mgr.AddPane(
            window,
            aui.AuiPaneInfo()
            .Name(str(window.getLabel()))
            .Centre()
            .MaximizeButton(True)
            .PaneBorder(True)
            .Caption(str(window.getLabel())),
        )
        self._mgr.Update()
        return window

    def bind_events(self):
        self.Bind(wx.EVT_MENU, self.on_new_project, id=ID_NewProject)
        self.Bind(wx.EVT_MENU, self.on_save_project, id=ID_SaveProject)
        self.Bind(wx.EVT_MENU, self.on_import_project, id=ID_ImportProject)
        self.Bind(wx.EVT_MENU, self.on_screen_shot, id=ID_ScreenShot)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(
            EVT_MODEL_DIRTYSTATE_CHANGE_EVENT, self.on_dirty_state_changed
        )
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(aui.EVT_AUI_PANE_CLOSE, self.on_pane_close)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.On_notebook_page_close)
        self.Bind(
            wx.EVT_MENU_RANGE,
            self.on_open_project,
            id=ID_latest_Project,
            id2=ID_latest_Project + 7,
        )
        self.Bind(wx.EVT_MENU, self.on_start, id=ID_StartTest)
        self.Bind(wx.EVT_MENU, self.on_stop, id=ID_StopTest)
        self.Bind(wx.EVT_MENU, self.on_start_robot, id=ID_Robot)
        self.Bind(wx.EVT_MENU, self.clear_log, id=ID_ClearLog)
        self.Bind(wx.EVT_MENU, self.show_pane, id=ID_ViewProperties)
        self.Bind(wx.EVT_MENU, self.show_pane, id=ID_ViewConsole)
        self.Bind(wx.EVT_MENU, self.show_pane, id=ID_ViewProjects)

    def __del__(self):
        pass

    @property
    def squisher(self):
        return self.squish_runner

    def on_start_robot(self, evt):
        # Activate the virtual environment
        if setting.prod is False:
            venv_path = os.path.join(os.path.dirname(__file__), "../../venv")
            activate_script = os.path.join(
                venv_path, "Scripts", "activate.bat"
            )
            subprocess.call(activate_script, shell=True)
            # Start the subprocess using the virtual environment's Python interpreter
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
            subprocess.Popen(
                [python_path, os.path.join(venv_path, "Scripts", "ride.py")]
            )
        else:
            venv_path = os.path.join(
                os.path.dirname(__file__), "../../../python3"
            )
            python_path = os.path.join(venv_path, "python.exe")
            subprocess.Popen(
                [python_path, os.path.join(venv_path, "Scripts", "ride.py")]
            )

    def on_start(self, evt):
        # silently save the project
        self.on_save_project(None)

        communication_type = self.active_project.getPropertyByName(
            "CommunicationType"
        ).getStringValue()
        if communication_type == "PIPE":
            ctype = SERIAL_PIPE
            pipe_name = self.active_project.getPropertyByName(
                "PipeName"
            ).getStringValue()
            com_port_val = pipe_name
        else:
            com_port_val = self.active_project.getPropertyByName(
                "COM"
            ).getStringValue()
            ctype = SERIAL_PORT
        logger.info("Start communication ..")
        squish_result = True
        communication_result = self.bps.start(com_port_val, ctype)
        if communication_result is True:
            logger.info("Start communication successfully")
        else:
            logger.info("Start communication failed")
        enabled_squish = (
            self.active_project.squish_container.getPropertyByName("Enabled")
        )
        if communication_result and enabled_squish.getStringValue() == "True":
            dlg = wx.MessageDialog(
                self,
                "Start Squish, click YES, Otherwise click NO.\n"
                "To use squish, make sure Squish is properly installed and set\n"
                "GX1 GUI application should be started before you click YES!\n"
                "To use it with VM, stop the stest and then the vm will show Pipe error, you need to \n"
                "Close and start the VM again, restart VM will not work ",
                "Confirm to start",
                # wx.OK | wx.ICON_INFORMATION
                wx.YES_NO | wx.ICON_INFORMATION,
            )
            is_start_squish = dlg.ShowModal()
            if is_start_squish == wx.ID_YES:
                while True:
                    logger.info("Start Squish connection ..")
                    ip_prop = (
                        self.active_project.squish_container.getPropertyByName(
                            "IP"
                        )
                    )
                    aut_prop = (
                        self.active_project.squish_container.getPropertyByName(
                            "AUT"
                        )
                    )
                    private_key = (
                        self.active_project.squish_container.getPropertyByName(
                            "PrivateKey"
                        )
                    )
                    squishHomeDirProp = (
                        self.active_project.squish_container.getPropertyByName(
                            "SquishHome"
                        )
                    )
                    if (
                        ip_prop
                        and aut_prop
                        and squishHomeDirProp
                        and private_key
                    ):
                        ip_address = ip_prop.getStringValue()
                        aut_name = aut_prop.getStringValue()
                        private_key_file = private_key.getStringValue()
                        squishHomeDir = squishHomeDirProp.getStringValue()
                        if not os.path.exists(private_key_file):
                            logger.error("The ssh private not exists")
                            squish_result = False
                            break
                        if not os.path.exists(squishHomeDir):
                            logger.error(
                                "The squish install directory not exist"
                            )
                            squish_result = False
                            break

                        self.squish_runner = SquishProxy(
                            squishHomeDir,
                            ip_address,
                            private_key_file,
                            aut_name,
                        )
                        squish_result = (
                            self.squish_runner.start_squish_server()
                        )
                        if squish_result is True:
                            self.squish_runner.create_proxy()
                            squish_result = self.squish_runner.connect()
                            if squish_result:
                                self.active_project.squish_runner = (
                                    self.squish_runner
                                )
                                self.screen_window.start()
                            else:
                                logger.error("Connect to Squish hooker failed")
                                squish_result = False
                                break
                        else:
                            logger.error(
                                "Start squish pyro server start failed"
                            )
                            squish_result = False
                            break
                    else:
                        squish_result = False
                        logger.error("The property of squish setting failed")
                        break
                    break
        if communication_result is True and squish_result is True:
            self.SetWindowStyle(
                wx.CAPTION
                | wx.MAXIMIZE_BOX
                | wx.MINIMIZE_BOX
                | wx.RESIZE_BORDER
            )
            self.active_project.scenario_py_container.start_all_scenarios()
            self.__on_runtime_state()

    def __on_runtime_state(self):
        if self.active_project:
            self.active_project.set_model_status(TREEMODEL_STATUS_RUNTIME)
        tool_count = self.tb.GetToolCount()
        for tool_index in range(tool_count):
            tool = self.tb.FindToolByIndex(tool_index)
            self.tb.EnableTool(tool.GetId(), False)
        self.tb.EnableTool(ID_ScreenShot, True)
        self.tb.EnableTool(ID_ClearLog, True)
        self.tb.EnableTool(ID_ViewProperties, True)
        self.tb.EnableTool(ID_ViewConsole, True)
        self.tb.EnableTool(ID_ViewProjects, True)
        self.tb.EnableTool(ID_StopTest, True)
        self.sb.set_text1("Project is running")
        self.GetMenuBar().EnableTop(0, False)
        self.GetMenuBar().EnableTop(1, False)
        self.GetMenuBar().EnableTop(2, False)
        self.tb.Realize()

    def __on_normal_state(self):
        if self.active_project:
            self.active_project.set_model_status(TREEMODEL_STATUS_NORMAL)
            tool_count = self.tb.GetToolCount()
            for tool_index in range(tool_count):
                tool = self.tb.FindToolByIndex(tool_index)
                self.tb.EnableTool(tool.GetId(), True)
                if tool.GetId() == ID_SaveProject:
                    self.tb.EnableTool(
                        ID_SaveProject, self.active_project.isDirty()
                    )
        self.tb.EnableTool(ID_StopTest, False)
        self.sb.set_text1("Project is Editing")
        self.sb.set_status(TREEMODEL_STATUS_NORMAL)
        self.GetMenuBar().EnableTop(0, True)
        self.GetMenuBar().EnableTop(1, True)
        self.GetMenuBar().EnableTop(2, True)
        self.tb.EnableTool(ID_ScreenShot, False)
        self.tb.Realize()

    def on_stop(self, evt):
        self.active_project.scenario_py_container.stop_all_scenarios()
        self.screen_window.stop()
        if self.bps.stop():
            self.__on_normal_state()
            self.SetWindowStyle(wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER)
        try:
            if self.squish_runner:
                self.squish_runner.disconnect()
                self.squish_runner.stop_squish_server()
        except Exception as err:
            logger.warn("There is an error during stopping squisher")
        finally:
            self.squish_started = False
        self.tb.Realize()

    def on_screen_shot(self, evt):
        dirname = os.path.dirname(__file__)
        screenshot_folder = get_screen_shot_home_folder()
        if not os.path.exists(screenshot_folder):
            os.makedirs(screenshot_folder)
        if self.squish_runner:
            name = time.strftime("%Y%b%d_%H_%M_%S.png", time.localtime())
            full_path_name = os.path.join(screenshot_folder, name)
            self.squish_runner.screen_save(full_path_name)
            self.active_project.image_processing_container.import_to_asset(
                full_path_name
            )
            # load it

    def on_pane_close(self, evt):
        # print "close pane"
        evt.Skip()

    def On_notebook_page_close(self, evt):
        # print "close pane"
        page_index = evt.GetSelection()
        page = self.notebook.GetPage(page_index)
        if isinstance(page, PythonSTC):
            page.script_model.save()
        evt.Skip()

    def show_pane(self, evt):
        id = evt.Id
        if id == ID_ViewProjects:
            self._mgr.ShowPane(
                self._mgr.GetPaneByName("ProjectExplorer").window, True
            )
        elif id == ID_ViewConsole:
            self._mgr.ShowPane(self._mgr.GetPaneByName("Console").window, True)
        elif id == ID_ViewProperties:
            self._mgr.ShowPane(
                self._mgr.GetPaneByName("Properties").window, True
            )

    def remove_page(self, name):
        panel = self._mgr.GetPaneByName(name)
        if panel:
            self._mgr.ClosePane(panel)
            self._mgr.DetachPane(panel.window)
            self._mgr.Update()

    def on_dirty_state_changed(self, evt):
        self.tb.EnableTool(ID_SaveProject, evt.dirtystate)
        self.tb.Realize()

    def on_save_project(self, evt):
        if self.active_project:
            perspective_default = self._mgr.SavePerspective()
            self.active_project.saveDefaultPerspective(perspective_default)
            self.active_project.save()
            self.tb.EnableTool(ID_SaveProject, False)
            self.tb.Realize()

    def on_close(self, event):
        if self.__close_active_project() is False:
            event.Veto()
            return
        self._mgr.UnInit()
        self.appconfig.save()
        event.Skip()

    def on_import_project(self, event):
        dlg = wx.FileDialog(
            self,
            message="Choose a project file",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard="Project file (project.xml)|*.json",
            style=wx.FD_OPEN | wx.FD_CHANGE_DIR,
        )

        if dlg.ShowModal() == wx.ID_OK:
            projectpath = dlg.GetPath()
            prjdir = os.path.dirname(projectpath)
            self.open_project(prjdir)

    def on_open_project(self, evt):
        index = evt.Id - ID_latest_Project
        projectdir = self.__fast_open_projects_list[index]
        self.open_project(projectdir)
        self.__on_normal_state()

    def add_new_notebook_page(self, ctrl, page_name):
        self.notebook.AddPage(ctrl, page_name)
        return self.notebook.GetPageCount() - 1

    def show_feature_annotation_page(self):
        page_count = self.notebook.GetPageCount()

        for idx in range(page_count):
            txt = self.notebook.GetPageText(idx)
            if NOTE_PAGE_NAME_IMAGE_FEATURE == txt:
                self.notebook.SetSelection(idx)
                page_stc = self.notebook.GetPage(idx)
                page_exists = True
                break

    def unload_script_model(self, model):
        filename = os.path.basename(model.script_file_path)
        page_count = self.notebook.GetPageCount()
        for idx in range(page_count):
            txt = self.notebook.GetPageText(idx)
            if filename == txt:
                self.notebook.RemovePage(idx)
                break

    def load_script_model(self, model):
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
            page_stc = PythonSTC(self.notebook, wx.ID_ANY)
            page_stc.script_model = model
            idx = self.add_new_notebook_page(page_stc, filename)
            self.notebook.SetSelection(idx)
        return page_stc

    def do_update(self):
        self._mgr.Update()
        self.Refresh()

    def on_erase_background(self, event):
        event.Skip()

    def on_size(self, event):
        event.Skip()

    def on_update_ui(self, event):
        pass

    def get_start_position(self):
        x = 20
        pt = self.ClientToScreen(wx.Point(0, 0))
        return wx.Point(pt.x + x, pt.y + x)

    def on_exit(self, event):
        self.Close(True)

    def on_about(self, event):
        msg = (
            "This Is The About Dialog Of G1X Sim Desk.\n\n"
            + "Author: Kevin Xu @ 25 March 2023\n\n"
            + "Please Report Any Bug/Requests Of Improvements\n"
            + "To Me At The Following Adresses:\n\n"
            + "xuf@bsci.com\n"
            + "Welcome To G1X Sim Desk "
            + constant.APPVERSION
            + "!!"
        )

        dlg = wx.MessageDialog(
            self,
            msg,
            "G1X Simulator Desktop About",
            wx.OK | wx.ICON_INFORMATION,
        )

        dlg.ShowModal()
        dlg.Destroy()

    def assign_project(self, projectmodel):
        self.projecttree.assign_project(projectmodel)
        self.property_grid_panel.assign_project(projectmodel)
        self.active_project.console = self.console

    def on_new_project(self, event):
        if self.__close_active_project():
            newwizard = Npw(self)
            if newwizard.run():
                projectname, projectdir = (
                    newwizard.getProjectName(),
                    newwizard.getProjectDir(),
                )
                if not os.path.exists(os.path.join(projectdir, projectname)):
                    self.active_project = Project(projectname)
                    self.active_project.saveDefaultPerspective(
                        self._mgr.SavePerspective()
                    )
                    self.assign_project(self.active_project)
                    self.active_project.create(projectname, projectdir)
                    self.active_project.setDirty()
                    self.tb.EnableTool(ID_SaveProject, False)
                    self.tb.EnableTool(ID_StartTest, True)
                    self.tb.EnableTool(ID_StopTest, False)
                    self._mgr.LoadPerspective(self.original_perspective)
                    self.SetTitle(
                        "DVTFront for GX1 --" + self.active_project.getLabel()
                    )
                else:
                    wx.MessageBox("The project already exist, please check!")

    def open_project(self, projectdir):
        if self.__close_active_project():
            projectname = os.path.basename(projectdir)
            self.active_project = Project(projectname)
            self.assign_project(self.active_project)
            self.active_project.open(projectdir)
            defaultperspecitve = self.active_project.getDefaultPerspective()

            if defaultperspecitve:
                self._mgr.LoadPerspective(defaultperspecitve)
            else:
                self._mgr.LoadPerspective(self.original_perspective)

            self.tb.EnableTool(ID_StartTest, True)
            self.tb.EnableTool(ID_StopTest, False)
            self.tb.EnableTool(ID_SaveProject, False)
            self.SetTitle(
                "GX1 Simulator Desktop --" + self.active_project.getLabel()
            )
            # self.__onNormalState()

    def __close_active_project(self):
        if self.active_project is None:
            return True
        dlg = wx.MessageDialog(
            self,
            "Please Confirm to Save the project, Yes to Change, No not save the change ",
            "Confirm to Close",
            # wx.OK | wx.ICON_INFORMATION
            wx.YES_NO | wx.ICON_INFORMATION | wx.CANCEL,
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

    def show_page_in_centre_pane(self, panel_label):
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

    def create_console_ctrl(self):
        self.console = Console(self)
        return self.console

    def create_project_treectrl(self):
        self.projecttree = ProjectTreeCtrl(
            self,
            -1,
            wx.Point(0, 0),
            wx.Size(200, 250),
            wx.TR_DEFAULT_STYLE | wx.NO_BORDER,
        )
        return self.projecttree

    def create_property_grid(self):
        self.property_grid_panel = PropertyGridPanel(self, wx.ID_ANY)

        return self.property_grid_panel

    def create_notebook(self):
        client_size = self.GetClientSize()
        ctrl = aui.AuiNotebook(
            self, -1, wx.Point(client_size.x, client_size.y), wx.Size(430, 200)
        )

        arts = [
            aui.AuiDefaultTabArt,
            aui.AuiSimpleTabArt,
            aui.VC71TabArt,
            aui.FF2TabArt,
            aui.VC8TabArt,
            aui.ChromeTabArt,
        ]
        self.screen_window = MyScrolledPanel(self)
        self.feature_detection_panel = ImagePanel(self)
        ctrl.AddPage(self.screen_window, "Screen")
        ctrl.AddPage(
            self.feature_detection_panel, NOTE_PAGE_NAME_IMAGE_FEATURE
        )
        SimDeskContext().set_image_feature_panel(self.feature_detection_panel)
        # create the notebook off-window to avoid flicker
        self.notebook = ctrl
        return ctrl


#
