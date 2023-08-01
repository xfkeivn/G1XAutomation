"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: squishPyServe.py
@time: 2023/3/25 20:34
@desc:
"""

import os
import socket
import sys
import time

import Pyro5.api
import Pyro5.server
import Pyro5.socketutil
from Pyro5.api import Daemon, expose, locate_ns, oneway

from squish.squish_lib import *

Pyro5.config.SERVERTYPE = "multiplex"
Pyro5.config.POLLTIMEOUT = 3


@Pyro5.server.behavior(instance_mode="single")
class SquishPyServer:
    def __init__(
        self,
        squish_install_dir,
        target_ip_address,
        private_keyfile,
        attach_app_name="gx1",
    ):
        self.squish_tester = SquishTest(
            squish_install_dir,
            target_ip_address,
            private_keyfile,
            attach_app_name,
        )

    # ================================================================================
    # Squish library communication
    # ================================================================================

    @expose
    def connect(self):
        return self.squish_tester.connect()

    @expose
    def disconnect(self):
        return self.squish_tester.disconnect()

    @expose
    def list_drag(self, gobj, offset):
        return self.squish_tester.list_drag(gobj, offset)

    @expose
    def mouse_tap(self, gobj):
        return self.squish_tester.mouse_tap(gobj)

    @expose
    def mouse_wheel(self, gobj, steps):
        return self.squish_tester.mouse_wheel(gobj, steps)

    @expose
    def mouse_wheel_screen(self, x, y, steps):
        return self.squish_tester.mouse_wheel_screen(x, y, steps)

    @expose
    def long_mouse_drag(self, gobj, x, y, z, steps):
        return self.squish_tester.long_mouse_drag(gobj, x, y, z, steps)

    @expose
    def mouse_click(self, gobj):
        return self.squish_tester.mouse_click(gobj)

    @expose
    def mouse_xy(self, x, y):
        return self.squish_tester.mouse_xy(x, y)

    @expose
    def long_mouse_click(self, gobj, x, y):
        return self.squish_tester.long_mouse_click(gobj, x, y)

    @expose
    def screen_save(self, path_to_save):
        return self.squish_tester.screen_save(path_to_save)

    @expose
    def get_gobj_text(self, gobj):
        return self.squish_tester.get_gobj_text(gobj)

    @expose
    def find_all_objects(self, gobj, *return_attrs):
        return self.squish_tester.find_all_objects(gobj, *return_attrs)


if __name__ == "__main__":
    servePyro = True
    _hostName = socket.gethostname()
    _hostIP = "127.0.0.1"

    print(sys.argv)

    if len(sys.argv) == 1:
        ipaddr = r"192.168.80.130"
        auth = r"C:\Users\xuf\.ssh\bsci"
        aut = "gx1"
        install_dir = r"D:\Squish for Qt 7.0.1"
    else:
        install_dir = sys.argv[1]
        ipaddr = sys.argv[2]
        auth = sys.argv[3]
        aut = sys.argv[4]

    target_ip, ssh_private_key_file, attached_app_name = (ipaddr, auth, aut)
    if os.path.exists(ssh_private_key_file) is False:
        print(" The private key file does not exists")
    else:
        squish_tester = SquishPyServer(
            install_dir, target_ip, ssh_private_key_file, attached_app_name
        )
        if servePyro:
            (
                nameserverUri,
                nameserverDaemon,
                broadcastServer,
            ) = Pyro5.nameserver.start_ns(host="0.0.0.0")
            assert (
                broadcastServer is not None
            ), "expect a broadcast server to be created"
            print("Got a Nameserver, uri: %s" % nameserverUri)
        else:
            try:
                nameserver = Pyro5.core.locate_ns(host=_hostIP)
            except Pyro5.errors.NamingError:
                print("Failed to locate the nameserver")
                sys.exit(1)

        with Daemon(host=_hostIP, port=45082) as daemon:
            uri = daemon.register(squish_tester, "gx1.squish_server")
            print("Adapter class registered, uri: ", uri)
            if servePyro:
                nameserverDaemon.nameserver.register(
                    "gx1.development.squish_server", uri
                )
                daemon.combine(nameserverDaemon)
                daemon.combine(broadcastServer)
            else:
                nameserver.register("gx1.development.squish_server", uri)
            try:
                daemon.requestLoop()
            except KeyboardInterrupt:
                print("caught Ctrl-C")
            except Exception as e:
                # print(e)
                pass
