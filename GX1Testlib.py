import threading
from sim_desk.models.Project import Project
from BackPlaneSimulator import BackPlaneSimulator as BPS
from squish.squish_lib import SquishTest
from importlib import reload
from sim_desk.mgr.appconfig import AppConfig
import sys
reload(sys)
import datetime
import time
import os
import io

curfiledir = os.path.dirname(__file__)
sys.path.append(os.path.dirname(curfiledir))
from robot import utils
from robot.libraries.BuiltIn import BuiltIn

from robot.api import logger


class CommandListener(object):
    def __init__(self):
        self.ml_stringio = None
        self.ml_file = None
        self.message_log_lock = threading.Lock()
        self.current_log_filename = None
        self.command_log_folder = "Command_Logs"
        self.is_log_inited = False
        self.command_filters = []

    def _correctfilename(self, filename):
        special_chrs = r'\/:*?"<>|'
        modified_filename = ''
        for c in filename:
            if c not in special_chrs:
                modified_filename += c
        return modified_filename

    def exclude_command_code(self,command_code):
        self.command_filters.append(command_code)

    def include_command_code(self,command_code):
        self.command_filters.remove(command_code)

    def open_message_log(self):
        """
        log the command message in to a log file for tracing during the test
        :return:
        """
        self.message_log_lock.acquire()
        if not self.is_log_inited:
            self.ml_stringio = io.StringIO()
            variables = BuiltIn().get_variables()
            suite_name = variables['${SUITE_NAME}']
            logfile_basename = self._correctfilename("%s.log" % (suite_name + "_" + variables['${TEST NAME}']))
            out_put_dir = variables['${OUTPUT_DIR}']
            logfile_dir = os.path.join(out_put_dir, self.command_log_folder)
            if not os.path.exists(logfile_dir):
                os.mkdir(logfile_dir)
            self.current_log_filename = os.path.join(logfile_dir, logfile_basename)
            with open(self.current_log_filename, "a") as self.ml_file:
                self.ml_file.close()
            logger.info('Command Message Log setup, log output directory is %s' % self.current_log_filename)
            self.is_log_inited = True
        self.message_log_lock.release()

    def close_message_log(self):
        """
        Arguments:
            None

        Return Value:
            None
         See `Open Message Log` for an explanation on how to log command data. Must be called to flush the log file

        """

        if self.is_log_inited:
            self.message_log_lock.acquire()
            content = self.ml_stringio.getvalue()
            if os.path.exists(self.current_log_filename):
                with open(self.current_log_filename, "a") as self.ml_file:
                    self.ml_file.write(content)
                    self.ml_file.close()
            self.ml_stringio.close()
            logger.info("The message log is closed")
            self.is_log_inited = False
            self.message_log_lock.release()
        else:
            logger.warn("The log is not initiated when trying to closed")

    def __message_logging(self, msg):
        # t1 = time.clock()
        if self.is_log_inited:
            self.message_log_lock.acquire()
            self.ml_stringio.write(msg+"\n")
            self.message_log_lock.release()

    def on_command_received(self,command):
        if command.data.u16_CommandCode in self.command_filters:
            return
        self.__message_logging(f'{command.time_ns//100000}:{command.sequence}:{command.data}')

    def on_command_responsed(self,response):
        if response.data.u16_ResponseCode - 1 in self.command_filters:
            return
        self.__message_logging(f'{response.time_ns//100000}:{response.sequence}:{response.data}')


