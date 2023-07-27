"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: squish_proxy.py
@time: 2023/3/25 20:34
@desc:
"""
import os
import subprocess

from Pyro5.api import Proxy, locate_ns

import setting
from utils import logger


class SquishProxy:
    def __init__(
        self, install_dir, target_ip, ssh_private_key, attachable_app_name
    ):
        self.target_ip = target_ip
        self.ssh_private_key = ssh_private_key
        self.attachable_app_name = attachable_app_name
        self.proxy = None
        self.squisher_proxy_server_proces = None
        self.install_dir = install_dir

    def start_squish_server(self):
        logger.info(
            "start the squish pyro server %s,%s,%s"
            % (self.target_ip, self.ssh_private_key, self.attachable_app_name)
        )
        if setting.prod is False:
            venv_path = os.path.join(os.path.dirname(__file__), "../venv")
            activate_script = os.path.join(
                venv_path, "Scripts", "activate.bat"
            )
            subprocess.call(activate_script, shell=True)
            # Start the subprocess using the virtual environment's Python interpreter
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
            self.squisher_proxy_server_proces = subprocess.Popen(
                [
                    python_path,
                    "-m",
                    "squish.squishPyServer",
                    self.install_dir,
                    self.target_ip,
                    self.ssh_private_key,
                    self.attachable_app_name,
                ],
                cwd=os.path.dirname(os.path.dirname(__file__)),
            )

        else:
            venv_path = os.path.join(
                os.path.dirname(__file__), "../../python3"
            )
            python_path = os.path.join(venv_path, "python.exe")
            self.squisher_proxy_server_proces = subprocess.Popen(
                [
                    python_path,
                    "-m",
                    "squish.squishPyServer",
                    self.install_dir,
                    self.target_ip,
                    self.ssh_private_key,
                    self.attachable_app_name,
                ],
                cwd=os.path.dirname(os.path.dirname(__file__)),
            )

        if self.squisher_proxy_server_proces.poll() is None:
            return True
        else:
            return False

    def stop_squish_server(self):
        if self.squisher_proxy_server_proces is not None:
            self.squisher_proxy_server_proces.kill()
            self.squisher_proxy_server_proces = None

    def create_proxy(self):
        with locate_ns(host="127.0.0.1") as ns:
            for router, router_uri in ns.list(
                prefix="gx1.development.squish_server"
            ).items():
                print("found router: %s" % router)
                self.proxy = Proxy(router_uri)
                return True
        return False

    def connect(self):
        return self.proxy.connect()

    def disconnect(self):
        return self.proxy.disconnect()

    def list_drag(self, gobj, offset):
        return self.proxy.list_drag(gobj, offset)

    def mouse_tap(self, gobj):
        return self.proxy.mouse_tap(gobj)

    def mouse_wheel(self, gobj, steps):
        return self.proxy.mouse_wheel(gobj, steps)

    def mouse_wheel_screen(self, x, y, steps):
        return self.proxy.mouse_wheel_screen(x, y, steps)

    def long_mouse_drag(self, gobj, x, y, z, steps):
        return self.proxy.long_mouse_drag(gobj, x, y, z, steps)

    def mouse_click(self, gobj):
        return self.proxy.mouse_click(gobj)

    def mouse_xy(self, x, y):
        return self.proxy.mouse_xy(x, y)

    def long_mouse_click(self, gobj, x, y):
        return self.proxy.long_mouse_click(gobj, x, y)

    def screen_save(self, path_to_save):
        return self.proxy.screen_save(path_to_save)

    def get_gobj_text(self, gobj):
        return self.proxy.get_gobj_text(gobj)

    def get_Names(self, gobj):
        return self.proxy.get_Names(gobj)

    def find_all_objects(self, gobj):
        return self.proxy.find_all_objects(gobj)


if __name__ == "__main__":
    proxy = SquishProxy("192.168.80.130", r"C:\Users\xuf\.ssh\bsci", "gx1")
    proxy.create_proxy()
    proxy.connect()

    proxy.disconnect()
