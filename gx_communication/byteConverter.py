import binascii
import struct

from gx_communication import constants


def bytes_flip(byte_array):
    little_endian_list = []
    for i in range(0, len(byte_array), 2):
        little_endian_list.insert(0, byte_array[i: i + 2])
    lit_e_bytes = b""
    temp = lit_e_bytes.join(little_endian_list)
    return temp


def num2bytes(num, num_format, endian="little"):
    hex_str = format(num, num_format)
    hex_bytes = bytearray(hex_str, "ascii")
    if endian == "little":
        hex_bytes = bytes_flip(hex_bytes)
    return hex_bytes


def bytes2num(hex_bytes, endian="little"):
    if endian == "little":
        hex_bytes = bytes_flip(hex_bytes)
    return int(hex_bytes, 16)


def bin2asciihex(binarray):
    return bytearray(binarray.hex(), "ascii")


def asciihex2bin(asciihex):
    return binascii.unhexlify(asciihex)


def num2bin(num, num_format, endian="little"):
    if num_format == constants.UINT8_FORMAT:
        char_format = "B"
    elif num_format == constants.UINT16_FORMAT:
        char_format = "H"
    elif num_format == constants.UINT32_FORMAT:
        char_format = "I"
    else:
        raise Exception("Char_format is not valid...")
    return struct.pack(char_format, num)
