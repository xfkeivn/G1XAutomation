from gx_communication import gx_command_codes
from gx_communication import serializable
from typing import List


class Command(serializable.Serializable, serializable.Deserializable):
    """
    Base class for RD1055 commands.

    Attributes
    ----------
    u16_CommandCode: int
        Command code as defined in Command Protocol
    response: Response
        Instance of corresponding command response class
    """

    # Command overhead: transport code, reserved, len and CRC
    CMD_OVERHEAD_SIZE = 6
    RX_BUFFER_SIZE = 256
    APP_LEVEL_ENCRYPTION_SIZE = 22
    WORD_SIZE = 4
    MAX_CMD_SIZE = RX_BUFFER_SIZE - APP_LEVEL_ENCRYPTION_SIZE

    def __init__(self, commandCode):
        super().__init__()
        super(serializable.Deserializable, self).__init__()
        super(serializable.Serializable, self).__init__()
        self.u16_CommandCode = commandCode
        self.response = None


class Response(serializable.Serializable, serializable.Deserializable):
    """
    Base class for RD1055 command responses.

    Attributes
    ----------
    u16_ResponseCode: int
        Response code as defined in Command Protocol
    u16_ErrorCode: int
        Error code returned in command response
    """

    def __init__(self, commandCode):
        super().__init__()
        super(serializable.Serializable, self).__init__()
        self.u16_ResponseCode = commandCode + 0x1
        self.u16_ErrorCode = 0x0000


class WhoAmICmd(Command):
    """
    Defines Who Am I Command fields as per Command Protocol.
    """

    def __init__(self):
        super().__init__(gx_command_codes.WHO_AM_I_CMD)
        self.response = WhoAmIResp()


class WhoAmIResp(Response):
    """
    Defines Who Am I Command response fields as per Command Protocol.

   Attributes
    ----------
    u8_DeviceId: int
        ID of device
    """

    def __init__(self):
        super().__init__(gx_command_codes.WHO_AM_I_CMD)
        self.u8_DeviceId = 0x00
        self.au8_address = []


class SetSystemVolumn(Command):
    """
    Defines command for configuring electrode settings.
    Attributes
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.SET_SYSTEM_VOLUME)
        self.response = SetSystemVolumnResp()
        self.u8_volumn = 0x00


class SetSystemVolumnResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.SET_SYSTEM_VOLUME)


class GetSystemVolumn(Command):
    """
    Defines command for configuring electrode settings.
    Attributes
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.GET_SYSTEM_VOLUME)
        self.response = GetSystemVolumnResp()


class GetSystemVolumnResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.GET_SYSTEM_VOLUME)
        self.u8_volumn = 0x00


class SetElectrodeSettingCmd(Command):
    """
    Defines command for configuring electrode settings.
    Attributes
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.SET_ELECTRODE_SETTING_CMD)
        self.response = SetElectrodeSettingResp()
        self.u8_ElectrodePairCount = 0x00
        self.au8_Electrodes = []
        self._arrayLengths = {'au8_Electrodes': 8}


class SetElectrodeSettingResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.SET_ELECTRODE_SETTING_CMD)


class GetElectrodesCmd(Command):
    """
    Defines command for getting electrodes.
    Attributes
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.GET_ELECTRODE_SETTING_CMD)
        self.u16_reserved = 0x0000
        self.response = GetElectrodesResp()


class GetElectrodesResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.GET_ELECTRODE_SETTING_CMD)
        self.u8_NumberOfRegisters = 0x00
        self.u16_Electrodes = []


