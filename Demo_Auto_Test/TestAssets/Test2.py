from scenario import Scenario



class Test2(Scenario):
    """
    This is the scenario implementation for the user to define
    When scenario is started, each command received will be processed by scenario if there is
    on_receive_?, where ? is the command name.
    if on_response_? is defined, it will be called back before the response of command ? is sent.
    You can use all functions defined in the Squish lib and Simulator in this scenario file
    by self.squisher and self.simulator
    Example:
    def on_receive_abc(self,command_obj):
        received_time = command_obj.time_ns
        command_code = command_obj.code
        field_value = command_obj.xx
        array_element_field = command_obj.xx[1].yy
        self.simulator.set_command_pending_response_by_parameters(command_obj.code,xx=100,yy=200)



    """
    def __init__(self):
        Scenario.__init__(self)
        self.lead_impedance = 0

    def on_start(self):
        """
        This will be called when the scenario is started by the Test Executor
        This is called in sync, so it will block the main thread
        :return:
        """


        pass

    def on_stop(self):
        """
        This will be called when the scenario is stopped by the Test Executor
        This is called in sync, so it will block the main thread
        :return:
        """
        pass


    def on_receive_GetMeasuredChannelsCmd(self,commandObj):

        command_code = commandObj.code
        kw = dict()
        self.lead_impedance += 1
        kw["ar_measured_channels[0].u8_ImpedanceAvailable"] = 1
        kw["ar_measured_channels[0].u16_ImpedanceValue"] = self.lead_impedance%100
        self.simulator.set_command_pending_response_by_parameters(command_code,**kw)

