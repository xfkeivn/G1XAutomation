GENERIC_CMD = 0
GX_COMMAND_START = 0xC000
GX_BOOT_COMMAND_START = 0xC800
GX_TEST_COMMAND_START = 0xCA00

WHO_AM_I_CMD = GX_COMMAND_START + 0

SET_ELECTRODE_SETTING_CMD = GX_COMMAND_START + 0x02
GET_ELECTRODE_SETTING_CMD = GX_COMMAND_START + 0x04
SET_STIMULATION_SETTING_CMD = GX_COMMAND_START + 0x06
GET_STIMULATION_SETTING_CMD = GX_COMMAND_START + 0x08
SET_THERMAL_RF_SETTING_CMD = GX_COMMAND_START + 0x0A
GET_THERMAL_RF_SETTING_CMD = GX_COMMAND_START + 0x0C
SET_PULSED_RF_SETTING_CMD = GX_COMMAND_START + 0x0E
GET_PULSED_RF_SETTING_CMD = GX_COMMAND_START + 0x10
GET_FW_IMAGE_PROPERTIES_CMD = GX_COMMAND_START + 0x1A


CTRL_RESET_TIMER_CMD = GX_COMMAND_START + 0x22
SET_IMPEDANCE_VOLUME_CMD = GX_COMMAND_START + 0x2A

CTRL_START_CMD = GX_COMMAND_START + 0x32
CTRL_STOP_CMD = GX_COMMAND_START + 0x34
BLOCK_CHANNEL_CMD = GX_COMMAND_START + 0x3A
CTRL_ADJUST_TEMP = GX_COMMAND_START + 0x3C
CTRL_ADJUST_VOLT = GX_COMMAND_START + 0x3E
CTRL_ADJUST_CURR = GX_COMMAND_START + 0x40
CTRL_CONFIG = GX_COMMAND_START + 0x42
GET_IMPEDANCE_VOLUME = GX_COMMAND_START + 0x44
GET_STATUS = GX_COMMAND_START + 0x46
GET_MEASURED_CHANNEL = GX_COMMAND_START + 0x48
SET_SYSTEM_VOLUME = GX_COMMAND_START + 0x4A
GET_SYSTEM_VOLUME = GX_COMMAND_START + 0x4C
GET_DETAILED_ERROR = GX_COMMAND_START + 0x4E

SET_IMPEDANCE_SETTING = GX_COMMAND_START + 0x52
GET_IMPEDANCE_SETTING = GX_COMMAND_START + 0x54
# boot commands
FW_UPGRADE_START_CMD = GX_BOOT_COMMAND_START + 0x00
FW_UPGRADE_WRITE_CMD = GX_BOOT_COMMAND_START + 0x02
FW_UPGRADE_END_CMD = GX_BOOT_COMMAND_START + 0x04
LAUNCH_APPLICATION = GX_BOOT_COMMAND_START + 0x06
LAUNCH_APPLICATION2 = GX_BOOT_COMMAND_START + 0x08

# test commands
UNIT_TEST_CMD = GX_TEST_COMMAND_START + 0x00
SET_CPLD_REGISTERS = GX_TEST_COMMAND_START + 0x02
GET_CPLD_REGISTERS = GX_TEST_COMMAND_START + 0x04
MTI_TEST_CMD = GX_TEST_COMMAND_START + 0x06
