"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: ImageModel.py
@time: 2023/3/26 11:35
@desc:
"""
from sim_desk.models.CommonProperty import *
from sim_desk.models.TreeModel import *
from sim_desk.ui.images import *
from sim_desk.mgr.context import SimDeskContext
from sim_desk.ui.ImagePanel import ImagePanel
import os
from executor_context import ExecutorContext

EDIT_MODE_MOVING = 0
EDIT_MODE_RESIZING_XY = 1
EDIT_MODE_RESIZING_X = 2
EDIT_MODE_RESIZING_Y = 3
ANCHORSIZE = 10


class FeatureRectModel(TreeModel):
    DETECTION_TYPE_OCR = 1
    DETECTION_TYPE_STRUCTURE_SIMILARITY = 2
    DETECTION_TYPE_PIXEL_SIMILARITY = 3

    def set_region(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

    def get_region(self):
        return self.x, self.y, self.width, self.height

    def __init__(self, parent, name=''):
        TreeModel.__init__(self, parent, name)
        model_len = len(parent.getModelChildren())
        self.label = f'Rect{model_len}'
        alias_prop = StringProperty("Alias", "Alias", editable=True)
        alias_prop.setSavable(True)
        self.addProperties(alias_prop)
        alias_prop.setStringValue(self.label)

        self.region_prop = StringProperty("Region", "Region", editable=False)
        self.region_prop.setSavable(True)
        self.addProperties(self.region_prop)
        feature_type = EnumProperty("FeatureType", "FeatureType",
                                    enumstrs=["OCR", "STRUCTURE_SIMILARITY", "PIXEL2PIXEL"],
                                    enumvalues=[0, 1, 2])
        self.addProperties(feature_type)
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.feature_type = self.DETECTION_TYPE_OCR
        self.editmode = EDIT_MODE_RESIZING_XY
        self.mouse_pos = None
        self.selected = False
        self.image_rect = wx.Rect(0, 0, 1024, 768)
        # self.font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        self.tree_action_list.append(
            TreeAction("Remove", wx.ID_HIGHEST + 1011, self.remove_self))

    def getImage(self):
        return flex

    def remove_self(self, event):
        dlg = wx.MessageDialog(self.getProject_Tree(), 'Please Confirm to delete',
                               'Confirm to delete',
                               # wx.OK | wx.ICON_INFORMATION
                               wx.YES_NO | wx.ICON_INFORMATION
                               )
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            self.remove()
        SimDeskContext().get_image_feature_panel().canvas_panel.Refresh()
        dlg.Destroy()

    def from_json(self, element):
        TreeModel.from_json(self, element)
        self.x, self.y, self.width, self.height = eval(self.region_prop.getStringValue())

    def to_json(self):
        self.region_prop.stringvalue = (f'({self.x},{self.y},{self.width},{self.height})')
        return TreeModel.to_json(self)

    def setName(self, name):
        self.name = name

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False

    def isValid(self):
        return self.width > 10 and self.height > 10

    def __getAnchors(self):
        anchor_1_x = self.x + self.width - ANCHORSIZE / 2
        anchor_1_y = self.y + self.height - ANCHORSIZE / 2
        anchor_1_rect = wx.Rect(anchor_1_x, anchor_1_y, ANCHORSIZE, ANCHORSIZE)
        anchor_2_x = self.x + self.width / 2 - ANCHORSIZE / 2
        anchor_2_y = self.y + self.height - ANCHORSIZE / 2
        anchor_2_rect = wx.Rect(anchor_2_x, anchor_2_y, ANCHORSIZE, ANCHORSIZE)
        anchor_3_x = self.x + self.width - ANCHORSIZE / 2
        anchor_3_y = self.y + self.height / 2 - ANCHORSIZE / 2
        anchor_3_rect = wx.Rect(anchor_3_x, anchor_3_y, ANCHORSIZE, ANCHORSIZE)
        return anchor_1_rect, anchor_2_rect, anchor_3_rect

    def draw(self, dc):
        gcdc = wx.GraphicsContext.Create(dc)
        if self.selected:
            gcdc.SetPen(wx.RED_PEN)  # for drawing lines / borders__getAnchors
            anchor_1_rect, anchor_2_rect, anchor_3_rect = self.__getAnchors()
            gcdc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, alpha=255)))
            gcdc.DrawRectangle(*anchor_1_rect)
            gcdc.DrawRectangle(*anchor_2_rect)
            gcdc.DrawRectangle(*anchor_3_rect)
        else:
            gcdc.SetPen(wx.YELLOW_PEN)  # for drawing lines / borders
        yellowbrush = wx.Brush(wx.Colour(0, 0, 0, alpha=90))
        gcdc.SetBrush(yellowbrush)  # Yellow fill
        gcdc.DrawRectangle(self.x, self.y, self.width, self.height)
        name = self.getPropertyByName("Alias").getStringValue()
        dc.SetTextForeground(wx.BLUE)
        w, h = SimDeskContext().get_image_feature_panel().canvas_panel.GetTextExtent(name)
        dc.DrawText(name or "", self.x + self.width / 2 - w / 2, self.y + self.height / 2 - h / 2)

    def inRange(self, x, y):

        rect = wx.Rect(self.x, self.y, self.width, self.height)
        anchor_1_rect, anchor_2_rect, anchor_3_rect = self.__getAnchors()
        return rect.Contains(x, y)

    def inAnchor1(self, x, y):
        anchor_1_rect, anchor_2_rect, anchor_3_rect = self.__getAnchors()
        return anchor_1_rect.Contains(x, y)

    def inAnchor2(self, x, y):
        anchor_1_rect, anchor_2_rect, anchor_3_rect = self.__getAnchors()
        return anchor_2_rect.Contains(x, y)

    def inAnchor3(self, x, y):
        anchor_1_rect, anchor_2_rect, anchor_3_rect = self.__getAnchors()
        return anchor_3_rect.Contains(x, y)

    def resize(self, width, height):
        if width < 2 * ANCHORSIZE: width = 2 * ANCHORSIZE
        if height < 2 * ANCHORSIZE: height = 2 * ANCHORSIZE
        updatew = max(self.width, width)
        updateh = max(self.height, height)
        self.width = width
        self.height = height
        SimDeskContext().get_image_feature_panel().canvas_panel.RefreshRect(
            wx.Rect(self.x, self.y, updatew, updateh).Inflate(ANCHORSIZE, ANCHORSIZE))

    def refresh(self):
        SimDeskContext().get_image_feature_panel().canvas_panel.RefreshRect(
            wx.Rect(self.x, self.y, self.width, self.height).Inflate(ANCHORSIZE, ANCHORSIZE))

    def move(self, x, y):
        r1 = wx.Rect(self.x, self.y, self.width, self.height)
        deltx = x - self.mouse_pos.x
        delty = y - self.mouse_pos.y
        newx = self.x + deltx
        newy = self.y + delty
        if newx < 0: newx = 0
        if newy < 0: newy = 0
        if self.image_rect.Contains(wx.Rect(newx, newy, self.width, self.height)):
            self.x = newx
            self.y = newy
            r2 = wx.Rect(x, y, self.width, self.height)
            r = r1.Union(r2)
            self.mouse_pos = wx.Point(x, y)
            SimDeskContext().get_image_feature_panel().canvas_panel.RefreshRect(r.Inflate(10, 10))

    def on_activate(self):
        TreeModel.on_activate(self)
        if not ExecutorContext().is_robot_context():
            self.region_prop.setStringValue((f'({self.x},{self.y},{self.width},{self.height})'))


class ImageModel(TreeModel):
    def __init__(self, parent, file_path):
        TreeModel.__init__(self, parent, os.path.basename(file_path))
        self.filepath = file_path
        if self.filepath is not None:
            self.label = os.path.basename(self.filepath)

        name_prop = StringProperty("Name", "Name", editable=False)
        name_prop.setSavable(False)
        self.addProperties(name_prop)

        name_prop.setStringValue(self.label)
        alias_prop = StringProperty("Alias", "Alias", editable=True)
        alias_prop.setSavable(True)
        self.addProperties(alias_prop)

        path_prop = StringProperty("Path", "Path", editable=False)
        path_prop.setSavable(True)
        self.addProperties(path_prop)
        path_prop.setStringValue(self.filepath)
        self.image_object = None
        self.tree_action_list.append(
            TreeAction("Remove", wx.ID_HIGHEST + 1011, self.remove_self))
        self.path = path_prop.getStringValue()
        self.image = None

    def deselect_all(self):
        for rect in self.getModelChildren():
            if rect.selected is True:
                rect.selected = False
                rect.refresh()

    def from_json(self, element):
        if element.get('sub_models') is not None:
            for name, module in element['sub_models'].items():
                feature_model = FeatureRectModel(self)
                self.addChild(feature_model)
        TreeModel.from_json(self, element)

    def on_activate(self):
        TreeModel.on_activate(self)
        if not ExecutorContext().is_robot_context():
            self.image = wx.Image(self.path, wx.BITMAP_TYPE_ANY)
            SimDeskContext().get_image_feature_panel().load_image(self)
            SimDeskContext().get_main_frame().show_feature_annotation_page()

    def getImage(self):
        return flex

    def populate(self):
        if not ExecutorContext().is_robot_context():
            imagepanel: ImagePanel = SimDeskContext().get_image_feature_panel()
            imagepanel.load_image(self)

    def remove_self(self, event):
        dlg = wx.MessageDialog(self.getProject_Tree(), 'Please Confirm to delete',
                               'Confirm to delete',
                               # wx.OK | wx.ICON_INFORMATION
                               wx.YES_NO | wx.ICON_INFORMATION
                               )
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            path = self.getPropertyByName("Path").getStringValue()
            if os.path.exists(path):
                os.remove(path)
            self.remove()
            SimDeskContext().get_image_feature_panel().canvas_panel.Refresh()
            SimDeskContext().get_image_feature_panel().canvas_panel.imageobj = None

        dlg.Destroy()

    def get_region(self, x, y):
        for region_model in self.getModelChildren():
            flag = region_model.inRange(x, y) or region_model.inAnchor1(x, y) or region_model.inAnchor2(x,
                                                                                                        y) or region_model.inAnchor3(
                x, y)
            if flag:
                return region_model
        return None

    def select_region(self, region):

        SimDeskContext().get_image_feature_panel().select_region(region)
        region.on_activate()
        region.select()
        region.refresh()
