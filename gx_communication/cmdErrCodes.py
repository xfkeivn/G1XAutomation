# Copyright 2020 Boston Scientific Corporation.
# All rights reserved.
#
# This file and its contents are a product of Boston Scientific
# Corporation.  All software distributed by Boston Scientific
# Neuromodulation is done so under a software license.  This file may
# not be copied or modified without execution of the appropriate
# software license agreement with Boston Scientific Neuromodulation or
# explicit written permission of Boston Scientific Neuromodulation.
# This file is provided as is, with no warranties of any kind including
# the warranties of design, merchantability and fitness for a
# particular purpose, or arising from a course of dealing, usage or
# trade practice.
#
# Boston Scientific Neuromodulation shall have no liability with
# respect to the infringement of copyrights, trade secrets or any
# patents by this file or any part thereof.
#
# In no event will Boston Scientific Neuromodulation be liable for any
# lost revenue or profits or other special, indirect and consequential
# damages, even if Boston Scientific has been advised of the
# possibility of such damages, as a result of the usage of this file
# and software for which this file is a part.


class CmdErrCodes:
    """
    Class with definitions for all the command error codes
    """

    u16_PGM_ERR_START_NUMBER = 0x1100
    u16_DOWNLOAD_ERR_START_NUMBER = 0x1300

    NewFault = 0x4000
    ErrNone = 0x00
    SendResp = 0x00
    InvalidCRC = 0x02
    InvalidDestinationDevType = 0x04
    UnknownCmdOrBadOptionByte = 0x06
    NoRoomInMsgForResp = 0x07
    InvalidPassword = 0x08
    ExpectedMoreParms = 0x0A
    UnsupportedParameter = 0x0D
    ParmOutOfRange = 0x0F
    InvalidFileId = 0x18
    SuspendResponse = 0x19
    NotInDownloadMode = 0x22
    LogFileEmpty = 0x38
    NotLogFileId = 0x39
    TooManyParms = 0x53
    UnitTestFailed = 0x54
    #New for GX1
    InvalidAppHash = 0x80
    InvalidCpldHash = 0x81
    FailedLock = 0x82
    FailedUnlock = 0x83
    NotInIdleMode = 0x84
    PulseStateError = 0x85
    NoElectrodesConfigured = 0x86
    ElectrodeIndexOrRangeError = 0x87
    NoSavedSettings = 0x88
    CmdNotSupported = 0x89
    FailedVoltageMeas = 0x8A
    OffVoltageTooHigh = 0x8B
    WidthOutOfRange = 0x91
    RateOrPeriodOutOfRange = 0x92
    StimPulseTimingOutOfRange = 0x93
    VoltageOutOfRange = 0x94
    CurrentOutOfRange = 0x95
    RampSpeedOutOfRange = 0x96
    ControlSettingOutOfRange = 0x97
    SensoryMotorOutOfRange = 0x98
    TimeParmOutOfRange = 0x99
    StaggerTimeOutOfRange = 0x9A
    TempOutOfRange = 0x9B
    PowerOutOfRange = 0x9C
    RfModeOutOfRange = 0x9D
    AutoRampOutOfRange = 0x9E
    TempSettingOutOfRange = 0x9F
    NoConfigurationData = 0xA0
    Failed = 0xEE


    @staticmethod
    def getErrCodeName(ErrCode):
        """
        Returns the Error code name for a given error code value.

        Attributes
        ----------
            ErrCode: int
                Error code value.

        Returns
        -------
            Error code name.
        """
        errCodeNamesList = [
            a
            for a in dir(CmdErrCodes)
            if (
                not a.startswith("__")
                and not callable(getattr(CmdErrCodes, a))
            )
        ]
        for name in errCodeNamesList:
            if CmdErrCodes.__dict__[name] == ErrCode:
                return name
        return ""
