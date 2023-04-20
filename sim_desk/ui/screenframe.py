import wx

from sim_desk.mgr.context import SimDeskContext
import os


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

    def on_mouse_move(self, event):
        pos = event.GetPosition()
        self.mainframe.sb.SetStatusText(f"Mouse position: ({pos.x}, {pos.y})")

    def on_left_down(self, event):
        # This function will be called when the left mouse button is clicked on the panel
        x, y = event.GetPosition()
        if self.mainframe.squish_runner is not None and self._squish_started is True:
            self.mainframe.squish_runner.mouse_xy(x,y)

    def start(self):
        self._squish_started = True
        self.timer.Start(40)  # 200 ms = 5 fps

    def stop(self):
        self._squish_started = False
        self.timer.Stop()

    def update_image(self, event):
        dirname = os.path.dirname(__file__)
        screenshot = os.path.join(dirname, "screen.png")
        self.mainframe.squish_runner.screen_save(screenshot)
        self.set_image(screenshot)

    def set_image(self, image_path):
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
