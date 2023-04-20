"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: ImagePanel.py
@time: 2023/3/26 10:58
@desc:
"""

import wx
from sim_desk.mgr.context import SimDeskContext


class DrawPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.parent = parent
        self.mainframe = SimDeskContext().get_main_frame()
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_event)
        self.SetMinSize(wx.Size(1024, 768))
        self.SetMaxSize(wx.Size(1024, 768))
        self.SetDoubleBuffered(True)
        self.imageobj = None
        self.current_region = None

    def on_mouse_event(self, event):
        from sim_desk.models.ImageModel import EDIT_MODE_MOVING, EDIT_MODE_RESIZING_XY, EDIT_MODE_RESIZING_X, \
            EDIT_MODE_RESIZING_Y
        if self.imageobj is None:
            event.Skip()
        else:
            if event.Moving():
                pos = event.GetPosition()
                if self.imageobj.getRegion(pos.x, pos.y) is None:
                    self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))
                if self.current_region is not None:
                    if self.current_region.inRange(pos.x, pos.y):
                        self.current_region.editmode = EDIT_MODE_MOVING
                        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
                    elif self.current_region.inAnchor1(pos.x,pos.y):
                        self.current_region.editmode = EDIT_MODE_RESIZING_XY
                        self.SetCursor(wx.Cursor(wx.CURSOR_SIZENWSE))
                    elif self.current_region.inAnchor2(pos.x, pos.y):
                        self.current_region.editmode = EDIT_MODE_RESIZING_Y
                        self.SetCursor(wx.Cursor(wx.CURSOR_SIZENS))
                    elif self.current_region.inAnchor3(pos.x, pos.y):
                        self.current_region.editmode = EDIT_MODE_RESIZING_X
                        self.SetCursor(wx.Cursor(wx.CURSOR_SIZEWE))

            if event.ButtonDown():
                pos = event.GetPosition()
                region = self.imageobj.getRegion(pos.x, pos.y)
                if region is not None:
                    region.mouse_pos = pos
                    self.current_region = region
                    self.imageobj.deselect_all()
                    self.imageobj.select_region(self.current_region)
                else:
                    self.imageobj.deselect_all()
                    from sim_desk.models.ImageModel import FeatureRectModel
                    self.current_region = FeatureRectModel(self.imageobj)

                    self.current_region.set_region(pos.x,pos.y,0,0)

                    self.current_region.editmode = EDIT_MODE_RESIZING_XY

            if event.ButtonUp():
                pass

            if event.Dragging():
                if self.current_region is not None:
                    pos = event.GetPosition()
                    if self.current_region.isValid():
                        if self.current_region not in self.imageobj.getModelChildren():
                            self.imageobj.addChild(self.current_region)

                    if self.current_region.editmode == EDIT_MODE_RESIZING_XY:
                        self.current_region.resize(pos.x - self.current_region.x, pos.y - self.current_region.y)

                    elif self.current_region.editmode == EDIT_MODE_RESIZING_X:
                        self.current_region.resize(pos.x - self.current_region.x, self.current_region.height)

                    elif self.current_region.editmode == EDIT_MODE_RESIZING_Y:
                        self.current_region.resize(self.current_region.width, pos.y - self.current_region.y)

                    elif self.current_region.editmode == EDIT_MODE_MOVING:
                        self.current_region.move(pos.x, pos.y)

    def on_paint(self, event):
        dc = wx.BufferedPaintDC(self)
        if self.imageobj is not None and self.imageobj.image is not None:
            dc.DrawBitmap(wx.Bitmap(self.imageobj.image), 0, 0)
            for featurereg in self.imageobj.getModelChildren():
                featurereg.draw(dc)
        else:
            dc.Clear()
        event.Skip()


class ImagePanel(wx.ScrolledWindow):
    def __init__(self, parent):
        super().__init__(parent)
        self.canvas_panel = DrawPanel(self)

        self.frameSizer = wx.BoxSizer(wx.VERTICAL)
        self.frameSizer.Add(self.canvas_panel, 0, wx.EXPAND,10)
        self.SetSizer(self.frameSizer)
        self.canvas_panel.SetMinSize(wx.Size(1024, 768))

        self.SetScrollRate(10, 10)
        self.SetVirtualSize(1024, 768)
        self.current_region = None
        self.SetDoubleBuffered(True)
        self.Layout()

    def select_region(self, region):
        if self.canvas_panel.imageobj is not None:
            self.current_region = region

    def load_image(self, imageobj):

        if self.canvas_panel.imageobj is None or self.canvas_panel.imageobj is not imageobj:
            self.canvas_panel.imageobj = imageobj
            self.canvas_panel.current_region = None
            self.Layout()
            self.canvas_panel.Refresh()
        self.canvas_panel.Refresh()


if __name__ == "__main__":
    r1 = wx.Rect(100, 100, 100, 100)
    r2 = wx.Rect(120, 120, 100, 100)
    print(r1.Union(r2))