# *****  BW ***
class BlockChannelCmd(Command):
    """
    Defines command for blocking/Unblocking electrode channels.
    Attributes
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.BLOCK_CHANNEL_CMD)
        self.response = BlockChannelResp()
        self.u8_BlockCount = 0x00
        self.au8_BlockedChannels = []
        self._arrayLengths = {'au8_BlockedChannels': 4}


class BlockChannelResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.BLOCK_CHANNEL_CMD)


# *** end BW ****

class SetStimulationSettingCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.SET_STIMULATION_SETTING_CMD)
        self.response = SetStimulationSettingResp()
        self.u8_ControlSetting = 0x00
        self.u8_SensoryMotor = 0x00
        self.u8_Rate = 0x00
        self.u8_Width = 0x00
        self.u8_Amplitude = 0x00
        self.u8_RampSpeed = 0x00
        self.u8_MaxVoltage = 0x00
        self.u8_MaxCurrent = 0x00


class GetStimulationSettingCmd(Command):
    def __init__(self):
        super().__init__(gx_command_codes.GET_STIMULATION_SETTING_CMD)
        self.response = GetStimulationSettingResponse()


class GetStimulationSettingResponse(Response):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.GET_STIMULATION_SETTING_CMD)
        self.u8_ControlSetting = 0x00
        self.u8_SensoryMotor = 0x00
        self.u8_Rate = 0x00
        self.u8_Width = 0x00
        self.u8_Amplitude = 0x00
        self.u8_RampSpeed = 0x00
        self.u8_MaxVoltage = 0x00
        self.u8_MaxCurrent = 0x00


class SetStimulationSettingResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.SET_STIMULATION_SETTING_CMD)


class SetThermalRFSettingCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.SET_THERMAL_RF_SETTING_CMD)
        self.response = SetThermalRFSettingResp()
        self.u8_TRFMode = 0x00
        self.u8_AutoRamp = 0x00
        self.u8_RampRate = 0x00
        self.u16_SetTime = 0x0000
        self.u8_SetTemp = 0x00
        self.u16_StaggerStartTime = 0x0000
        self.u16_ElectrodePower = 0x0000
        self.u16_StepTime = 0x0000
        self.u16_FinalTime = 0x0000
        self.u8_StartTemp = 0x00
        self.u8_StepTempInc = 0x00
        self.u8_FinalTemp = 0x00
        self.u8_SetVoltage = 0x00


class SetThermalRFSettingResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.SET_THERMAL_RF_SETTING_CMD)


class GetThermalRFSettingResp(Response):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.GET_THERMAL_RF_SETTING_CMD)
        self.u8_TRFMode = 0x00
        self.u8_AutoRamp = 0x00
        self.u8_RampRate = 0x00
        self.u16_SetTime = 0x0000
        self.u8_SetTemp = 0x00
        self.u16_StaggerStartTime = 0x0000
        self.u16_ElectrodePower = 0x0000
        self.u16_StepTime = 0x0000
        self.u16_FinalTime = 0x0000
        self.u8_StartTemp = 0x00
        self.u8_StepTempInc = 0x00
        self.u8_FinalTemp = 0x00
        self.u8_SetVoltage = 0x00


class GetThermalRFSettingCmd(Command):
    def __init__(self):
        super().__init__(gx_command_codes.GET_THERMAL_RF_SETTING_CMD)
        self.response = GetThermalRFSettingResp()


class SetPulsedRFSettingCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.SET_PULSED_RF_SETTING_CMD)
        self.response = SetPulsedRFSettingResp()
        self.u8_PRFMode = 0x00
        self.u8_AutoRamp = 0x00
        self.u16_SetTime = 0x0000
        self.u8_MaxTemp = 0x00
        self.u8_PulseRate = 0x00
        self.u16_StaggerStartTime = 0x0000
        self.u16_Voltage = 0x00
        self.u16_PulseWidth = 0x00
        self.u16_ElectrodePower = 0x0000


class SetPulsedRFSettingResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.SET_PULSED_RF_SETTING_CMD)


class GetPulsedRFSettingResp(Response):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.GET_PULSED_RF_SETTING_CMD)
        self.u8_PRFMode = 0x00
        self.u8_AutoRamp = 0x00
        self.u16_SetTime = 0x0000
        self.u8_MaxTemp = 0x00
        self.u8_PulseRate = 0x00
        self.u16_StaggerStartTime = 0x0000
        self.u16_Voltage = 0x00
        self.u16_PulseWidth = 0x00
        self.u16_ElectrodePower = 0x0000


class GetPulsedRFSettingCmd(Command):
    def __init__(self):
        super().__init__(gx_command_codes.GET_PULSED_RF_SETTING_CMD)
        self.response = GetPulsedRFSettingResp()


class GetFwImagePropertiesCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.GET_FW_IMAGE_PROPERTIES_CMD)
        self.response = GetFwImagePropertiesResp()


class GetFwImagePropertiesResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.GET_FW_IMAGE_PROPERTIES_CMD)


class CtrlResetTimerCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.CTRL_RESET_TIMER_CMD)
        self.response = CtrlResetTimerResp()
        self.u8_ChannelSelect = 0x00


class CtrlResetTimerResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.CTRL_RESET_TIMER_CMD)


# BW **********************************************
class CtrlStartCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.CTRL_START_CMD)
        self.response = CtrlStartResp()


class CtrlStartResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.CTRL_START_CMD)


class CtrlStopCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.CTRL_STOP_CMD)
        self.response = CtrlStopResp()


class CtrlStopResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.CTRL_STOP_CMD)


class AdjustVoltageCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.CTRL_ADJUST_VOLT)
        self.response = AdjustVoltageResp()
        self.i16_DeltaVoltage = 0x0000


class AdjustVoltageResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.CTRL_ADJUST_VOLT)


class AdjustCurrentCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.CTRL_ADJUST_CURR)
        self.response = AdjustCurrentResp()
        self.i16_DeltaCurrent = 0x0000


class AdjustCurrentResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.CTRL_ADJUST_CURR)


class AdjustTempCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.CTRL_ADJUST_TEMP)
        self.response = AdjustTempResp()
        self.i16_target_temp = 0x0000


class AdjustTempResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.CTRL_ADJUST_TEMP)


class UT_EchoCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.UNIT_TEST_CMD)
        self.response = UT_EchoResp()
        self.u16_subID = 0x0003
        self.u16_NumberOfBytes = 0x0000
        self.au8_Data = []


class UT_EchoResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.UNIT_TEST_CMD)
        self.u16_subID = 0x0003
        self.u16_NumberOfBytes = 0x0000
        self.au8_Data = []


# end BW ***************************************************


class SetImpedanceVolumeCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.SET_IMPEDANCE_VOLUME_CMD)
        self.response = SetImpedanceVolumeResp()
        self.u8_ImpedanceVolume = 0x00


class SetImpedanceVolumeResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.SET_IMPEDANCE_VOLUME_CMD)


class SetImpedanceSettingCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.SET_IMPEDANCE_SETTING)
        self.response = SetImpedanceSettingResp()
        self.u16_open_circuit_impedance = 0x00
        self.u16_short_circuit_impedance = 0x00


class SetImpedanceSettingResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.SET_IMPEDANCE_SETTING)


class GetImpedanceSettingCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.GET_IMPEDANCE_SETTING)
        self.response = GetImpedanceSettingResp()


class GetImpedanceSettingResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.GET_IMPEDANCE_SETTING)
        self.u16_open_circuit_impedance = 0x00
        self.u16_short_circuit_impedance = 0x00


class SetCPLDRegCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.SET_CPLD_REGISTERS)
        self.response = SetCPLDRegResp()
        self.u16_NumberOfRegisters = 0x0000
        self.u16_Address = 0x0000
        self.u32_RegisterValues = []


class SetCPLDRegResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.SET_CPLD_REGISTERS)


class GetCPLDRegCmd(Command):
    """
    ---------
    """

    def __init__(self):
        super().__init__(gx_command_codes.GET_CPLD_REGISTERS)
        self.response = GetCPLDRegResp()
        self.u16_NumberOfRegisters = 0x0000
        self.u16_Address = 0x0000


class GetCPLDRegResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.GET_CPLD_REGISTERS)
        self.u16_NumberOfRegisters = 0x0000
        self.u16_Address = 0x0000
        self.u32_RegisterValues = []


class CtrlConfigCmd(Command):
    def __init__(self):
        super().__init__(gx_command_codes.CTRL_CONFIG)
        self.response = CtrlConfigResp()
        self.u16_OpenCircuitImpedance = 0x0000
        self.u16_ShortCircuitImpedance = 0x0000
        self.u16_ClientTimeout = 0x0000
        self.u16_DiagnosticClient = 0x0000


class CtrlConfigResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.CTRL_CONFIG)


class GetStatusCmd(Command):
    def __init__(self):
        super().__init__(gx_command_codes.GET_STATUS)
        self.response = GetStatusResp()
        # spec is u16, but the SW UI is u8
        self.u8_reversed = 0x0000


class GetStatusResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.GET_STATUS)
        self.u8_StatusFlags = 0
        self.u16_ChannelStatus = 0
        self.u8_OutputStatus = 0
        self.u8_ButtonStatus = 0


class GetMeasuredChannelsCmd(Command):
    def __init__(self):
        super().__init__(gx_command_codes.GET_MEASURED_CHANNEL)
        self.response = GetMeasuredChannelsResp()
        self.au8_channels = []
        self._arrayLengths = {'au8_channels': 4}


class MeasuredChannelParam(serializable.Serializable):
    def __init__(self):
        serializable.Serializable.__init__(self)
        self.u8_Source = 0
        self.u8_Reference = 0
        self.u8_Blocked = 0
        self.u8_ImpedanceAvailable = 0
        self.u16_ImpedanceValue = 0
        self.u8_TempSourceAvailable = 0
        self.u16_TempSource = 0
        self.u8_TempRefAvailable = 0
        self.u16_TempRef = 0
        self.u16_Timer = 0
        self.u8_ElectricalSummaryAvailable = 0
        self.u16_Current = 0
        self.u16_Voltage = 0
        self.u16_Power = 0
        self.u16_Width = 0

    def __str__(self):
        return serializable.Serializable.__str__(self)


class GetMeasuredChannelsResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.GET_MEASURED_CHANNEL)
        self.ar_measured_channels: List[MeasuredChannelParam] = [MeasuredChannelParam() for i in range(4)]
        self._arrayTypes['ar_measured_channels'] = 'MeasuredChannelParam'


class LaunchApplication(Command):
    def __init__(self):
        super().__init__(gx_command_codes.LAUNCH_APPLICATION)
        self.response = LaunchApplicationResp()
        self.au8_fw_hash_data = [0]*32
        self.au8_cpld_hash_data = [0] * 32
        self._arrayLengths = {'au8_fw_hash_data': 32,'au8_cpld_hash_data':32}

class LaunchApplication2(Command):
    def __init__(self):
        super().__init__(gx_command_codes.LAUNCH_APPLICATION2)
        self.response = LaunchApplicationResp2()
        self.au8_fw_hash_data = [0]*32
        self.au8_cpld_hash_data = [0] * 32
        self.au8_config_hash_data = [0] * 32
        self._arrayLengths = {'au8_fw_hash_data': 32,'au8_cpld_hash_data':32,'au8_config_hash_data':32}


class LaunchApplicationResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.LAUNCH_APPLICATION)


class LaunchApplicationResp2(Response):
    def __init__(self):
        super().__init__(gx_command_codes.LAUNCH_APPLICATION2)


class GetDetailedError(Command):
    def __init__(self):
        super().__init__(gx_command_codes.GET_DETAILED_ERROR)
        self.response = GetDetailedErrorResp()


class GetDetailedErrorResp(Response):
    def __init__(self):
        super().__init__(gx_command_codes.GET_DETAILED_ERROR)
        self.u8_ErrorType = 0
        self.u8_ErrorClass = 0
        self.u16_ErrorId = 0
        self.u8_ElectrodeIsValid = 0
        self.u8_ElectrodeNum = 0
        self.u8_TempIsValid = 0
        self.u8_Temp = 0
        self.u8_SupplementalTempIsValid = 0
        self.u8_SupplementalTemp = 0
        self.u8_ImpedanceIsValid = 0
        self.u16_Impedance = 0
        self.u8_VoltageIsValid = 0
        self.u16_Voltage = 0
        self.u8_CurrentIsValid = 0
        self.u16_Current = 0
        self.u8_PowerIsValid = 0
        self.u16_Power = 0
        self.u16_ErrorDetail = 0
        self.u32_SupplementalInfo = 0
