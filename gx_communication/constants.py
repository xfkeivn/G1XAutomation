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

"""
Description: Contains constants related to commands for Sardeen.
"""

from enum import IntEnum


MARLIN_DEV_NAME = "Marlin Device"
STIMULATOR_DEV_NAME = "Marlin Hybrid"
DONGLE_DEV_NAME = "R2F Dongle"


class DevIds(IntEnum):
    """
    WhoAmICmd IDs of devices supported by Skipper and TestRunner.
    """

    r2f_dongle = 0x05
    marlin_hybrid = 0x06


DevIdsToName = {
    DevIds.r2f_dongle: DONGLE_DEV_NAME,
    DevIds.marlin_hybrid: STIMULATOR_DEV_NAME,
}

WHO_AM_I_CMD = bytearray(b"\x80\x00\x08\x00\xfe\xb0")
WHO_AM_I_CMD_RESP = bytearray(b"\xff\xb0")
WHO_AM_I_DEV_ID_OFFSET = 8

FWD_SARDEEN_CMD_CODE = 0x01C4
TRAWLER_READ_CMD_CODE = 0x01
TRAWLER_WRITE_CMD_CODE = 0x02
TRAWLER_READ_DATA_OFFSET = 15
TRAWLER_READ_DATA_LEN = 4

TRANSPORT_CODE = 0x80
TRANSPORT_CODE_LEN = 1
TRANSPORT_CODE_OFFSET = 0
BRIDGE_BYTE = 0x40
RESERVED = 0x00
RESERVED_LEN = 1
RESP_CODE_OFFSET = 4
RESP_CODE_LEN = 2
RESP_ERR_CODE_OFFSET = 6
RESP_ERR_CODE_LEN = 2
CMD_CRC_LEN = 2
CMD_LENGTH_LEN = 2
CMD_LENGTH_OFFSET = 2
CMD_PREFIX_LEN = TRANSPORT_CODE_LEN + RESERVED_LEN + CMD_LENGTH_LEN
RESPONSE_PREFIX_LEN = (
    TRANSPORT_CODE_LEN + RESERVED_LEN + CMD_LENGTH_LEN + RESP_CODE_LEN
)

MIN_RESP_LEN = 10
MAX_SEND_CMD_RETRIES = 5
RX_START_TIMEOUT = 6
MAX_MSG_LEN = 511

CMD_ERR_NONE = 0x0000

MIN_RAW_RESP_LEN = 4
SCS3_CMD_LENGTH_OFFSET = 1

UINT8_FORMAT = '02x'
UINT16_FORMAT = '04x'
UINT32_FORMAT = '08x'

WHO_AM_I_RESP = b'\x80\x00\x13\x00\xFF\xB0\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\xF6'
