#!/usr/bin/env python
# encoding: utf-8
"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSCUDSStudio
@file: CommandResponse.py
@time: 2023/3/26 11:35
@desc:
"""
from gx_communication.gx_commands import Response
from  gx_communication import gx_commands
from gx_communication.serializable import *
from sim_desk.models.CommonProperty import *
from sim_desk.ui.images import message_reply, signal, slot, did,message

class CommandResponseModel(TreeModel):
    def __init__(self,parent,label,response_cls):
        TreeModel.__init__(self,parent,label)
        self.image = message_reply
        self.response_obj = response_cls()


        number_value_property = StringProperty('Command Code', 'Command Code',
                                               '%X'% (self.response_obj.u16_ResponseCode-1), editable=False)
        self.addProperties(number_value_property)
        number_value_property = StringProperty('Response Code', 'Response Code',
                                               '%X' % (self.response_obj.u16_ResponseCode), editable=False)
        self.addProperties(number_value_property)



class ElementModel(TreeModel):
    def __init__(self,parent,label,default_value):
        TreeModel.__init__(self,parent,label)
        self.default_value = default_value
        self.image = did



class FieldRecordArrayModel(TreeModel):
    def __init__(self,parent,label,record_type_obj,default_value):
        TreeModel.__init__(self,parent,label)
        self.record_type_obj = record_type_obj
        self.default_value = default_value
        self.image = slot

    def create_default_elements(self):
        if self.default_value is not None and isinstance(self.default_value,list):
            for ele in self.default_value:
                if isinstance(ele,self.record_type_obj):
                    self.create_array_element(ele)

    def create_array_element(self,ele):
        elemnt_model = ElementModel(self,f'{self.record_type_obj.__name__}[{len(self.children_models)}]',ele)
        self.addChild(elemnt_model)
        model_generator = self.getRoot().model_generator
        model_generator.create_field_models(self.record_type_obj, elemnt_model)


class FieldNumberArrayModel(TreeModel):
    def __init__(self,parent,label,default_value):
        TreeModel.__init__(self,parent,label)
        self.image = slot


class FieldStringModel(TreeModel):
    def __init__(self,parent,label,default_value):
        TreeModel.__init__(self,parent,label)
        self.image = message


class FieldNumberModel(TreeModel):
    def __init__(self,parent,label,default_value):
        TreeModel.__init__(self,parent,label)
        self.image = signal
        if 'u16_ResponseCode' == label:
            number_value_property = StringProperty(label, label, '%X'%default_value, editable=False)
        else:
            number_value_property = IntProperty(label, label, default_value, editable=True)

        self.addProperties(number_value_property)


class ResponseModelGenerator():
    def __init__(self,container):
        self.container = container
        self.container.getRoot().model_generator = self

    def create_field_model_record_array(self,parent_model, field_name,field_value,record_type_obj):
        model = FieldRecordArrayModel(parent_model,field_name,record_type_obj,field_value)
        return model

    def create_field_model_number_array(self,parent_model, field_name,field_value):
        model = FieldNumberArrayModel(parent_model, field_name,field_value)
        return model

    def create_field_model_number(self,parent_model, field_name,field_value):
        model = FieldNumberModel(parent_model, field_name,field_value)
        return model

    def create_field_model_string(self,parent_model, field_name,field_value):
        model = FieldStringModel(parent_model, field_name,field_value)
        return model


    def create_field_models(self,response_cls,parent_model):
        response_obj = response_cls()
        response_cls_fields = getSerializableFields(response_obj)

        for field_name in response_cls_fields:
            field_value = getattr(response_obj, field_name)
            if REC_ARRAY_PREFIX == field_name[0: len(UINT8_T_PREFIX)]:
                name_of_record_type = getattr(response_obj, '_arrayTypes').get(field_name)
                record_type_obj = self.get_record_type(name_of_record_type)
                field_model = self.create_field_model_record_array(parent_model, field_name,field_value,record_type_obj)
                parent_model.addChild(field_model)
                field_model.create_default_elements()
            elif field_name[0: len(UINT8_NUM_ARRAY_PREFIX)] in numArrayFieldTypes:
                field_model = self.create_field_model_number_array(parent_model, field_name,field_value)
                parent_model.addChild(field_model)
            elif STRING_PREFIX == field_name[0: len(UINT8_T_PREFIX)]:
                field_model = self.create_field_model_string(parent_model, field_name,field_value)
                parent_model.addChild(field_model)
            else:
                field_model = self.create_field_model_number(parent_model,  field_name,field_value)
                parent_model.addChild(field_model)

        return parent_model


    def create_command_response_models(self,):
        response_classes = []
        for name in dir(gx_commands):
            obj = getattr(gx_commands, name)
            if isinstance(obj, type) and issubclass(obj, Response) and 'Response' not in obj.__name__:
                response_classes.append(obj)
        for response_cls in response_classes:
            model = CommandResponseModel(self.container,response_cls.__name__,response_cls)
            self.container.addChild(model)
            self.create_field_models(response_cls,model)



    def get_record_type(self,record_type_name):
        for name in dir(gx_commands):
            type_obj = getattr(gx_commands, name)
            if isinstance(type_obj, type) and issubclass(type_obj, Serializable):
                if type_obj.__name__ == record_type_name:
                    return type_obj
        return None



