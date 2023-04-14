from utils.singleton import Singleton
from BackPlaneSimulator import BackPlaneSimulator
from squish.squish_proxy import SquishProxy

class ExecutorContext(metaclass=Singleton):
    SIMDESK_CONTEXT = "SimDesk"
    ROBOT_CONTEXT = "Robot"

    def __init__(self):
        self.context_name = None
        self.context = None

    def set_gui_context(self, context):
        self.context_name = ExecutorContext.SIMDESK_CONTEXT
        self.context = context

    def set_robot_context(self, context):
        self.context = context
        self.context_name = ExecutorContext.ROBOT_CONTEXT

    @property
    def squisher_runner(self):
        squisher:SquishProxy = None
        if self.context_name == ExecutorContext.SIMDESK_CONTEXT:
            from sim_desk.mgr.context import SimDeskContext
            squisher = self.context.squisher
        if self.context_name == ExecutorContext.ROBOT_CONTEXT:
            squisher = self.context.squish_proxy
        return squisher

    @property
    def simulator(self):
        simulator:BackPlaneSimulator = None
        if self.context_name == ExecutorContext.SIMDESK_CONTEXT:
            simulator  = self.context.bps
        if self.context_name == ExecutorContext.ROBOT_CONTEXT:
            simulator = self.context.gx1_simulator
        return simulator