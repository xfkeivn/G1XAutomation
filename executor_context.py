"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: executor_context.py
@time: 2023/3/25 20:34
@desc:
"""
from utils.singleton import Singleton


class ExecutorContext(metaclass=Singleton):
    SIMDESK_CONTEXT = "SimDesk"
    ROBOT_CONTEXT = "Robot"

    def __init__(self):
        self.context_name = None
        self.context = None

    def is_robot_context(self):
        return self.context_name == ExecutorContext.ROBOT_CONTEXT

    def set_gui_context(self, context):
        self.context_name = ExecutorContext.SIMDESK_CONTEXT
        self.context = context

    def set_robot_context(self, context):
        self.context = context
        self.context_name = ExecutorContext.ROBOT_CONTEXT

    @property
    def squisher_runner(self):
        from squish.squish_proxy import SquishProxy
        squisher:SquishProxy = None
        if self.context_name == ExecutorContext.SIMDESK_CONTEXT:
            from sim_desk.mgr.context import SimDeskContext
            squisher = self.context.squisher
        if self.context_name == ExecutorContext.ROBOT_CONTEXT:
            squisher = self.context.squish_proxy
        return squisher

    @property
    def simulator(self):
        from BackPlaneSimulator import BackPlaneSimulator
        simulator:BackPlaneSimulator = None
        if self.context_name == ExecutorContext.SIMDESK_CONTEXT:
            simulator  = self.context.bps
        if self.context_name == ExecutorContext.ROBOT_CONTEXT:
            simulator = self.context.gx1_simulator
        return simulator