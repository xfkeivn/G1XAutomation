#!/usr/bin/env python
# encoding: utf-8
"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: GX1
@file: BackPlaneSimulator.py
@time: 2023/3/24 15:02
@desc:
"""
import threading
from queue import Queue
from gx_communication import comport as comp
from gx_communication import gx_commands as commands
import logging
from gx_communication.gx_command_codes import *
from gx_communication import RD1055_format
from gx_communication.bsnUtil import generateCrcBytes
from threading import Thread
from rpc_constants import *
import time
from utils import simple_queue
from logging.handlers import RotatingFileHandler
logger = logging.getLogger("GX1")
logger.setLevel(level=logging.DEBUG)
logger.addHandler(RotatingFileHandler(r'GX1.log'))


# mapping of the command code with the Command
Command_Code_Class_Mapping = {
    WHO_AM_I_CMD: commands.WhoAmICmd,
    SET_ELECTRODE_SETTING_CMD: commands.SetElectrodeSettingCmd,
    GET_ELECTRODE_SETTING_CMD: commands.GetElectrodesCmd,
    SET_STIMULATION_SETTING_CMD: commands.SetStimulationSettingCmd,
    SET_THERMAL_RF_SETTING_CMD: commands.SetThermalRFSettingCmd,
    SET_PULSED_RF_SETTING_CMD: commands.SetPulsedRFSettingCmd,
    CTRL_CONFIG: commands.CtrlConfigCmd,
    GET_FW_IMAGE_PROPERTIES_CMD: commands.GetFwImagePropertiesCmd,
    GET_STATUS: commands.GetStatusCmd,
    GET_MEASURED_CHANNEL: commands.GetMeasuredChannelsCmd,
    CTRL_RESET_TIMER_CMD: commands.CtrlResetTimerCmd,
    SET_IMPEDANCE_VOLUME_CMD: commands.SetImpedanceVolumeCmd,
    CTRL_START_CMD: commands.CtrlStartCmd,
    CTRL_STOP_CMD: commands.CtrlStopCmd,
    BLOCK_CHANNEL_CMD: commands.BlockChannelCmd,
    #CTRL_ADJUST_VOLT: commands.CtrlAdjustOutputCmd,
    CTRL_ADJUST_CURR: None,
    UNIT_TEST_CMD: None,
    GET_STIMULATION_SETTING_CMD: None,
    GET_THERMAL_RF_SETTING_CMD: None,
    GET_PULSED_RF_SETTING_CMD: None,
    CTLR_ADJUST_TEMP: None,
}


def bytes_2_hex(byte_array):
    hex_values = ' '.join(['0x%x' % byte for byte in byte_array])
    return hex_values


def test_crc(self):
    crc = generateCrcBytes([0x80, 0x00, 0x09, 0x00, 0x46, 0xc0, 0x00])
    print(self.bytes_hex_print(crc))


class BackPlaneSimulator(object):
    def __init__(self, ):
        self.com_port = 'COM3'
        self.com_handle = None
        self.receive_thread = None
        self.receive_thread_stop = False
        self.pending_resp_lock = threading.Lock()
        self.command_logging_lock = threading.Lock()
        self.command_response_pending = {}
        self.command_logging = simple_queue.MessageDictQueue()

    def start(self, com_port="COM3"):
        if self.receive_thread is not None and self.receive_thread.is_alive():
            return False
        self.com_port = com_port
        self.com_handle = comp.SerialCmd(self.com_port)
        self.receive_thread = Thread(target=self.__receive_response)
        self.receive_thread_stop = False
        self.receive_thread.start()
        time.sleep(0.1)
        return self.receive_thread.is_alive()

    def stop(self):
        if self.receive_thread is not None and self.receive_thread.is_alive():
            self.receive_thread_stop = True
            self.com_handle.disconnect()
            self.receive_thread.join(1)

        return not self.receive_thread.is_alive()

    def set_command_pending_response(self,command_code, command_response_obj):
        if command_code not in Command_Code_Class_Mapping:
            return RPC_RESULT_COMMAND_CODE_NOT_EXIST
        self.pending_resp_lock.acquire()
        self.command_response_pending[command_code] = command_response_obj
        self.pending_resp_lock.release()
        return RPC_RESULT_SUCCESS

    def set_command_pending_response_by_parameters(self,command_code, **kwargs):
        if command_code not in Command_Code_Class_Mapping:
            return RPC_RESULT_COMMAND_CODE_NOT_EXIST
        self.pending_resp_lock.acquire()

        response_obj = self.command_response_pending.get(command_code)
        if response_obj is None:
            command_class = Command_Code_Class_Mapping.get(command_code)
            response_obj = command_class().response
            self.command_response_pending[command_code] = response_obj
        self.__set_pending_response_filed_values(response_obj,**kwargs)
        self.pending_resp_lock.release()

        return RPC_RESULT_SUCCESS

    def find_logged_command(self, command_code, start_pos=0):
        return self.command_logging.get_all_retain_specific(command_code)

    def clean_logged_command_queue(self):
        self.command_logging.clear()

    def __get_attr(self,key_name,parent_attr):
        if '[' not in key_name:
            return getattr(parent_attr, key_name)
        else:
            start_idx = key_name.find('[')
            end_idx = key_name.find(']')
            attrname = key_name[0:start_idx]
            index = int(key_name[start_idx:end_idx])
            keyattr = getattr(parent_attr, attrname, None)
            if keyattr is None:
                return None
            return keyattr[index]

    def __set_pending_response_filed_values(self,pending_response_obj,**kwargs):
        for key, value in kwargs.items():
            key = key.strip()
            key_parts = key.split('.')
            layers = len(key_parts)
            layer = 0
            upper_layer_attr = pending_response_obj
            layer_attr = None
            for key_part in key_parts:
                layer_attr = self.__get_attr(key_part,upper_layer_attr)
                if layer == layers - 1:
                    break
                else:
                    upper_layer_attr = layer_attr
                layer += 1
            if layer_attr is not None:
                layer_attr = value

    def __logging_command(self, command_code, command_obj):
        self.command_logging.put(command_code,(time.time_ns(),command_obj))

    def __dispatch_command(self, command_obj):
        self.pending_resp_lock.acquire()
        command_pending_response = self.command_response_pending.get(command_obj.u16_CommandCode)
        self.pending_resp_lock.release()
        response_obj = command_obj.response
        if command_pending_response is None:
            self.pending_resp_lock.acquire()
            self.command_response_pending[command_obj.u16_CommandCode] = response_obj
            self.pending_resp_lock.release()
            return response_obj
        else:
            return command_pending_response

    def __receive_response(self):

        while not self.receive_thread_stop:
            response = self.com_handle.get_command()
            if self.receive_thread_stop:
                logger.debug("the thread is stopped")
                break
            if response is None:
                continue
            logger.debug('*' * 100)
            logger.debug('Decoded:' + bytes_2_hex(response))
            payload = RD1055_format.get_payload(response)
            logger.debug('Payload:' + bytes_2_hex(payload))
            cmd_code_bytes = payload[0:2]
            command_code_value = int.from_bytes(cmd_code_bytes, 'little')
            logger.debug('Command Code: %x' % command_code_value + bytes_2_hex(cmd_code_bytes))
            command_class = Command_Code_Class_Mapping.get(command_code_value)
            if command_class is None:
                logger.error('Command Code %X not defined for processing' % command_code_value)
                logger.debug('*' * 100)
                continue
            logger.debug(f'Command {command_class.__name__} is received')
            command_obj = command_class()
            command_obj.deserialize(payload)
            self.__logging_command(command_code_value,command_obj)
            self.com_handle.send_response(self.__dispatch_command(command_obj))
            logger.debug('*' * 100)

