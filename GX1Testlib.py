"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: GX1Testlib.py
@time: 2023/3/25 20:34
@desc:
"""
import sys
import threading
import uuid
from importlib import reload

from PIL import Image

from BackPlaneSimulator import BackPlaneSimulator as BPS
from executor_context import ExecutorContext
from sim_desk.mgr.appconfig import AppConfig
from sim_desk.models.Project import Project
from squish.squish_proxy import SquishProxy
from verifier.ocr import TessertOCR
from verifier.p2p_image_compare import P2PImageCompare

reload(sys)
import datetime
import io
import os
import time

curfiledir = os.path.dirname(__file__)
sys.path.append(os.path.dirname(curfiledir))
from robot import utils
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.Dialogs import *

from gx_communication.comport import *
from utils import logger
from utils.singleton import Singleton


def correct_filename(filename):
    special_chrs = r'\/:*?"<>|'
    return "".join(c for c in filename if c not in special_chrs)


class CommandListener(metaclass=Singleton):
    def __init__(self, strftime_dir=None):
        self.ml_stringio = None
        self.ml_file = None
        self.message_log_lock = threading.Lock()
        self.current_log_filename = None
        self.command_log_folder = "Command_Logs"
        self.is_log_inited = False
        self.command_filters = []
        self.strftime_dir = strftime_dir or datetime.datetime.now().strftime(
            "%Y_%m_%d_%H_%M_%S"
        )

    def exclude_command_code(self, command_code):
        self.command_filters.append(command_code)

    def include_command_code(self, command_code):
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
            # suite_name = variables["${SUITE_NAME}"]
            logfile_basename = correct_filename(
                "%s.log" % variables["${TEST NAME}"]
            )
            out_put_dir = variables["${OUTPUT_DIR}"]
            logfile_dir = os.path.join(
                out_put_dir,
                self.strftime_dir,
                self.command_log_folder,
                # correct_filename(suite_name),
            )
            os.makedirs(logfile_dir, exist_ok=True)
            self.current_log_filename = os.path.join(
                logfile_dir, logfile_basename
            )
            with open(self.current_log_filename, "a") as self.ml_file:
                self.ml_file.close()
            logger.info(
                "Command Message Log setup, log output directory is %s"
                % self.current_log_filename
            )
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
            self.ml_stringio.write(msg + "\n")
            self.message_log_lock.release()

    def on_command_received(self, command):
        if command.data.u16_CommandCode in self.command_filters:
            return
        self.__message_logging(
            f"{command.format_time}:{command.sequence}:{command.data}"
        )

    def on_command_responsed(self, response):
        if response.data.u16_ResponseCode - 1 in self.command_filters:
            return
        self.__message_logging(
            f"{response.format_time}:{response.sequence}:{response.data}"
        )


class GX1Testlib(metaclass=Singleton):
    """
    Library for Test Automation Framework For GX1 system

    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_VERSION = "1.0"
    ROBOT_LISTENER_API_VERSION = 2

    # ====================================================================================================#
    #
    #    Internal Function Definition
    #
    # ====================================================================================================#

    def __init__(self, project_dir=None):
        """
        Initialize the Library.
        **This interface will  initialize the device and the test system  **
        The Library will load the current project file which contains all the information used for test scripts to run.
        This file can be created by GUI tool.

        Examples (use only one of these):

        | *Setting* | *Value*  | *Value*    | *Value* |
        | Library | TAFLib  | projectdir
        """

        self.project_model = None
        self.project_dir = project_dir
        self.gx1_simulator = BPS()
        self.squish_proxy = None

        self.strftime_dir = datetime.datetime.now().strftime(
            "%Y_%m_%d_%H_%M_%S"
        )
        self.command_listener = CommandListener(strftime_dir=self.strftime_dir)
        self.gx1_simulator.add_command_listener(self.command_listener)
        self.ROBOT_LIBRARY_LISTENER = self
        self.project_inited = False
        self.out_put_dir = None
        self.is_log_inited = False
        self.squish_name_mapping = dict()
        self.tessert_ocr = TessertOCR()
        self.p2p_comparer = P2PImageCompare()
        self.system_context = ExecutorContext()
        self.system_context.set_robot_context(self)

    #####################################################################################################
    ################################listeners #####################################################################

    def _end_test(self, name, attrs):
        logger.info(f"Test {name} end.")
        self.command_listener.close_message_log()

    def _start_test(self, name, attrs):
        # BuiltIn().set_variable("${OUTPUT DIR}",self.projectmodel.getTestOutputDir())
        logger.info("Test %s started" % (name))
        self.command_listener.open_message_log()

    def _end_suite(self, name, attrs):
        logger.info("Suite %s end." % (name))

    def _start_suite(self, name, attrs):
        # BuiltIn().set_variable("${OUTPUT DIR}",self.projectmodel.getTestOutputDir())
        logger.info("Suite %s started" % (name))

    def _close(self):
        """
        when this hook is called, the output.xml and other reports are not closed yet.
        :return:
        """
        pass

    def _get_unique_image_name(self):
        my_uuid = uuid.uuid4()
        return f"Img_{my_uuid}.png"

    def _embed_screenshot(self, path, width):
        link = utils.get_link_path(path, self._log_dir)
        logger.info(
            '<a href="%s"><img src="%s" width="%s"></a>' % (link, link, width),
            html=True,
        )

    def _link_screenshot(self, path):
        link = utils.get_link_path(path, self._log_dir)
        logger.info(
            "Screenshot saved to '<a href=\"%s\">%s</a>'." % (link, path),
            html=True,
        )

    def _get_obj_from_alias(self, alias):
        obj = self.squish_name_mapping.get(alias, None)
        if obj is None:
            raise Exception(f"There is no squish name {alias} in the name.py")
        return obj

    @property
    def _log_dir(self):
        variables = BuiltIn().get_variables()
        outdir = variables["${OUTPUTDIR}"]
        # log = variables["${LOGFILE}"]
        # log = os.path.dirname(log) if log != "NONE" else "."
        dir_path = os.path.normpath(
            os.path.join(
                outdir,
                self.strftime_dir,
            )
        )
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def _get_screenshot_path(self, basename):
        directory = self._log_dir
        variables = BuiltIn().get_variables()
        test_dir = os.path.join(
            directory,
            "output_images",
            # correct_filename(variables["${SUITE_NAME}"]),
            correct_filename(variables["${TEST NAME}"]),
        )
        os.makedirs(test_dir, exist_ok=True)

        if basename.lower().endswith((".png", ".png")):
            return os.path.join(test_dir, basename)
        index = 0
        while True:
            index += 1
            path = os.path.join(test_dir, "%s_%d.png" % (basename, index))
            if not os.path.exists(path):
                return path

    def __init_project(self):
        appconfig = AppConfig()
        last_open_project = appconfig.getProjectHistoryList()[-1]

        if self.project_dir is None:
            self.project_dir = last_open_project

        logger.info(f"Loading the project at {self.project_dir}")
        self.project_model.open(self.project_dir)
        ip_prop = self.project_model.squish_container.getPropertyByName("IP")
        aut_prop = self.project_model.squish_container.getPropertyByName("AUT")
        private_key = self.project_model.squish_container.getPropertyByName(
            "PrivateKey"
        )
        squishHomeDirProp = (
            self.project_model.squish_container.getPropertyByName("SquishHome")
        )
        if ip_prop and aut_prop and private_key:
            ip_address = ip_prop.getStringValue()
            aut_name = aut_prop.getStringValue()
            private_key_file = private_key.getStringValue()
            self.squish_proxy = SquishProxy(
                squishHomeDirProp.getStringValue(),
                ip_address,
                private_key_file,
                aut_name,
            )
            logger.info(
                f"Squish Hook {ip_address}, {aut_name}, {private_key_file}"
            )
            logger.info(
                "%s has been loaded successfully"
                % self.project_model.getLabel()
            )
        else:
            logger.error(
                "Failed to init the project the project setting error"
            )

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
            self.project_model = Project(None)
            self.__init_project()
            self.squish_name_mapping = (
                self.project_model.squish_container.get_all_name_mapping()
            )
            self.project_inited = True
            communication_type = self.project_model.getPropertyByName(
                "CommunicationType"
            ).getStringValue()
            if communication_type == "PIPE":
                ctype = SERIAL_PIPE
                pipe_name = self.project_model.getPropertyByName(
                    "PipeName"
                ).getStringValue()
                com_port_val = pipe_name
            else:
                com_port_val = self.project_model.getPropertyByName(
                    "COM"
                ).getStringValue()
                ctype = SERIAL_PORT

            result = True
            result = self.gx1_simulator.start(com_port_val, ctype)
            if result:
                logger.info("GX1 Simulator is started")
            else:
                logger.error("GX1 Simulator failed to start")
                raise Exception("GX1 Simulator failed to start")

            if communication_type == "PIPE":
                pause_execution(
                    "Please start the virtual machine now. restart will not work"
                )
            # TODO(csniu): It's right, on the real machine
            # result = self.squish_proxy.connect()
            # enabled_squish = (
            #     self.project_model.squish_container.getPropertyByName(
            #         "Enabled"
            #     )
            # )
            # if enabled_squish.getStringValue() == "True":
            #     pause_execution(
            #         "Waiting to start Squish hooker in GX1 GUI,\n Start GX1 GUI application first"
            #     )
            self.squish_proxy.start_squish_server()
            self.squish_proxy.create_proxy()
            result = self.squish_proxy.connect()
            if result:
                logger.info("Squish tester is started")
            else:
                logger.error("Squish tester failed to start")
                raise Exception("GX1 Simulator failed to start")

        else:
            logger.warn("Project is already initialized")

    def close_test(self):
        """
        Description:
        Close all and cleanup after the test is done
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
            enabled_squish = (
                self.project_model.squish_container.getPropertyByName(
                    "Enabled"
                )
            )
            if enabled_squish.getStringValue() == "True":
                self.squish_proxy.disconnect()
                self.squish_proxy.stop_squish_server()
                logger.info("Squish tester is stopped")
        else:
            logger.warn("The project is not initialized for testing ")
        self.project_inited = False

    def set_command_response(self, command_code, **response_data):
        """
        Set the response data
        :param command_code: the command code not the response code
        :param response_data: the leaf field of the response data
        :return:
        """
        command_code = int(command_code, 16)
        key_int_value_map = dict()
        for key, str_value in response_data.items():
            key_int_value_map[key] = int(str_value)
        return self.gx1_simulator.set_command_pending_response_by_parameters(
            command_code, **key_int_value_map
        )

    def clean_command_logging_queue(self):
        """
        Clean the queue
        :return:
        """
        return self.gx1_simulator.clean_logged_command_queue()

    def find_logged_commands(self, command_code, start_seq=-1, **kwargs):
        """
        To find the command or response in the queue
        :param command_code: the command code or response code
        :param start_seq: from where to search forward
        :param kwargs: the matching condition of the field value, key pairs
        :return:
        """
        start_seq = int(start_seq)
        command_code = int(command_code, 16)
        return self.gx1_simulator.find_logged_commands(
            command_code, start_seq, **kwargs
        )

    def start_scenario(self, scenario_name):
        """
        Start the stimulation scenario by its alias
        :param scenario_name:
        :return:
        """
        self.project_model.scenario_py_container.start_scenario(scenario_name)

    def stop_scenario(self, scenario_name):
        """
        Stop the scenario by its alias
        :param scenario_name:
        :return:
        """
        self.project_model.scenario_py_container.stop_scenario(scenario_name)

    def screen_shot(self, embedded_image_to_report=True):
        """
        Capture the image from Screen and embedded  the image captured to the report
        :param embedded_image_to_report: whether the image should be embedded into report
        :return: the image file location
        """
        # basename = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S.png')
        basename = self._get_unique_image_name()
        screenshot_name = self._get_screenshot_path(basename)
        self.squish_proxy.screen_save(screenshot_name)
        if embedded_image_to_report in ["1", "TRUE", True]:
            self._embed_screenshot(screenshot_name, 400)
        return screenshot_name

    def list_drag(self, gobj, offset):
        """If object is applicable, allow to drag a list.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            offset (int): The direction and length to drag in pixels.

        """
        offset = int(offset)
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_proxy.list_drag(gobj, offset)

    def mouse_tap(self, gobj):
        """If object is applicable, perform a touch tap by passing in the Squish object reference.

        See `squishtest.tapObject`

        Args:
            gobj (dict): A dictionary containing the Squish object details

        """
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_proxy.mouse_tap(gobj)

    def mouse_wheel(self, gobj, steps):
        """If object is applicable, this function performs a mouse wheel operation,
        emulating rotation of the vertical wheel of a mouse.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            steps (int): number of ticks to move the mouse wheel.

        """
        steps = int(steps)
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_proxy.mouse_wheel(gobj, steps)

    def mouse_wheel_screen(self, x, y, steps):
        """If the Squish object exist, this function will perform a mouse wheel scroll
        operation on all scrollable objects on the screen. The number of ticks to scroll
        can only be 1 or -1.

        Args:
            steps (int): an integer number, if > 0, ticks to scroll is one. Otherwise is minus one
            x (int): position but not in use.
            y (int): position but not in use.

        """
        steps = int(steps)
        return self.squish_proxy.mouse_wheel_screen(x, y, steps)

    def long_mouse_drag(self, gobj, x, y, dx, dy):
        """If object is applicable, this function will produce a mouse drag operation with a fixed delay of
        about one second between pressing the mouse button and starting to move the mouse cursor.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            x (int): The x coordinate of the mouse cursor.
            y (int): The y coordinate of the mouse cursor.
            dx (int): The objectOrName widget is dragged by dx pixels horizontally.
            dy (int): The objectOrName widget is dragged by dy pixels vertically.
        """
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_proxy.long_mouse_drag(
            gobj, int(x), int(y), int(dx), int(dy)
        )

    def mouse_click(self, gobj):
        """If object is applicable, perform a mouse click by passing in the Squish object reference.

        See `squishtest.mouseClick`

        Args:
            gobj (dict): A dictionary containing the Squish object details.

        """
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_proxy.mouse_click(gobj)
        # return self.squish_proxy.mouse_click(gobj)

    def mouse_xy(self, x, y):
        """Perform a mouse click on the active window.

        Args:
            x (int): the pixels on the x axis.
            y (int): the pixels on the y axis.

        """
        x = int(x)
        y = int(y)
        return self.squish_proxy.mouse_xy(x, y)

    def long_mouse_click(self, gobj, x, y):
        """Perform a long mouse click on the active window.

        Args:
            x (int): the pixels on the x axis.
            y (int): the pixels on the y axis.

        """
        x = int(x)
        y = int(y)
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_proxy.long_mouse_click(gobj, x, y)

    def get_text(self, screenshot_path, image_alias, rect_alias, lang="en"):
        """
        Get the text from the image and the feature rect
        :param screenshot_path: the image path that need to be verified.
        :param image_alias: the alias of the sample image
        :param rect_alias: the alias of the sample feature rect
        :param lang: the language of the text
        :return: the text
        """

        feature_rect = (
            self.project_model.image_processing_container.get_feature_rect(
                image_alias, rect_alias
            )
        )
        result = self.tessert_ocr.get_string(
            screenshot_path,
            (feature_rect[0], feature_rect[1]),
            (
                feature_rect[0] + feature_rect[2],
                feature_rect[1] + feature_rect[3],
            ),
        )
        cropped_image = result[1]
        basename = self._get_unique_image_name()
        screenshot_name = self._get_screenshot_path(basename)
        cropped_image.save(screenshot_name)
        self._embed_screenshot(screenshot_name, feature_rect[2])
        return result[0]

    def compare_feature_rect(
        self, screenshot_path, sample_image_alias, sample_rect_alias
    ):
        """
        To compare the consistency of image  feature rect
        :param screenshot_path: the image path that need to be verified.
        :param sample_image_alias: the alias of the sample image
        :param sample_rect_alias: the alias of the sample feature rect
        :return: the consistency
        """
        sample_image_path = (
            self.project_model.image_processing_container.get_image_object(
                sample_image_alias
            )
            .getPropertyByName("Path")
            .getStringValue()
        )
        feature_rect = (
            self.project_model.image_processing_container.get_feature_rect(
                sample_image_alias, sample_rect_alias
            )
        )
        img1 = Image.open(screenshot_path)
        img2 = Image.open(sample_image_path)
        img1 = img1.crop(
            (
                feature_rect[0],
                feature_rect[1],
                feature_rect[0] + feature_rect[2],
                feature_rect[1] + feature_rect[3],
            )
        )
        img2 = img2.crop(
            (
                feature_rect[0],
                feature_rect[1],
                feature_rect[0] + feature_rect[2],
                feature_rect[1] + feature_rect[3],
            )
        )
        screenshot_name_1 = self._get_screenshot_path(
            self._get_unique_image_name()
        )
        img1.save(screenshot_name_1)
        screenshot_name_2 = self._get_screenshot_path(
            self._get_unique_image_name()
        )
        img2.save(screenshot_name_2)
        self._embed_screenshot(screenshot_name_1, feature_rect[2])
        self._embed_screenshot(screenshot_name_2, feature_rect[2])
        ident = self.p2p_comparer.compare(
            screenshot_path, sample_image_path, feature_rect
        )
        return ident

    def find_all_objects(self, gobj, *return_attrs):
        """finds and returns a list of objects that match the given object description.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            return_attrs (list): A list of attributes to return,default is ['text']
        Returns:
            (list): a list of objects if exist, empty list otherwise.
        """
        gobj = self._get_obj_from_alias(gobj)
        return self.squish_proxy.find_all_objects(gobj, *return_attrs)


if __name__ == "__main__":
    gx1_testlib = GX1Testlib()
    gx1_testlib.init_test()
    # gx1_testlib.get_text("", "ElectrodeSetup", "Monopolar")

    gx1_testlib.mouse_xy(722, 161)
    gx1_testlib.start_scenario("RampMeasure")
    time.sleep(1)
    gx1_testlib.start_scenario("RampMeasure")
    gx1_testlib.clean_command_logging_queue()
    KWG = dict()
    time.sleep(1)
    KWG["ar_measured_channels[0].u8_TempRefAvailable"] = 1
    command_lists = gx1_testlib.find_logged_commands("0xC049", 0, **KWG)
    KWG.clear()
    KWG["au8_channels[0]"] = 1
    command_lists = gx1_testlib.find_logged_commands("0xC048", 0, **KWG)
    gx1_testlib.mouse_xy(109, 702)

    gx1_testlib.mouse_click("OneTouch")
    time.sleep(1)
    gx1_testlib.mouse_click("Stimulation")
    time.sleep(1)
    gx1_testlib.set_command_response("0xC046", u8_OutputStatus=1)
    # tt.start()
    time.sleep(10)
    # gx1_testlib.mouse_click("OneTouch")
    # gx1_testlib.command_listener.open_message_log()
    # gx1_testlib.screen_shot(1)

    gx1_testlib.close_test()
