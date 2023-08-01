#!/usr/bin/env python
# encoding: utf-8
"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: CommandResponse.py
@time: 2023/3/26 11:35
@desc:
"""
from BackPlaneSimulator import BackPlaneSimulator as BPS
from BackPlaneSimulator import CommandResponseFilter
from gx_communication import gx_commands
from gx_communication.gx_commands import Command, Response
from gx_communication.serializable import *
from sim_desk.models.CommonProperty import *
from sim_desk.models.TreeModel import (
    TREEMODEL_STATUS_NORMAL,
    TREEMODEL_STATUS_RUNTIME,
    TreeAction,
)
from sim_desk.ui.images import did, message, message_reply, signal, slot
from utils import logger


class CommandResponseModel(TreeModel):
    def __init__(self, parent, label, response_cls, command_cls):
        TreeModel.__init__(self, parent, label)
        self.image = message_reply
        self.command_node = False
        if isinstance(response_cls(), Command):
            self.command_node = True
        self.response_obj = response_cls()
        self.command_class = command_cls

        if self.command_node is False:
            number_value_property = StringProperty(
                "Command Code",
                "Command Code",
                "%X" % (self.response_obj.u16_ResponseCode - 1),
                editable=False,
            )
            self.addProperties(number_value_property)
            number_value_property = StringProperty(
                "Response Code",
                "Response Code",
                "%X" % (self.response_obj.u16_ResponseCode),
                editable=False,
            )

            self.addProperties(number_value_property)
            logging = BoolProperty("CommandLogging", "CommandLogging")
            self.addProperties(logging)
            logging = BoolProperty("ResponseLogging", "ResponseLogging")
            self.addProperties(logging)
        else:
            number_value_property = StringProperty(
                "Command Code",
                "Command Code",
                "%X" % (self.response_obj.u16_CommandCode),
                editable=False,
            )
            self.addProperties(number_value_property)

    def from_json(self, element):
        TreeModel.from_json(self, element)

        try:
            if self.command_node is False:
                command_logging = (
                    self.getPropertyByName("CommandLogging").getStringValue()
                    == "True"
                )
                response_logging = (
                    self.getPropertyByName("ResponseLogging").getStringValue()
                    == "True"
                )
                response_code = int(
                    self.getPropertyByName("Response Code").getStringValue(),
                    16,
                )
                command_code = int(
                    self.getPropertyByName("Command Code").getStringValue(), 16
                )
                if response_logging:
                    CommandResponseFilter().include_response(response_code)
                else:
                    CommandResponseFilter().exclude_response(response_code)
                if command_logging:
                    CommandResponseFilter().include_command(command_code)
                else:
                    CommandResponseFilter().exclude_command(command_code)
        except Exception as err:
            logger.error(err)

    def updateProperty(self, wxprop):
        TreeModel.updateProperty(self, wxprop)
        if self.command_node is True:
            return
        prop = self.getPropertyBywxprop(wxprop)
        if prop and prop.propertyname == "CommandLogging":
            stringvalue = wxprop.GetValueAsString()
            logging = stringvalue == "True"
            intvalue = int(
                self.getPropertyByName("Command Code").getStringValue(), 16
            )
            if logging:
                CommandResponseFilter().include_command(intvalue)
            else:
                CommandResponseFilter().exclude_command(intvalue)

        if prop and prop.propertyname == "ResponseLogging":
            stringvalue = wxprop.GetValueAsString()
            logging = stringvalue == "True"
            intvalue = int(
                self.getPropertyByName("Response Code").getStringValue(), 16
            )
            if logging:
                CommandResponseFilter().include_response(intvalue)
            else:
                CommandResponseFilter().exclude_response(intvalue)

        return prop

    def set_model_status(self, status):
        if self.command_node is True:
            return
        if status == TREEMODEL_STATUS_RUNTIME:
            command_logging = (
                self.getPropertyByName("CommandLogging").getStringValue()
                == "True"
            )
            response_logging = (
                self.getPropertyByName("ResponseLogging").getStringValue()
                == "True"
            )
            response_code = int(
                self.getPropertyByName("Response Code").getStringValue(), 16
            )
            command_code = int(
                self.getPropertyByName("Command Code").getStringValue(), 16
            )
            if response_logging:
                CommandResponseFilter().include_response(response_code)
            else:
                CommandResponseFilter().exclude_response(response_code)
            if command_logging:
                CommandResponseFilter().include_command(command_code)
            else:
                CommandResponseFilter().exclude_command(command_code)

    def get_script_snippet(self):
        if self.command_node is True:
            return ""
        snippet = (
            f"    def on_receive_{self.command_class.__name__}(self,commandObj):\n"
            f"        pass\n\n"
            f"    def on_response_{self.command_class.__name__}(self,responseObj):\n"
            f"        pass"
        )
        return snippet


class ElementModel(TreeModel):
    def __init__(self, parent, label, default_value):
        TreeModel.__init__(self, parent, label)
        self.default_value = default_value
        self.image = did


class FieldRecordArrayModel(TreeModel):
    def __init__(self, parent, label, record_type_obj, default_value):
        TreeModel.__init__(self, parent, label)
        self.record_type_obj = record_type_obj
        self.default_value = default_value
        self.image = slot

    def create_default_elements(self):
        if self.default_value is not None and isinstance(
            self.default_value, list
        ):
            for ele in self.default_value:
                if isinstance(ele, self.record_type_obj):
                    self.create_array_element(ele)

    def create_array_element(self, ele):
        elemnt_model = ElementModel(
            self, f"[{len(self.children_models)}]", ele
        )
        self.addChild(elemnt_model)
        model_generator = self.getRoot().model_generator
        model_generator.create_field_models(self.record_type_obj, elemnt_model)


class FieldNumberArrayModel(TreeModel):
    def __init__(self, parent, label, default_value):
        TreeModel.__init__(self, parent, label)
        self.image = slot


class FieldStringModel(TreeModel):
    def __init__(self, parent, label, default_value):
        TreeModel.__init__(self, parent, label)
        self.image = message


class FieldNumberModel(TreeModel):
    def __init__(self, parent, label, default_value):
        TreeModel.__init__(self, parent, label)
        self.image = signal
        is_command_code = self.get_command_response().command_node
        if "u16_ResponseCode" == label:
            number_value_property = StringProperty(
                label, label, "%X" % default_value, editable=False
            )
        else:
            number_value_property = IntProperty(
                label, label, default_value, editable=not is_command_code
            )
        if "u16_CommandCode" == label:
            number_value_property = StringProperty(
                label, label, "%X" % default_value, editable=False
            )
        self.addProperties(number_value_property)
        self.tree_action_list.append(
            TreeAction("Copy", wx.ID_HIGHEST + 1010, self.on_copy)
        )

    def get_command_response(self):
        parent = self.parent
        while parent is not None:
            if isinstance(parent, CommandResponseModel):
                return parent
            else:
                parent = parent.parent

    def on_copy(self, evt):
        # Copy the text to the system clipboard
        clipboard = wx.Clipboard.Get()
        text = self.get_parameter_name()[0]
        data = wx.TextDataObject(self.__get_name_without_response_name(text))
        clipboard.SetData(data)

    def __get_name_without_response_name(self, full_name):
        parts = full_name.split(".")
        return ".".join(parts[1:])

    def get_parameter_name(self):
        name_list = []
        parent = self
        command_code = None
        while parent is not None:
            name_list.append(parent.label)
            if isinstance(parent, CommandResponseModel):
                stringvalue = parent.getPropertyByName(
                    "Command Code"
                ).getStringValue()
                command_code = int(stringvalue, 16)
                break
            parent = parent.parent
        reversed_names = list(reversed(name_list))
        full_name = ""
        for index, name in enumerate(reversed_names):
            if not name.startswith("[") and index != 0:
                full_name += "."
            full_name += name
        return full_name, command_code

    def get_script_snippet(self):
        full_text = self.get_parameter_name()[0]
        snippet = f"{self.__get_name_without_response_name(full_text)}"
        return snippet

    def updateProperty(self, wxprop):
        TreeModel.updateProperty(self, wxprop)
        prop = self.getPropertyBywxprop(wxprop)
        if prop:
            stringvalue = wxprop.GetValueAsString()
            intvalue = int(stringvalue)
            if prop.editable:
                parameter_name, command_code = self.get_parameter_name()
                BPS().set_command_pending_response_by_parameters(
                    command_code, **{parameter_name: intvalue}
                )
        return prop


class ResponseModelGenerator:
    def __init__(self, container):
        self.container = container
        self.container.getRoot().model_generator = self

    def create_field_model_record_array(
        self, parent_model, field_name, field_value, record_type_obj
    ):
        model = FieldRecordArrayModel(
            parent_model, field_name, record_type_obj, field_value
        )
        return model

    def create_field_model_number_array(
        self, parent_model, field_name, field_value
    ):
        model = FieldNumberArrayModel(parent_model, field_name, field_value)
        return model

    def create_field_model_number(self, parent_model, field_name, field_value):
        model = FieldNumberModel(parent_model, field_name, field_value)
        return model

    def create_field_model_string(self, parent_model, field_name, field_value):
        model = FieldStringModel(parent_model, field_name, field_value)
        return model

    def create_field_models(self, response_cls, parent_model):
        response_obj = response_cls()
        response_cls_fields = getSerializableFields(response_obj)

        for field_name in response_cls_fields:
            field_value = getattr(response_obj, field_name)
            if REC_ARRAY_PREFIX == field_name[0 : len(UINT8_T_PREFIX)]:
                name_of_record_type = getattr(response_obj, "_arrayTypes").get(
                    field_name
                )
                record_type_obj = self.get_record_type(name_of_record_type)
                field_model = self.create_field_model_record_array(
                    parent_model, field_name, field_value, record_type_obj
                )
                parent_model.addChild(field_model)
                field_model.create_default_elements()
            elif (
                field_name[0 : len(UINT8_NUM_ARRAY_PREFIX)]
                in numArrayFieldTypes
            ):
                field_model = self.create_field_model_number_array(
                    parent_model, field_name, field_value
                )
                parent_model.addChild(field_model)
            elif STRING_PREFIX == field_name[0 : len(UINT8_T_PREFIX)]:
                field_model = self.create_field_model_string(
                    parent_model, field_name, field_value
                )
                parent_model.addChild(field_model)
            else:
                field_model = self.create_field_model_number(
                    parent_model, field_name, field_value
                )
                parent_model.addChild(field_model)

        return parent_model

    def create_command_response_models(
        self,
    ):
        response_classes = []
        response_command_mapping = dict()
        for name in dir(gx_commands):
            cls_obj = getattr(gx_commands, name)
            if (
                isinstance(cls_obj, type)
                and issubclass(cls_obj, Command)
                and "Command" not in cls_obj.__name__
            ):
                response_obj = cls_obj().response
                response_cls_name = response_obj.__class__.__name__
                response_command_mapping[response_cls_name] = cls_obj

        for name in dir(gx_commands):
            obj = getattr(gx_commands, name)
            if (
                isinstance(obj, type)
                and issubclass(obj, Response)
                and "Response" not in obj.__name__
            ):
                response_classes.append(obj)

        for response_cls in response_classes:
            command_cls = response_command_mapping.get(response_cls.__name__)
            model = CommandResponseModel(
                self.container,
                response_cls.__name__,
                response_cls,
                command_cls,
            )
            self.container.addChild(model)
            self.create_field_models(response_cls, model)

        # add the command nodes
        command_classes = []
        for name in dir(gx_commands):
            obj = getattr(gx_commands, name)
            if (
                isinstance(obj, type)
                and issubclass(obj, Command)
                and "Command" not in obj.__name__
            ):
                command_classes.append(obj)

        for command_cls in command_classes:
            # command_cls = response_command_mapping.get(command_cls.__name__)
            model = CommandResponseModel(
                self.container, command_cls.__name__, command_cls, command_cls
            )
            self.container.addChild(model)
            self.create_field_models(command_cls, model)

    def get_record_type(self, record_type_name):
        for name in dir(gx_commands):
            type_obj = getattr(gx_commands, name)
            if isinstance(type_obj, type) and issubclass(
                type_obj, Serializable
            ):
                if type_obj.__name__ == record_type_name:
                    return type_obj
        return None
