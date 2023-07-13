"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: screenframe.py
@time: 2023/3/26 10:58
@desc:
"""
import os
import threading

import wx

from sim_desk.mgr.context import SimDeskContext
from utils import logger
from utils.utilities import get_screen_shot_home_folder


class ScreenUpdateEvent(wx.PyCommandEvent):  # 1 定义事件
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.eventArgs = ""

    def GetEventArgs(self):
        return self.eventArgs

    def SetEventArgs(self, args):
        self.eventArgs = args


myEVT_MY_SCREEN_UPDATE = wx.NewEventType()  # 2 创建一个事件类型
EVT_SCREEN_UPDATE = wx.PyEventBinder(myEVT_MY_SCREEN_UPDATE, 1)  # 3 创建一个绑定器对象


class MyScrolledPanel(wx.ScrolledWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # Create a sizer to hold the content of the panel
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.screen = ScreenFrame(self)
        self.sizer.Add(self.screen, 0, wx.ALL, 10)

        # Set the sizer for the panel
        self.SetSizer(self.sizer)

        # Set the virtual size of the panel
        self.SetScrollRate(10, 10)
        self.SetVirtualSize(1024, 768)

    def start(self):
        self.screen.start()  # 200 ms = 5 fps

    def stop(self):
        self.screen.stop()


class ScreenFrame(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.parent = parent
        self.mainframe = SimDeskContext().get_main_frame()
        self.current_image = None
        self.current_image_index = 0
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_TIMER, self.update_image, self.timer)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.buffer = None
        self.image = None
        self.SetMinSize(wx.Size(1024, 768))
        self.SetDoubleBuffered(True)
        self._squish_started = False
        self.update_frame_thread: threading.Thread = None

        # self.Bind(EVT_SCREEN_UPDATE, self.set_image)

    def __update_screen(self):
        while True:
            if self._squish_started is False:
                break
            try:
                screenshot = os.path.join(
                    get_screen_shot_home_folder(), "screen.png"
                )
                self.mainframe.squish_runner.screen_save(screenshot)
                evt = ScreenUpdateEvent(
                    myEVT_MY_SCREEN_UPDATE, wx.NewId()
                )  # 5 创建自定义事件对象
                evt.SetEventArgs(screenshot)  # 6添加数据到事件
                self.GetEventHandler().ProcessEvent(evt)  # 7 处理事件
            except Exception as err:
                logger.error(err)

    def on_mouse_move(self, event):
        pos = event.GetPosition()
        self.mainframe.sb.SetStatusText(f"Mouse position: ({pos.x}, {pos.y})")

    def on_left_down(self, event):
        # This function will be called when the left mouse button is clicked on the panel
        x, y = event.GetPosition()
        if (
            self.mainframe.squish_runner is not None
            and self._squish_started is True
        ):
            self.mainframe.squish_runner.mouse_xy(x, y)

    def start(self):
        self._squish_started = True
        self.timer.Start(40)  # 200 ms = 5 fps
        # self.update_frame_thread = threading.Thread(target=self.__update_screen)
        # self.update_frame_thread.setDaemon(True)
        # self.update_frame_thread.start()

    def stop(self):
        self._squish_started = False
        # if self.update_frame_thread is not None:
        #    self.update_frame_thread.join(1)

        self.timer.Stop()

    def update_image(self, event):
        # dirname = os.path.dirname(__file__)
        screenshot = os.path.join(get_screen_shot_home_folder(), "screen.png")
        self.mainframe.squish_runner.screen_save(screenshot)
        self.set_image(screenshot)

    def set_image(self, image_path):
        # image_path = evt.GetEventArgs()
        new_image = wx.Image(image_path)
        panel_size = self.GetClientSize()

        # Scale the image to fit the panel, but maintain its aspect ratio
        img_width = new_image.GetWidth()
        img_height = new_image.GetHeight()
        panel_width = panel_size[0]
        panel_height = panel_size[1]
        if panel_width / panel_height < img_width / img_height:
            scaled_width = panel_width
            scaled_height = panel_width * img_height // img_width
        else:
            scaled_width = panel_height * img_width // img_height
            scaled_height = panel_height

        new_image = new_image.Scale(scaled_width, scaled_height)
        self.image = wx.Bitmap(new_image)
        self.Refresh()

    def on_size(self, event):
        self.Refresh()

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        if self.image is not None:
            dc.DrawBitmap(self.image, 0, 0)
        else:
            dc.Clear()
