#!/usr/bin/env python
# encoding: utf-8
"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSCUDSStudio
@file: squish_lib.py
@time: 2023/4/1 17:40
@desc:
"""
#!/usr/bin/env python
# encoding: utf-8
"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSCUDSStudio
@file: pyssh.py
@time: 2023/3/25 20:34
@desc:
"""
import sys
sys.path.append(r'E:\Squish for Qt 7.0.1\bin')
sys.path.append(r'E:\Squish for Qt 7.0.1\lib\python')
import squishtest as sqt
import psutil
import subprocess
import time
import logging
from utils.utilties import os_system_cmd
from project_specific import names
logger = logging.getLogger("GX1")


def find_process(pname):
    """Look the list of currently running process for match the given name process.

    Args:
        pname (str): The process name such as ``python``

    Retuns:
        (str): The complete name of the process, i.e. ``python.exe``

    """
    pfound = None
    for proc in psutil.process_iter():
        if pname in proc.name():
            pfound = proc.name()
    return pfound


class SquishTest(object):
    def __init__(self, target_ip_address, private_keyfile, attach_app_name='RFGenerator'):
        self.process_to_attach = attach_app_name
        self._squish_started = False
        self._open_ssh_folder = r"C:\\Windows\\System32\\OpenSSH"
        self._target_ip_address = target_ip_address
        self._private_keyfile = private_keyfile
        self._ssh_User = ["-i", self._private_keyfile]
        self._spSsh = None
        self._app_context = None
        self._is_check_obj_exists = True
        self._parent = None
        self._connectingCallback = None

    # ================================================================================
    # Squish library communication
    # ================================================================================
    def start_squish_server(self):
        """Starts the Squish server as a subprocess.

        """
        try:
            subprocess.run(["squishserver.exe", "--stop"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.Popen(['squishserver.exe'],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self._squish_started = True
            time.sleep(3)
        except WindowsError as err:
            logger.error("Squish server started failed")
            return False
        return True

    def ssh_connect(self):
        """Establish the SSh connection to port 3520 for Squish AUT attachment.
        """
        for i in range(0, 3):
            self._spSsh = subprocess.Popen(
                [self._open_ssh_folder + "\\ssh", "-oStrictHostKeyChecking=no", "-tt", "-L", "3250:localhost:3250",
                 *self._ssh_User, "bsci@%s" % self._target_ip_address], bufsize=0, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,shell=True)
            time.sleep(1)
            if self.is_active() is True:
                try:
                    self.input_cmd("")
                except:
                    pass
                line = self._spSsh.stdout.readline()
                line = "".join(e for e in line.decode() if e.isprintable())
                if line.find("bsci@") >= 0:
                    logger.info("SSH connection Successful %s %s" % (self._target_ip_address, str(self._ssh_User)))
                    break
                elif line.find("MTI> ") >= 0:
                    self.disconnect()
                    logger.info("The system is still in MTI mode, please reboot it to the application mode")
                    break

            logger.info("Retry generating the ssh key for %s %s..." % (self._target_ip_address, str(self._ssh_User)))
            os_system_cmd("%s\\ssh-keygen -R %s" % (self._open_ssh_folder, self._target_ip_address))
            os_system_cmd("echo exit|%s\\ssh -oStrictHostKeyChecking=no -L 3520:localhost:3520 bsci@%s" % (
                self._open_ssh_folder, self._target_ip_address))
            self._spSsh = None

        return self._spSsh is not None

    def connect(self):
        """This function will try to attach to a Squish AUT VssUI.

        """

        if self._connectingCallback:
            self._connectingCallback()
        if self._squish_started is not True:
            if self.start_squish_server() is False:
                return False

        self.disconnect()
        if self.ssh_connect() is not True:
            logger.error("Failed to establish SSH connection!!!")
            if self.connectDoneCallback:
                self.connectDoneCallback()
            return False

        for i in range(0, 2):
            try:
                self._app_context = sqt.attachToApplication(self.process_to_attach)
                logger.info(f'Attach AUT {self.process_to_attach} Successful')
                # ct = sqt.applicationContext("VssUI")
                # ctLst = sqt.applicationContextList()
                break
            except:
                logger.info(f"Failed to attach to AUT  {self.process_to_attach}!!!")
                self.disconnect()
                logger.info(f"Retry connecting to AUT  {self.process_to_attach}.")

                time.sleep(2)
                os_system_cmd("%s\\ssh-keygen -R %s" % (self._open_ssh_folder, self._target_ip_address))
                os_system_cmd("echo exit|%s\\ssh -oStrictHostKeyChecking=no -L 3520:localhost:3520 bsci@%s" % (
                self._open_ssh_folder, self._target_ip_address))
                time.sleep(2)
                self.ssh_connect()

            self.start_squish_server()

        if self._app_context is None:
            self.disconnect()
            os_system_cmd("%s\\ssh-keygen -R %s" % (self._open_ssh_folder, self._target_ip_address))
            if self.connectDoneCallback: self.connectDoneCallback()
            return False

        if self.connectDoneCallback: self.connectDoneCallback()
        return True

    def is_active(self):
        """check if the command line launched from python script as a subprocess is still running.

        Returns:
            bool: True if the suprocess is running, False otherwise.

        """
        return self._spSsh.poll() is None  # None mean the subprocess still running

    def input_cmd(self, cmd_str, delay=0.01):
        """If an SSH session is active, send a command over it.

        Args:
            cmd_str (str): The string command to send.
            delay (int or float): A delay before sending the command.

        Returns:
            bool: True is successful, False otherwise such i.e. if not SSH session is active.

        """
        if self.is_active() is not True:
            logger.info("Not able to send command due to ssh session not active!!!")
            return False

        time.sleep(delay)

        if type(cmd_str) == bytes:
            cmd_str = cmd_str.decode()

        _inputCmdStr = cmd_str.replace("\n", "").replace("\r", "")
        self._spSsh.stdin.write((_inputCmdStr + "\n").encode())
        self._spSsh.stdin.flush()
        return True

    def disconnect(self):
        """Detach the AUT.

        """
        if self._app_context is not None:
            self._app_context.detach()
            self._app_context = None
            logger.info(f"Detach AUT {self.process_to_attach}... Done")

        if self._spSsh is not None:
            self._spSsh.kill()
            time.sleep(0.5)
            self._spSsh = None
            logger.info("Disconnecting SSH... Done")

    def gobj_exist(self, gobj, timeout=0.5):
        """Look for a squish object. If there is no AUT try to make a connection.

        Args:
            gobj (dict): A dictionary containing the Squish object details,
            i.e.: ``rEADY_Text = {"container": o_Tab, "text": "READY", "type": "Text", "unnamed": 1, "visible": True}``

        Returns:
            (bool): True if the Squish object exist, False otherwise.

        """
        if (self._app_context is None) or (self._app_context.isFrozen(2) is True):
            self.connect()
            time.sleep(1)

        return self.getGobj(gobj) is not None

    def get_gobj(self, gobj, timeout=0.5):
        """Returns the Squish object for the given native script dictionary of squish object.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            timeout (int): Timeout Value.

        Returns:
            (obj or None): The Squish object if exist, None otherwise.

        """
        if sqt.object.exists(gobj) is not True:
            return None
        try:
            _obj = sqt.waitForObject(gobj, timeout * 1000)
        except:
            _obj = None
        return _obj

    def get_action_obj(self, gobj):
        """Check if Squish object exist and the action of object can be applied.

        Args:
            gobj (dict): A dictionary containing the Squish object details

        Returns:
            (obj): The Squish object if exists, None otherwise.

        """
        if (self._app_context is None) or (self._app_context.isFrozen(2) is True):
            self.connect()
            time.sleep(1)

        if self._is_check_obj_exists is True:
            logger.info("GUI object %s applicable in current state" % (["is NOT", "is"][self.gobj_exist(gobj)]))
            return None

        if self.gobj_exist(gobj) is not True:
            logger.info("\n!!! Object not applicable in this screen context!!! (%s)" % str(gobj))
            return None

        return self.get_gobj(gobj)

    def list_drag(self, gobj, offset):
        """If object is applicable, allow to drag a list.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            offset (int): The direction and length to drag in pixels.

        """
        _obj = self.get_action_obj(gobj)
        if _obj is not None:
            sqt.flick(_obj, 0, offset)

    def mouse_tap(self, gobj):
        """If object is applicable, perform a touch tap by passing in the Squish object reference.

        See `squishtest.tapObject`

        Args:
            gobj (dict): A dictionary containing the Squish object details

        """
        _obj = self.get_action_obj(gobj)
        if _obj is not None:
            sqt.tap_object(_obj)

    def mouse_wheel(self, gobj, steps):
        """If object is applicable, this function performs a mouse wheel operation,
        emulating rotation of the vertical wheel of a mouse.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            steps (int): number of ticks to move the mouse wheel.

        """
        _obj = self.get_action_obj(gobj)
        if _obj is not None:
            sqt.mouseWheel(_obj, 1, 1, 0, steps, sqt.Qt.NoModifier)

    def mouse_wheel_screen(self, x, y, steps):
        """If the Squish object exist, this function will perform a mouse wheel scroll
        operation on all scrollable objects on the screen. The number of ticks to scroll
        can only be 1 or -1.

        Args:
            steps (int): an integer number, if > 0, ticks to scroll is one. Otherwise is minus one
            x (int): position but not in use.
            y (int): position but not in use.

        """
        steps = 1 if steps > 0 else -1
        for gobj in self.listViews:
            if self.gobj_exist(gobj):
                _obj = self.get_action_obj(gobj)
                sqt.mouseWheel(_obj, 1, 1, 0, steps, sqt.Qt.NoModifier)
                return
        # as part of the clean up, please remove the following code if not in use.
        # as a last resort, try this?:
        # sqt.mouseWheel(names.o_QQuickApplicationWindow, x, y, 0, steps, sqt.Qt.NoModifier)

    def long_mouse_drag(self, gobj, steps):
        """If object is applicable, this function will procuce a mouse drag operation with a fixed delay of
        about one second between pressing the mouse button and starting to move the mouse cursor.

        Args:
            gobj (dict): A dictionary containing the Squish object details
            steps (int): pixels to drag.

        """
        _obj = self.get_action_obj(gobj)
        if _obj is not None:
            sqt.longMouseDrag(_obj, 300, 30, 0, steps, sqt.Qt.NoModifier, sqt.Qt.LeftButton)

    def mouse_click(self, gobj):
        """If object is applicable, perform a mouse click by passing in the Squish object reference.

        See `squishtest.mouseClick`

        Args:
            gobj (dict): A dictionary containing the Squish object details.

        """
        _obj = self.get_action_obj(gobj)
        if _obj is not None:
            sqt.mouseClick(_obj)

    def set_gui_app_root(self, parent):
        self._parent = parent

    def mouse_xy(self, x, y):
        """Perform a mouse click on the active window.

        Args:
            x (int): the pixels on the x axis.
            y (int): the pixels on the y axis.

        """
        if self.get_action_obj(names.greenHouse_Application_QQuickWindowQmlImpl) is not None:  # in case we need to re-connect
            sqt.tapObject(names.greenHouse_Application_QQuickWindowQmlImpl, x, y)

    def long_mouse_click(self, gobj, x, y):
        """Perform a long mouse click on the active window.

        Args:
            x (int): the pixels on the x axis.
            y (int): the pixels on the y axis.

        """
        _obj = self.get_action_obj(gobj)
        if _obj is not None:
            sqt.longMouseClick(_obj, x, y, sqt.Qt.LeftButton)

    def screen_save(self, path_to_save):
        """Perform a screenshot of the screen and save it under the TMP folder on local station.

        """
        if self.get_action_obj(names.greenHouse_Application_QQuickWindowQmlImpl) is not None:  # in case we need to re-connect
            sqt.saveDesktopScreenshot(path_to_save)
        else:
            return None

    def get_gobj_text(self, gobj):
        """Given an Squish object dictionary, return the name of the object.

        Args:
            gobj (dict): The Squish dictionary.
            i.e. ``{"checkable": False, "container": o_Tab, "objectName": "t_btnPulseModeSmartDustLeft", "text": "SmartDust", "type": "VssButton", "visible": True}``

        """
        _obj = self.get_gobj(gobj)
        try:
            _txt = str(_obj.text)
        except:
            _txt = "NA"
        return _txt


if __name__ == "__main__":
    from sshtunnel import SSHTunnelForwarder

    # logger = logging.getLogger(
    #     'sshtunnel.SSHTunnelForwarder'
    # )
    # logger.setLevel(logging.DEBUG)
    # remote_user = 'bsci'
    # remote_host = '192.168.254.130'
    # remote_port = 22
    # local_host = '127.0.0.1'
    # local_port = 3520
    # private_server = 'localhost'
    # private_server_port = 3520
    #
    # try:
    #     with SSHTunnelForwarder(
    #             (remote_host, remote_port),
    #             ssh_username=remote_user,
    #             ssh_private_key=r'E:\WORKSPACE\GX1\FengKevin.Xu@bsci.com\FengKevin.Xu@bsci.com',
    #             remote_bind_address=(local_host, local_port),
    #             local_bind_address=(local_host, local_port),
    #             ssh_private_key_password='Xf59166565',
    #             logger = logger
    #     ) as server:
    #
    #         server.start()
    #         print('server connected')
    #
    #         r = requests.get(f'{private_server}:{private_server_port}').content
    #         print(r)
    #
    # except Exception as e:
    #     print(str(e))
    import paramiko

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect('192.168.254.130', username='bsci',password='Xf59166565',
                passphrase='Xf59166565',
                allow_agent=True)

    ssh.save_host_keys("hostkey.txt")

    stdin, stdout, stderr = ssh.exec_command('cd /',bufsize=0,timeout=5)
    stdin, stdout, stderr = ssh.exec_command('ls ', bufsize=0, timeout=5)
    print(stdout.readlines())
    ssh.close()