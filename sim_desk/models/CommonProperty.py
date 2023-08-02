"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: CommonProperty.py
@time: 2023/3/26 11:35
@desc:
"""
import wx
import wx.propgrid as wxpg

from sim_desk.models.TreeModel import TreeModel


class CommonProperty(TreeModel):
    def __init__(
        self,
        name,
        label=None,
        defaultvalue=wx.EmptyString,
        category=None,
        editable=True,
    ):
        TreeModel.__init__(self, None, name)
        self.propertyname = name
        self.propertylabel = None
        self.default_value = defaultvalue
        self.wxproperty = None
        self.editable = editable
        if label == None:
            self.propertylabel = self.propertyname
        else:
            self.propertylabel = label
        self.category = category
        self.savable = True

    def add_listener(self, prop_listener):
        self.prop_listener = prop_listener

    def setSavable(self, savable):
        self.savable = savable

    def isSavable(self):
        return self.savable

    def getCategory(self):
        return self.category

    def getName(self):
        return self.propertyname

    def getLabel(self):
        return self.propertylabel

    def setStringValue(self, stringvalue):
        self.stringvalue = stringvalue
        if self.wxproperty:
            self.wxproperty.SetValueFromString(self.stringvalue)

    def getSaveString(self):
        return self.getStringValue()

    def getStringValue(self):
        return self.stringvalue

    def getWxProperty(self):
        return self.wxproperty

    def to_json(self):
        ele = {"name": self.propertyname, "value": self.getSaveString()}
        return ele

    def from_json(self, element):
        self.stringvalue = element.get("value")

    def createwxproperty(self):
        raise Exception("not implementation")

    def isEditable(self):
        return self.editable


class StringProperty(CommonProperty):
    def __init__(
        self,
        name,
        label=None,
        defaultvalue=wx.EmptyString,
        category=None,
        editable=True,
    ):
        CommonProperty.__init__(
            self, name, label, defaultvalue, category, editable
        )
        self.stringvalue = defaultvalue

    def createwxproperty(self):
        self.wxproperty = wxpg.StringProperty(
            self.propertylabel, self.propertyname, self.getStringValue()
        )
        self.wxproperty.Enable(self.isEditable())
        return self.wxproperty


class FileProperty(CommonProperty):
    def __init__(
        self, name, label=None, defaultvalue=wx.EmptyString, category=None
    ):
        CommonProperty.__init__(self, name, label, defaultvalue, category)
        self.stringvalue = defaultvalue

    def createwxproperty(self):
        self.wxproperty = wxpg.FileProperty(
            self.propertylabel, self.propertyname, self.getStringValue()
        )
        return self.wxproperty


class BoolProperty(CommonProperty):
    def __init__(self, name, label=None, defaultvalue=True, category=None):
        CommonProperty.__init__(self, name, label, defaultvalue, category)
        self.stringvalue = wxpg.BoolProperty().ValueToString(defaultvalue)

    def createwxproperty(self):
        self.wxproperty = wxpg.BoolProperty(
            self.propertylabel, self.propertyname
        )
        self.wxproperty.SetValueFromString(self.getStringValue())
        return self.wxproperty

    def from_json(self, element):
        stringvalue = element.get("value")
        if stringvalue == "true":
            self.stringvalue = "True"
        else:
            self.stringvalue = "False"

    def setStringValue(self, stringvalue):
        if (
            stringvalue == "1"
            or stringvalue == "true"
            or stringvalue == "True"
        ):
            self.stringvalue = "True"
        if (
            stringvalue == "0"
            or stringvalue == "false"
            or stringvalue == "False"
        ):
            self.stringvalue = "False"

        if self.wxproperty:
            self.wxproperty.SetValueFromString(self.stringvalue)

    def getSaveString(self):
        if self.stringvalue == "True":
            return "true"
        else:
            return "false"


class IntProperty(CommonProperty):
    def __init__(
        self, name, label=None, defaultvalue=0, category=None, editable=True
    ):
        CommonProperty.__init__(
            self, name, label, defaultvalue, category, editable
        )
        self.stringvalue = wxpg.IntProperty().ValueToString(defaultvalue)

    def createwxproperty(self):
        self.wxproperty = wxpg.IntProperty(
            self.propertylabel, self.propertyname
        )
        self.wxproperty.SetValueFromString(self.getStringValue())
        self.wxproperty.Enable(self.isEditable())
        return self.wxproperty


class FloatProperty(CommonProperty):
    def __init__(
        self, name, label=None, defaultvalue=0, category=None, editable=True
    ):
        CommonProperty.__init__(
            self, name, label, defaultvalue, category, editable
        )
        self.stringvalue = wxpg.FloatProperty().ValueToString(defaultvalue)

    def createwxproperty(self):
        self.wxproperty = wxpg.FloatProperty(
            self.propertylabel, self.propertyname
        )
        self.wxproperty.SetValueFromString(self.getStringValue())
        self.wxproperty.Enable(self.isEditable())
        return self.wxproperty


class EnumProperty(CommonProperty):
    def __init__(
        self,
        name,
        label=None,
        defaultvalue=0,
        category=None,
        enumstrs=[],
        enumvalues=[],
        writable=False,
    ):
        self.property = (
            wxpg.EditEnumProperty if writable else wxpg.EnumProperty
        )
        CommonProperty.__init__(self, name, label, defaultvalue, category)
        self.stringvalue = self.property().ValueToString(defaultvalue)
        if len(enumstrs) != len(enumvalues):
            raise Exception("The enumstr and values are not equals")
        self.enumstrs = enumstrs
        self.enumvalues = enumvalues

    def getStringValue(self):
        if self.stringvalue == "" and self.enumstrs:
            return self.enumstrs[0]
        return self.stringvalue

    def createwxproperty(self):
        self.wxproperty = self.property(
            self.propertylabel,
            self.propertyname,
            self.enumstrs,
            self.enumvalues,
        )
        self.wxproperty.SetValueFromString(self.getStringValue())
        return self.wxproperty

    def setEnum(self, enumstrs):
        self.enumstrs = enumstrs
        self.enumvalues = list(range(len(self.enumstrs)))

    def setValues(self, enumvalues):
        self.enumvalues = enumvalues

    def from_json(self, element):
        self.strin = element.get("value")
        self.stringvalue = self.strin
        if len(self.enumstrs) > 0:
            if self.stringvalue not in self.enumstrs:
                self.stringvalue = self.enumstrs[0]

        # try:
        #    self.stringvalue = self.enumstrs[int(self.strin)]
        # except Exception as err:
        #    self.stringvalue = self.enumstrs[0]

    def getSaveString(self):
        stringvalue = self.getStringValue()
        return stringvalue
        # index = 0
        # try:
        #    index= self.enumstrs.index(stringvalue)
        # except Exception as err:
        #    index = 0;
        #
        # return "%d"%index


class ColourProperty(CommonProperty):
    def __init__(
        self, name, label=None, defaultvalue=wx.EmptyString, category=None
    ):
        CommonProperty.__init__(self, name, label, defaultvalue, category)
        self.stringvalue = wxpg.ColourProperty().ValueToString(defaultvalue)

    def createwxproperty(self):
        self.wxproperty = wxpg.ColourProperty(
            self.propertylabel, self.propertyname
        )
        self.wxproperty.SetValueFromString(self.getStringValue())
        return self.wxproperty


class FontProperty(CommonProperty):
    def __init__(
        self, name, label=None, defaultvalue=wx.EmptyString, category=None
    ):
        CommonProperty.__init__(self, name, label, defaultvalue, category)
        self.stringvalue = defaultvalue

    def createwxproperty(self):
        self.wxproperty = wxpg.FontProperty(
            self.propertylabel, self.propertyname
        )
        if self.stringvalue != wx.EmptyString:
            self.wxproperty.SetValueFromString(self.getStringValue())
        return self.wxproperty
