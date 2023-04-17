import queue

from executor_context import ExecutorContext as exeContext
from squish.squish_proxy import SquishProxy
from BackPlaneSimulator import BackPlaneSimulator
from threading import Thread
from BackPlaneSimulator import Command_Code_Class_Mapping
from utils import logger

class Scenario(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.context = exeContext()
        self.queue = queue.Queue()
        self.object_methods = [method_name for method_name in dir(self)
                          if callable(getattr(self, method_name)) and method_name.startswith("on_")]
        self.command_callbacks = dict()
        self.response_callbacks = dict()
        self.command_code_name_mapping = dict()
        self.command_name_code_mapping = dict()
        self.response_code_name_mapping = dict()
        self.response_name_code_mapping = dict()
        self.__scenario_started = False
        for command_code, command_cls in Command_Code_Class_Mapping.items():
            self.command_code_name_mapping[command_code] = command_cls.__name__
            self.command_name_code_mapping[command_cls.__name__] = command_code
            self.response_code_name_mapping[command_code] = command_cls.__name__
            self.response_name_code_mapping[command_cls.__name__] = command_code

        for method in self.object_methods:
            if method.startswith("on_receive_"):
                command_name = method[11:]
                command_code = self.command_name_code_mapping.get(command_name)
                self.command_callbacks[command_code] = method
            if method.startswith("on_response_"):
                command_name = method[12:]
                command_code = self.response_name_code_mapping.get(command_name)
                self.response_callbacks[command_code] = method

    @property
    def squisher(self):
        squish_runner:SquishProxy = self.context.squisher_runner
        return squish_runner

    @property
    def simulator(self):
        bps:BackPlaneSimulator = self.context.simulator
        return bps

    def run(self) -> None:
        while True:
            self.queue.get()

    def start_scenario(self):
        if hasattr(self,"on_start"):
            self.on_start()
        self.__scenario_started = True

    def stop_scenario(self):
        if hasattr(self, "on_stop"):
            self.on_stop()
        self.__scenario_started = False

    def on_command_received(self,command_obj):
        if self.__scenario_started is False:
            return
        command_code = command_obj.u16_CommandCode
        callback_method = self.command_callbacks.get(command_code)
        if callback_method is not None:
            getattr(self, callback_method)(command_obj)

    def on_command_responsed(self, response_obj):
        if self.__scenario_started is False:
            return
        response_code = response_obj.u16_ResponseCode
        command_code = response_code - 1
        callback_method = self.response_callbacks.get(command_code)
        if callback_method is not None:
            getattr(self, callback_method)(response_obj)


