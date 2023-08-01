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
import logging
import threading
import time
from threading import Thread
from datetime import datetime
import traceback

import wx

from gx_communication import RD1055_format
from gx_communication import comport as comp
from gx_communication import gx_commands as commands
from gx_communication.bsnUtil import generateCrcBytes
from gx_communication.comport import SERIAL_PIPE, SERIAL_PORT
from gx_communication.gx_command_codes import *
from gx_communication.gx_commands import Command as GX1Command
from gx_communication.gx_commands import Response as GX1Response
from utils import logger, simple_queue
from utils.singleton import Singleton

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
    CTRL_ADJUST_VOLT: commands.AdjustVoltageCmd,
    CTRL_ADJUST_CURR: commands.AdjustCurrentCmd,
    UNIT_TEST_CMD: commands.UT_EchoCmd,
    GET_STIMULATION_SETTING_CMD: commands.GetStimulationSettingCmd,
    GET_THERMAL_RF_SETTING_CMD: commands.GetThermalRFSettingCmd,
    GET_PULSED_RF_SETTING_CMD: commands.GetPulsedRFSettingCmd,
    CTRL_ADJUST_TEMP: commands.AdjustTempCmd,
    SET_CPLD_REGISTERS: commands.SetCPLDRegCmd,
    GET_CPLD_REGISTERS: commands.GetCPLDRegCmd,
    SET_IMPEDANCE_SETTING: commands.SetImpedanceSettingCmd,
    GET_IMPEDANCE_SETTING: commands.GetImpedanceSettingCmd,
    LAUNCH_APPLICATION: commands.LaunchApplication,
    LAUNCH_APPLICATION2: commands.LaunchApplication2,
    SET_SYSTEM_VOLUME: commands.SetSystemVolumn,
    GET_SYSTEM_VOLUME: commands.GetSystemVolumn,
}


def bytes_2_hex(byte_array):
    hex_values = " ".join(["0x%x" % byte for byte in byte_array])
    return hex_values


def test_crc(self):
    crc = generateCrcBytes([0x80, 0x00, 0x09, 0x00, 0x46, 0xC0, 0x00])
    print(self.bytes_hex_print(crc))


class MessageWrapper(object):
    def __init__(self, command_obj, time_ns):
        self.sequence = 0
        self.time_ns = time_ns
        self.format_time = datetime.fromtimestamp(self.time_ns / 1e9).strftime('%Y-%m-%d %H:%M:%S.%f')
        self.data = command_obj
        if isinstance(command_obj, GX1Command):
            self.code = command_obj.u16_CommandCode
        else:
            self.code = command_obj.u16_ResponseCode - 1


class CommandResponseFilter(metaclass=Singleton):
    def __init__(self):
        self.command_filter = []
        self.response_filter = []

    def clear(self):
        self.command_filter.clear()
        self.response_filter.clear()

    def exclude_command(self, command_code):
        if command_code not in self.command_filter:
            self.command_filter.append(command_code)

    def include_command(self, command_code):
        if command_code in self.command_filter:
            self.command_filter.remove(command_code)

    def exclude_response(self, response_code):
        if response_code not in self.response_filter:
            self.response_filter.append(response_code)

    def include_response(self, response_code):
        if response_code in self.response_filter:
            self.response_filter.remove(response_code)

    def filter(self, commandobj):
        if isinstance(commandobj.data, GX1Command):
            if commandobj.code in self.command_filter:
                return True
        if isinstance(commandobj.data, GX1Response):
            if commandobj.data.u16_ResponseCode in self.response_filter:
                return True
        return False


