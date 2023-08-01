from gx_communication import bsnUtil, byteConverter, constants


def protocol_4_command(payload, crc=True):
    # Protocol 4 ID
    protocol_id = byteConverter.num2bin(0x80, constants.UINT8_FORMAT)
    pass_through = byteConverter.num2bin(0x00, constants.UINT8_FORMAT)
    # size of entire command in bytes
    length = byteConverter.num2bin(len(payload) + 6, constants.UINT16_FORMAT)
    formatted = protocol_id + pass_through + length + payload
    if crc:
        crc_byte_array = bsnUtil.generateCrcBytes(formatted)
        formatted += crc_byte_array
    return formatted


def get_payload(resp):
    length = len(resp)
    # return resp[4: length-2]
    # UI SW seems send less 1
    return resp[4: length - 2]


def build_payload(cmd_dictionary):
    payload_bytes = bytearray()
    for key, value in cmd_dictionary.items():
        data_type = key[0:3]
        if data_type == "u8_":
            payload_bytes += byteConverter.num2bin(
                value, constants.UINT8_FORMAT
            )
        elif data_type == "u16":
            payload_bytes += byteConverter.num2bin(
                value, constants.UINT16_FORMAT
            )
        elif data_type == "u32":
            payload_bytes += byteConverter.num2bin(
                value, constants.UINT32_FORMAT
            )
        else:
            raise Exception("Unknown data type...")
    return payload_bytes
