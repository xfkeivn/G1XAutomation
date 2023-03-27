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
Description: This program includes helper functions related to the Sardeen
project. They are aimed to be used by skipper and unit tests
"""
import struct
import re

FIRST_BYTE_MASK = 0x000000FF  # Least significant byte
SECOND_BYTE_MASK = 0x0000FF00
THIRD_BYTE_MASK = 0x00FF0000
FOURTH_BYTE_MASK = 0xFF000000

FIRST_WORD_MASK = 0x0000FFFF  # Least significant word
SECOND_WORD_MASK = 0xFFFF0000

BIT_0_MASK = 0x1
BIT_1_MASK = 0x1 << 1
BIT_2_MASK = 0x1 << 2
BIT_3_MASK = 0x1 << 3
BIT_4_MASK = 0x1 << 4
BIT_5_MASK = 0x1 << 5
BIT_6_MASK = 0x1 << 6
BIT_7_MASK = 0x1 << 7
BIT_8_MASK = 0x1 << 8
BIT_9_MASK = 0x1 << 9
BIT_10_MASK = 0x1 << 10
BIT_11_MASK = 0x1 << 11
BIT_12_MASK = 0x1 << 12
BIT_13_MASK = 0x1 << 13
BIT_14_MASK = 0x1 << 14
BIT_15_MASK = 0x1 << 15
BIT_16_MASK = 0x1 << 16
BIT_17_MASK = 0x1 << 17
BIT_18_MASK = 0x1 << 18
BIT_19_MASK = 0x1 << 19
BIT_20_MASK = 0x1 << 20
BIT_21_MASK = 0x1 << 21
BIT_22_MASK = 0x1 << 22
BIT_23_MASK = 0x1 << 23
BIT_24_MASK = 0x1 << 24
BIT_25_MASK = 0x1 << 25
BIT_26_MASK = 0x1 << 26
BIT_27_MASK = 0x1 << 27
BIT_28_MASK = 0x1 << 28
BIT_29_MASK = 0x1 << 29
BIT_30_MASK = 0x1 << 30
BIT_31_MASK = 0x1 << 31


def generateCrc(buffer, seed=0):
    """
    Generates Crc16Ccitt data (x16 + x12 + x5 + 1 polynomial) based on
    input array and seed. Modeled after current crc implementation
    within Sardeen ROM

    Parameters
    ----------

    input_data: buffer
        Array of bytes that should go through crc

    crc_seed: int
        Initial seed value for crc (defaulted to 0)

    Returns
    -------

    int
        Output 16 bit crc value
    """
    crc = seed
    # swap bytes of crc
    for element in buffer:
        crc = ((crc >> 8) & FIRST_BYTE_MASK) | (crc << 8)
        if isinstance(element, int):
            value = element
        else:
            (value,) = struct.unpack("B", bytes([element]))
        crc ^= value
        crc ^= (crc & FIRST_BYTE_MASK) >> 4
        crc ^= (crc << 8) << 4
        crc ^= ((crc & FIRST_BYTE_MASK) << 4) << 1
        crc &= FIRST_WORD_MASK

    return int(crc)


def generateCrcBytes(msg):
    """
    Calculate Crc16Ccitt of msg and return the CRC in bytearray format.

    Parameters
    ----------
    msg: bytearray
        Array of bytes that should go through crc
    Returns
    -------
    bytearray
        Output 16 bit crc value
    """
    crc = generateCrc(msg)
    return crc.to_bytes(2, "little")


def calculatePearsonHash(data):
    """
    Calculate Pearson Hash of input data.

    Parameter
    ---------
    data: bytearray or bytes

    Returns
    -------
    pearsonHash: int
        Pearson hash
    """
    hashTable = [
        0x62, 0x06, 0x55, 0x96, 0x24, 0x17, 0x70, 0xA4, 0x87, 0xCF, 0xA9, 0x05,
        0x1A, 0x40, 0xA5, 0xDB, 0x3D, 0x14, 0x44, 0x59, 0x82, 0x3F, 0x34, 0x66,
        0x18, 0xE5, 0x84, 0xF5, 0x50, 0xD8, 0xC3, 0x73, 0x5A, 0xA8, 0x9C, 0xCB,
        0xB1, 0x78, 0x02, 0xBE, 0xBC, 0x07, 0x64, 0xB9, 0xAE, 0xF3, 0xA2, 0x0A,
        0xED, 0x12, 0xFD, 0xE1, 0x08, 0xD0, 0xAC, 0xF4, 0xFF, 0x7E, 0x65, 0x4F,
        0x91, 0xEB, 0xE4, 0x79, 0x7B, 0xFB, 0x43, 0xFA, 0xA1, 0x00, 0x6B, 0x61,
        0xF1, 0x6F, 0xB5, 0x52, 0xF9, 0x21, 0x45, 0x37, 0x3B, 0x99, 0x1D, 0x09,
        0xD5, 0xA7, 0x54, 0x5D, 0x1E, 0x2E, 0x5E, 0x4B, 0x97, 0x72, 0x49, 0xDE,
        0xC5, 0x60, 0xD2, 0x2D, 0x10, 0xE3, 0xF8, 0xCA, 0x33, 0x98, 0xFC, 0x7D,
        0x51, 0xCE, 0xD7, 0xBA, 0x27, 0x9E, 0xB2, 0xBB, 0x83, 0x88, 0x01, 0x31,
        0x32, 0x11, 0x8D, 0x5B, 0x2F, 0x81, 0x3C, 0x63, 0x9A, 0x23, 0x56, 0xAB,
        0x69, 0x22, 0x26, 0xC8, 0x93, 0x3A, 0x4D, 0x76, 0xAD, 0xF6, 0x4C, 0xFE,
        0x85, 0xE8, 0xC4, 0x90, 0xC6, 0x7C, 0x35, 0x04, 0x6C, 0x4A, 0xDF, 0xEA,
        0x86, 0xE6, 0x9D, 0x8B, 0xBD, 0xCD, 0xC7, 0x80, 0xB0, 0x13, 0xD3, 0xEC,
        0x7F, 0xC0, 0xE7, 0x46, 0xE9, 0x58, 0x92, 0x2C, 0xB7, 0xC9, 0x16, 0x53,
        0x0D, 0xD6, 0x74, 0x6D, 0x9F, 0x20, 0x5F, 0xE2, 0x8C, 0xDC, 0x39, 0x0C,
        0xDD, 0x1F, 0xD1, 0xB6, 0x8F, 0x5C, 0x95, 0xB8, 0x94, 0x3E, 0x71, 0x41,
        0x25, 0x1B, 0x6A, 0xA6, 0x03, 0x0E, 0xCC, 0x48, 0x15, 0x29, 0x38, 0x42,
        0x1C, 0xC1, 0x28, 0xD9, 0x19, 0x36, 0xB3, 0x75, 0xEE, 0x57, 0xF0, 0x9B,
        0xB4, 0xAA, 0xF2, 0xD4, 0xBF, 0xA3, 0x4E, 0xDA, 0x89, 0xC2, 0xAF, 0x6E,
        0x2B, 0x77, 0xE0, 0x47, 0x7A, 0x8E, 0x2A, 0xA0, 0x68, 0x30, 0xF7, 0x67,
        0x0F, 0x0B, 0x8A, 0xEF,
    ]

    pearsonHash = 0

    for data_byte in data:
        if isinstance(data_byte, int):
            value = data_byte
        else:
            (value,) = struct.unpack("B", data_byte)
        index = pearsonHash ^ value
        pearsonHash = hashTable[index]

    return pearsonHash


def UQmnToFloat(x, n):
    """
    Converts an unsigned number in Qm.n fixed point format to float

    Parameters
    ----------
    x: int
        Q format number to convert
    n: int
        Number of bits designating the fractional portion of x
    Returns
    -------
    float
        Conversion result
    """
    return (1.0 * x) / (2 ** n)


def QmnToFloat(x, n):
    """
    Converts an signed number in Qm.n fixed point format to float

    Parameters
    ----------
    x: int
        Q format number to convert
    n: int
        Number of bits designating the fractional portion of x
    Returns
    -------
    float
        Conversion result
    """
    # convert 16-bit two's complement hex to signed integer
    if x & (1 << 16 - 1):
        x -= 1 << 16
    return (1.0 * x) / (2 ** n)


def remove_whitespace(s):
    """
    Remove white space from a string.

    Parameters
    ----------

    s: string

    Returns
    -------

    String without whitespace

    """
    return re.sub(r'\s', '', s)


def add_spaces_to_hex(hex_string):
    """
    Add one space between hex number in a hex string.

    Parameters
    ----------

    hex_string: string

    Returns
    -------

    String with one space between two hex numbers

    """
    # Remove all existing spaces
    s = remove_whitespace(hex_string)
    # Add new spaces
    s2 = " ".join(s[i:i+2] for i in range(0, len(s), 2))
    return s2