class BackPlaneSimulator(metaclass=Singleton):
    def __init__(self):
        self.com_port = "COM3"
        self.com_handle = None
        self.receive_thread = None
        self.receive_thread_stop = False
        self.pending_resp_lock = threading.Lock()
        self.command_response_pending = {}
        self.command_logging = simple_queue.MessageDictQueue()
        self.command_listeners = list()
        self.command_response_filter = CommandResponseFilter()

    def start(self, com_port="COM3", serial_type=SERIAL_PORT):
        # self.command_listeners.clear()
        self.command_logging.clear()
        self.command_response_pending.clear()
        if self.receive_thread is not None and self.receive_thread.is_alive():
            return False
        self.com_port = com_port
        self.com_handle = comp.SerialCmd(self.com_port, serial_type)
        if self.com_handle.connected:
            self.receive_thread = Thread(target=self.__receive_response)
            self.receive_thread_stop = False
            self.receive_thread.start()
            time.sleep(0.1)
            return self.receive_thread.is_alive()
        else:
            return False

    def stop(self):
        self.command_response_filter.clear()
        self.command_listeners.clear()
        self.command_logging.clear()
        self.command_response_pending.clear()
        if self.receive_thread is not None and self.receive_thread.is_alive():
            self.receive_thread_stop = True
            self.com_handle.disconnect()
            self.receive_thread.join(1)

        return not self.receive_thread.is_alive()

    def remove_command_listener(self, listener):
        self.command_listeners.remove(listener)

    def add_command_listener(self, listener):
        if listener not in self.command_listeners:
            self.command_listeners.append(listener)

    def set_command_pending_response(self, command_code, command_response_obj):
        if command_code not in Command_Code_Class_Mapping:
            return False
        self.pending_resp_lock.acquire()
        self.command_response_pending[command_code] = command_response_obj
        self.pending_resp_lock.release()
        return True

    def set_command_pending_response_by_parameters(
        self, command_code, **kwargs
    ):
        if command_code not in Command_Code_Class_Mapping:
            return False
        self.pending_resp_lock.acquire()
        try:
            response_obj = self.command_response_pending.get(command_code)
            if response_obj is None:
                command_class = Command_Code_Class_Mapping.get(command_code)
                response_obj = command_class().response
                self.command_response_pending[command_code] = response_obj
            self.__set_pending_response_filed_values(response_obj, **kwargs)
        except Exception as err:
            logger.error(err)
        self.pending_resp_lock.release()
        return True

    def __match_conditions(self, wrapper_obj, **kwargs):
        message_obj = wrapper_obj.data
        match = True
        for key, value in kwargs.items():
            key = key.strip()
            key_parts = key.split(".")
            if key_parts[0] == message_obj.__class__.__name__:
                key_parts = key_parts[1:]
            layers = len(key_parts)
            layer = 0
            upper_layer_attr = message_obj
            layer_attr = None
            for key_part in key_parts:
                layer_attr = self.__get_attr(key_part, upper_layer_attr)
                if layer == layers - 1:
                    break
                else:
                    upper_layer_attr = layer_attr
                layer += 1
            if layer_attr is not None:
                if isinstance(layer_attr, int):
                    if layer_attr != int(value):
                        return False
        return True

    def find_logged_commands(self, command_code, after_seq_id=-1, **kwargs):
        logged_commands = self.command_logging.get_all_retain_specific(
            command_code
        )
        return [
            logged_command
            for logged_command in logged_commands
            if logged_command.sequence > after_seq_id
            and self.__match_conditions(logged_command, **kwargs)
        ]

    def clean_logged_command_queue(self):
        self.command_logging.clear()

    def __get_attr(self, key_name, parent_attr):
        if "[" not in key_name:
            return getattr(parent_attr, key_name)
        else:
            start_idx = key_name.find("[")
            end_idx = key_name.find("]")
            attrname = key_name[0:start_idx]
            index = int(key_name[start_idx + 1 : end_idx])
            keyattr = getattr(parent_attr, attrname)
            if keyattr is None:
                return None
            return keyattr[index]

    def __set_pending_response_filed_values(
        self, pending_response_obj, **kwargs
    ):
        for key, value in kwargs.items():
            key = key.strip()
            key_parts = key.split(".")
            if key_parts[0] == pending_response_obj.__class__.__name__:
                key_parts = key_parts[1:]
            layers = len(key_parts)
            layer = 0
            upper_layer_attr = pending_response_obj
            layer_attr = None
            for key_part in key_parts:
                layer_attr = self.__get_attr(key_part, upper_layer_attr)
                if layer == layers - 1:
                    break
                else:
                    upper_layer_attr = layer_attr
                layer += 1
            if layer_attr is not None:
                setattr(upper_layer_attr, key_part, value)

    def __process_command(self, command_code, command_obj):
        logged_msg = MessageWrapper(command_obj, time.time_ns())
        for command_listener in self.command_listeners:
            command_listener.on_command_received(logged_msg)
        # Logging
        if self.command_response_filter.filter(logged_msg) is True:
            return
        self.command_logging.put(command_code, logged_msg)
        logger.debug(f"{logged_msg.format_time}:{logged_msg.data}")

    def __process_response(self, command_response_code, response_obj):
        logged_msg = MessageWrapper(response_obj, time.time_ns())
        for command_listener in self.command_listeners:
            command_listener.on_command_responsed(logged_msg)

        # Logging
        if self.command_response_filter.filter(logged_msg) is True:
            return
        self.command_logging.put(command_response_code, logged_msg)
        logger.debug(f"{logged_msg.format_time}:{logged_msg.data}")

    def __dispatch_command(self, command_obj):
        self.pending_resp_lock.acquire()
        command_pending_response = self.command_response_pending.get(
            command_obj.u16_CommandCode
        )
        self.pending_resp_lock.release()
        response_obj = command_obj.response
        if command_pending_response is None:
            self.pending_resp_lock.acquire()
            self.command_response_pending[
                command_obj.u16_CommandCode
            ] = response_obj
            self.pending_resp_lock.release()
            return response_obj
        else:
            return command_pending_response

    def __receive_response(self):
        while not self.receive_thread_stop:
            response = self.com_handle.get_command()
            if self.receive_thread_stop:
                # logger.debug("the thread is stopped")
                break
            if response is None:
                continue
            payload = RD1055_format.get_payload(response)
            cmd_code_bytes = payload[0:2]
            command_code_value = int.from_bytes(cmd_code_bytes, "little")
            command_class = Command_Code_Class_Mapping.get(command_code_value)
            if command_class is None:
                logger.error(
                    "Command Code %X not defined for processing"
                    % command_code_value
                )
                continue
            command_obj = command_class()
            try:
                command_obj.deserialize(payload)
            except Exception as e:
                logger.debug(f"response:{response}")
                logger.error(traceback.format_exc())
                raise e

            self.__process_command(command_code_value, command_obj)
            response_cmd = self.__dispatch_command(command_obj)
            self.com_handle.send_response(response_cmd)
            self.__process_response(
                response_cmd.u16_ResponseCode, response_cmd
            )
