from scenario import Scenario
from utils import logger

class Rampmeasure(Scenario):
    """
    This is the scenario implementation for the user to define
    When scenario is started, each command received will be processed by scenario if there is
    on_command_?, where ? is the command name.
    if before_response_? is defined, it will be called back before the response of command ? is sent.
    You can use all functions defined in the Squish lib and Simulator in this scenario file
    by self.squisher and self.simulator
    Example:
    def on_command_abc(self,command_obj):
        received_time = command_obj.time_ns
        command_code = command_obj.code
        field_value = command_obj.xx
        array_element_field = command_obj.xx[1].yy
        self.simulator.set_command_pending_response_by_parameters(command_obj.code,xx=100,yy=200)

    """
    def __init__(self):
        Scenario.__init__(self)
        self.count = 0
        self.temp = 0

    def on_response_SetStimulationSettingCmd(self,response):

         logger.info(str(response.data))


    def on_receive_GetMeasuredChannelsCmd(self,commandobj):
        command_code = commandobj.code
        kw = dict()
        kw["ar_measured_channels[0].u8_TempRefAvailable"] = 1
        kw["ar_measured_channels[0].u16_TempRef"] = self.temp//10
        if self.temp <400:
            self.temp+=5

        elif self.temp > 700:

            self.temp-= 5

        else:

            self.temp+=10
        self.simulator.set_command_pending_response_by_parameters(command_code,**kw)
        #logger.info(str(commandobj))


    def on_receive_GetStatusCmd(self,commandobj):
        command_code = commandobj.code
        if self.count == 0:
            self.simulator.set_command_pending_response_by_parameters(command_code,u8_OutputStatus=1)
        if self.count == 1:
            self.simulator.set_command_pending_response_by_parameters(command_code, u8_OutputStatus=0)
        if self.count == 2:
            self.simulator.set_command_pending_response_by_parameters(command_code, u8_OutputStatus=1)
        self.count+=1
        #logger.info(str(commandobj))

    def on_start(self):
        """
        This will be called when the scenario is started by the Test Executor
        This is called in sync, so it will block the main thread
        :return:
        """
        logger.info("started")

    def on_stop(self):
        """
        This will be called when the scenario is stopped by the Test Executor
        This is called in sync, so it will block the main thread
        :return:
        """
        logger.info("stop")

    def on_response_GetStatusCmd(self,responseObj):
        pass

    def on_response_GetMeasuredChannelsCmd(self,responseObj):
        logger.info(f'u16_TempRef = {responseObj.data.ar_measured_channels[0].u16_TempRef}')