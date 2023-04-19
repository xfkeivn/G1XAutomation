import wx
import wx.lib.scrolledpanel as scrolled
import os


class ImagePanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        scrolled.ScrolledPanel.__init__(self, parent)
        self.canvas_panel = wx.Panel(self)
        self.frameSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.frameSizer.Add(self.canvas_panel, 1, wx.EXPAND)
        self.SetSizer(self.frameSizer)
        self.Layout()
        self.canvas_panel.Bind(wx.EVT_PAINT, self.onPaint)
        self.canvas_panel.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse_event)
        self.SetAutoLayout(1)
        self.SetupScrolling()
        self.imageobj = None
        self.current_region = None
        self.all_regions = []
        self.SetDoubleBuffered(True)

    def deleteRegion(self,uid):
        for region in self.imageobj.feature_regions:
            config = self.imageobj.rect_config_map[region]
            if config.get('uuid') == uid:
                self.imageobj.feature_regions.remove(region)
                region.refresh()
                break

    def deleteImage(self, uid):
        if self.imageobj is not None:
            if self.imageobj.imageconfig['uuid'] == uid:
                self.imageobj = None

    def selectRegion(self,region):
        if self.imageobj is not None:
            self.current_region = region

    def on_mouse_event(self, event):
        from sim_desk.models.ImageModel import EDIT_MODE_MOVING, EDIT_MODE_RESIZING_XY, EDIT_MODE_RESIZING_X, \
            EDIT_MODE_RESIZING_Y
        if self.imageobj is None:
            event.Skip()
        else:
            if event.Moving():
                pos = event.GetPosition()
                if self.imageobj.getRegion(pos.x, pos.y) is None:
                    self.canvas_panel.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))
                if self.current_region is not None:
                    if self.current_region.inRange(pos.x, pos.y):
                        self.current_region.editmode = EDIT_MODE_MOVING
                        self.canvas_panel.SetCursor(wx.Cursor(wx.CURSOR_HAND))
                    elif self.current_region.inAnchor1(pos.x,pos.y):
                        self.current_region.editmode = EDIT_MODE_RESIZING_XY
                        self.canvas_panel.SetCursor(wx.Cursor(wx.CURSOR_SIZENWSE))
                    elif self.current_region.inAnchor2(pos.x, pos.y):
                        self.current_region.editmode = EDIT_MODE_RESIZING_Y
                        self.canvas_panel.SetCursor(wx.Cursor(wx.CURSOR_SIZENS))
                    elif self.current_region.inAnchor3(pos.x, pos.y):
                        self.current_region.editmode = EDIT_MODE_RESIZING_X
                        self.canvas_panel.SetCursor(wx.Cursor(wx.CURSOR_SIZEWE))

            if event.ButtonDown():
                pos = event.GetPosition()
                region = self.imageobj.getRegion(pos.x, pos.y)
                if region is not None:
                    region.mouse_pos = pos
                    self.current_region = region
                    self.imageobj.selectRegion(self.current_region)
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

    def loadImage(self, imageobj):
        w,h = imageobj.image.GetWidth(),imageobj.image.GetHeight()
        self.SetSizeWH(w,h)
        if self.imageobj is None or self.imageobj is not imageobj:
            self.imageobj = imageobj
            self.canvas_panel.SetSizeHints(imageobj.image.GetWidth(), imageobj.image.GetHeight())
            self.Layout()
            self.SetupScrolling()
            self.canvas_panel.Refresh()

    def onPaint(self, event):
        dc = wx.BufferedPaintDC(self.canvas_panel)
        #dc = wx.PaintDC(self.canvas_panel)  # Must create a PaintDC.
        # Get the working rectangle we can draw in
        if self.imageobj is not None:
            dc.DrawBitmap(wx.Bitmap(self.imageobj.image), 0, 0)
            for featurereg in self.imageobj.getModelChildren():
                featurereg.draw(dc)
        event.Skip()


if __name__ == "__main__":
    r1 = wx.Rect(100, 100, 100, 100)
    r2 = wx.Rect(120, 120, 100, 100)
    print(r1.Union(r2))