class GX1Testlib(object):
    """
      Libaray for Test Automation Framework For GX1 system

      """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0'
    ROBOT_LISTENER_API_VERSION = 2

    # ====================================================================================================#
    #
    #    Internal Function Definition
    #
    # ====================================================================================================#

    def __init__(self, project_dir=None):
        """
        Initialize the Library.
        **This interface will not initialize the device and the test system  **
        Used Operate_Devices_All_Init to Initialize all devices and test system.

        The Library will load the current project file which contains all the information used for test scripts to run.
        This file can be created by GUI tool.

        Examples (use only one of these):

        | *Setting* | *Value*  | *Value*    | *Value* |
        | Library | TAFLib  | projectdir
        """
        logger.info("Project directory is %s" % project_dir)
        self.project_model = Project(None)
        self.project_dir = project_dir
        self.gx1_simulator = BPS()
        self.squish_tester = None

        self.command_listener = CommandListener()
        self.gx1_simulator.add_command_listener(self.command_listener)
        self.ROBOT_LIBRARY_LISTENER = self
        self.project_inited = False
        self.out_put_dir = None
        self.is_log_inited = False
        self.squish_name_mapping = dict()

    #####################################################################################################
    ################################listeners #####################################################################

    def _end_test(self, name, attrs):
        logger.info(f'Test {name} end.')
        self.command_listener.close_message_log()

    def _start_test(self, name, attrs):
        # BuiltIn().set_variable("${OUTPUT DIR}",self.projectmodel.getTestOutputDir())
        logger.info('Test %s started' % (name))
        self.command_listener.open_message_log()

    def _end_suite(self, name, attrs):
        logger.info('Suite %s end.' % (name))

    def _start_suite(self, name, attrs):
        # BuiltIn().set_variable("${OUTPUT DIR}",self.projectmodel.getTestOutputDir())
        logger.info('Suite %s started' % (name))

    def _close(self):
        """
        when this hook is called, the output.xml and other reports are not closed yet.
        :return:
        """
        pass

    def _embed_screenshot(self, path, width):
        link = utils.get_link_path(path, self._log_dir)
        logger.info('<a href="%s"><img src="%s" width="%s"></a>'
                    % (link, link, width), html=True)

    def _link_screenshot(self, path):
        link = utils.get_link_path(path, self._log_dir)
        logger.info("Screenshot saved to '<a href=\"%s\">%s</a>'."
                    % (link, path), html=True)

    def _get_obj_from_alias(self,alias):
        obj = self.squish_name_mapping.get(alias,None)
        if obj is None:
            raise Exception(f'There is no squish name {alias} in the name.py')
        return obj

    @property
    def _log_dir(self):
        variables = BuiltIn().get_variables()
        outdir = variables['${OUTPUTDIR}']
        log = variables['${LOGFILE}']
        log = os.path.dirname(log) if log != 'NONE' else '.'
        return os.path.normpath(os.path.join(outdir, log))

    def _get_screenshot_path(self, basename):
        directory = self._log_dir
        if basename.lower().endswith(('.png', '.png')):
            return os.path.join(directory, basename)
        index = 0
        while True:
            index += 1
            path = os.path.join(directory, "%s_%d.png" % (basename, index))
            if not os.path.exists(path):
                return path

    def __init_project(self):
        appconfig = AppConfig()
        last_open_project = appconfig.getProjectHistoryList()[-1]

        if self.project_dir is None:
            self.project_dir = last_open_project

        logger.info(f'Loading the project at {self.project_dir}')
        self.project_model.open(self.project_dir)
        ip_prop = self.project_model.squish_container.getPropertyByName("IP")
        aut_prop = self.project_model.squish_container.getPropertyByName("AUT")
        private_key = self.project_model.squish_container.getPropertyByName("PrivateKey")

        if ip_prop and aut_prop and private_key:
            ip_address = ip_prop.getStringValue()
            aut_name = aut_prop.getStringValue()
            private_key_file = private_key.getStringValue()
            self.squish_tester = SquishTest(ip_address, private_key_file, aut_name)
            logger.info(f'Squish Hook {ip_address}, {aut_name}, {private_key_file}')
            logger.info('%s has been loaded successfully' % self.project_model.getLabel())
        else:
            logger.error("Failed to init the project the project setting error")

    def init_test(self):
        """
        Description:
         This should be called before any test can started for GX1
        Arguments:

            None

        Return Value:

            None

        Examples:

        | init_test |

        """

        if not self.project_inited:
            self.__init_project()
            self.squish_name_mapping = self.project_model.squish_container.get_all_name_mapping()
            self.project_inited = True
            com_port_val = self.project_model.getPropertyByName("COM").getStringValue()
            result = self.gx1_simulator.start(com_port_val)
            if result:
                logger.info("GX1 Simulator is started")
            else:
                logger.error("GX1 Simulator failed to start")
                return

            result = self.squish_tester.connect()
            if result:
                logger.info("Squish tester is started")
            else:
                logger.error("Squish tester failed to start")
                return
        else:
            logger.warn("Project is already initialized")

    def close_test(self):
        """
        Description:
        Close the simulator and cleanup after the test is done
        exceptions.
        Arguments:
            None
        Return Value:
            None
        Examples:
        |close_test |

        """
        if self.project_inited is True:
            self.gx1_simulator.stop()
            logger.info("GX1 Simulator is stopped")
            self.squish_tester.disconnect()
            logger.info("Squish tester is stopped")
        else:
            logger.warn("The project is not initialized for testing ")
        self.project_inited = False

    def set_command_response(self,command_code,**response_data):
        return self.gx1_simulator.set_command_pending_response_by_parameters(command_code,**response_data)

    def clean_command_logging_queue(self):
        return self.gx1_simulator.clean_logged_command_queue()

    def find_logged_commands(self,command_code, start_seq=-1,**kwargs):
        return self.gx1_simulator.find_logged_command(command_code,start_seq,**kwargs)

    def screen_shot(self, embedded_image_to_report=True):

        """
        Capture the image from Screen and embedded  the image captured to the report
        :param embedded_image_to_report: whether the image should be embedded into report
        :return: the image file location
        """
        basename = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.png')
        screenshot_name = self._get_screenshot_path(basename)
        self.squish_tester.screen_save(screenshot_name)
        if embedded_image_to_report in ["1", "TRUE",True]:
            self._embed_screenshot(screenshot_name, 400)
        return screenshot_name

    def list_drag(self, gobj, offset):
        """If object is applicable, allow to drag a list.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            offset (int): The direction and length to drag in pixels.

        """
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_tester.list_drag(gobj,offset)

    def mouse_tap(self, gobj):
        """If object is applicable, perform a touch tap by passing in the Squish object reference.

        See `squishtest.tapObject`

        Args:
            gobj (dict): A dictionary containing the Squish object details

        """
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_tester.mouse_tap(gobj)

    def mouse_wheel(self, gobj, steps):
        """If object is applicable, this function performs a mouse wheel operation,
        emulating rotation of the vertical wheel of a mouse.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            steps (int): number of ticks to move the mouse wheel.

        """
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_tester.mouse_wheel(gobj,steps)

    def mouse_wheel_screen(self, x, y, steps):
        """If the Squish object exist, this function will perform a mouse wheel scroll
        operation on all scrollable objects on the screen. The number of ticks to scroll
        can only be 1 or -1.

        Args:
            steps (int): an integer number, if > 0, ticks to scroll is one. Otherwise is minus one
            x (int): position but not in use.
            y (int): position but not in use.

        """
        return self.squish_tester.mouse_wheel_screen(x,y,steps)

    def long_mouse_drag(self, gobj, steps):
        """If object is applicable, this function will produce a mouse drag operation with a fixed delay of
        about one second between pressing the mouse button and starting to move the mouse cursor.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            steps (int): pixels to drag.

        """
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_tester.long_mouse_drag(gobj,steps)

    def mouse_click(self, gobj):
        """If object is applicable, perform a mouse click by passing in the Squish object reference.

        See `squishtest.mouseClick`

        Args:
            gobj (dict): A dictionary containing the Squish object details.

        """
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_tester.mouse_click(gobj)

    def mouse_xy(self, x, y):
        """Perform a mouse click on the active window.

        Args:
            x (int): the pixels on the x axis.
            y (int): the pixels on the y axis.

        """
        return self.squish_tester.mouse_xy(x,y)

    def long_mouse_click(self, gobj, x, y):
        """Perform a long mouse click on the active window.

        Args:
            x (int): the pixels on the x axis.
            y (int): the pixels on the y axis.

        """
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_tester.long_mouse_click(gobj,x,y)


if __name__ == "__main__":
    gx1_testlib = GX1Testlib()
    gx1_testlib.init_test()
    time.sleep(1)
    gx1_testlib.mouse_click("OneTouch")
    time.sleep(10)

    #gx1_testlib.command_listener.open_message_log()
    #gx1_testlib.screen_shot(1)

    gx1_testlib.close_test()