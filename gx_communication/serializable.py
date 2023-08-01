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
Description: This program includes the Serializable and Deserializable base
classes that define functions to serialize and deserialize specific data types.
"""

import struct

from gx_communication import errors

from .cmdErrCodes import CmdErrCodes


class Serializable:
    """
    Base class for serializable objects like commands and records.

    Attributes
    ----------
    _arrayLengths: dict
        Utility attribute to store array fields length. To be populated by
        child classes.
    """

    def __init__(self):
        self._arrayLengths = {}
        self._arrayTypes = {}

    def serialize(self):
        """
        Builds a bytestream from the serializable object attributes. The
        serializable attributes have a name starting with a prefix listed in
        validFieldTypes, and based on it, the field is serialized appropriately
        as shown below:

        ================    ============
        Prefix              Field type
        ================    ============
        u8_, u16, u32       Number
        i8_, i16, i32       Number
        au8_, au16, au32    Number array
        ac_                 String
        ar_                 Record array
        ================    ============

        Returns
        -------
        bytearray
           Serializable object bytestream
        """

        bytestream = bytearray()
        for field in getSerializableFields(self):
            fieldValue = getattr(self, field)
            if REC_ARRAY_PREFIX == field[0: len(UINT8_T_PREFIX)]:
                fieldBytes = self._serializeRecordArray(fieldValue)
            elif field[0: len(UINT8_NUM_ARRAY_PREFIX)] in numArrayFieldTypes:
                fieldBytes = self._serializeNumberArray(field, fieldValue)
            elif STRING_PREFIX == field[0: len(UINT8_T_PREFIX)]:
                fieldBytes = self._serializeString(field, fieldValue)
            else:
                fieldBytes = self._serializeNumber(field, fieldValue)
            bytestream = bytearray().join([bytestream, fieldBytes])
        return bytestream

    def _serializeRecordArray(self, recordArray):
        """
        Serializes input record array by going through each element and
        serializing its internal fields.

        Parameters
        ----------
        recordArray: list
            Array of records

        Returns
        -------
        bytearray
            Array bytestream
        """

        fieldBytes = bytearray()
        for recordObj in recordArray:
            recBytes = recordObj.serialize()
            fieldBytes = bytearray().join([fieldBytes, recBytes])
        return fieldBytes

    def _serializeNumberArray(self, arrayFieldName, numberArray):
        """
        Serializes input number array by going through each element and
        serializing it based on its type prefix. The number type in the
        array is extracted from the attribute's name prefix e.g. for "au16",
        the number type is given by substring "u16", and it is used to get the
        struct pack format.

        Parameters
        ----------
        arrayFieldName: str
            Array field name
        numberArray: list
            Array of numbers

        Returns
        -------
        bytearray
            Array bytestream
        """

        fieldBytes = bytearray()
        (fieldFormat, fieldLen) = getFormatAndLenForField(
            arrayFieldName[1: len(UINT8_NUM_ARRAY_PREFIX)]
        )
        for number in numberArray:
            numberBytes = struct.pack(fieldFormat, number)
            fieldBytes = bytearray().join([fieldBytes, numberBytes])
        return fieldBytes

    def _serializeString(self, stringFieldName, string):
        """
        Serializes input string. It either truncates or pads with null chars if
        necessary to fit the length specified in arrayLengths.

        Parameters
        ----------
        stringFieldName: str
            String field name
        string: str
            String value

        Returns
        -------
        bytearray
            String bytestream
        """

        # truncate the string to fit the length
        # if len(value) is small or equal to the length this does nothing
        fieldLen = self._arrayLengths[stringFieldName]
        value = string[:fieldLen]

        # pad the string with null chars to fit the length
        # if the len(value) is bigger or equal to the length this does nothing
        fieldBytes = value.encode("ascii").ljust(fieldLen, b"\x00")
        return fieldBytes

    def _serializeNumber(self, numberFieldName, number):
        """
        Serializes input number based on its type prefix.

        Parameters
        ----------
        numberFieldName: str
            Numeric field name
        number: int
            Numeric value

        Returns
        -------
        bytearray
            Number bytestream
        """

        (fieldFormat, fieldLen) = getFormatAndLenForField(numberFieldName)
        fieldBytes = struct.pack(fieldFormat, number)
        return fieldBytes

    def __str__(self):
        fields = getSerializableFields(self)
        field_strings = [self.__class__.__name__]
        for field in fields:
            val = getattr(self, field)
            val_str = str(val)
            if isinstance(val, list):
                val_str = str([str(v) for v in val])

            filed_string = "%s->%s" % (field, str(val_str))
            field_strings.append(filed_string)
        return " ".join(field_strings)


class Deserializable:
    """
    Base class for deserializable objects like commands responses.

    Attributes
    ----------
    _arrayLengths: dict
        Utility attribute to store byte array fields length. To be populated by
        child classes.
    _arrayTypes: dict
        Utility attribute to store array fields type. To be populated by child
        classes.
    """

    def __init__(self):
        self._arrayLengths = {}
        self._arrayTypes = {}

    def deserialize(self, bytestream, offset=0):
        """
        Parses a bytestream into the fields specified in the deserializable
        object based on its type and position in the bytestream. The
        deserializable attributes have a name starting with a prefix listed in
        validFieldTypes, and based on it, the field is deserialized
        appropriately, as shown below:

        ================    ============
        Prefix              Field type
        ================    ============
        u8_, u16, u32       Number
        i8_, i16, i32       Number
        au8_, au16, au32    Number array
        ac_                 String
        ar_                 Record array
        ================    ============

        Parameters
        ----------
        bytestream: bytes
            Input bytestream
        offset: int
            Start offset in bytestream to deserialize

        Returns
        -------
        int
            Offset of last deserialized byte plus one
        """

        for field in getSerializableFields(self):
            if REC_ARRAY_PREFIX == field[0: len(UINT8_T_PREFIX)]:
                (fieldValue, offset) = self._deserializeRecordArray(
                    field, bytestream, offset
                )
            elif field[0: len(UINT8_NUM_ARRAY_PREFIX)] in numArrayFieldTypes:
                (fieldValue, offset) = self._deserializeNumberArray(
                    field, bytestream, offset
                )
            elif STRING_PREFIX == field[0: len(UINT8_T_PREFIX)]:
                (fieldValue, offset) = self._deserializeString(
                    field, bytestream, offset
                )
            else:
                (fieldValue, offset) = self._deserializeNumber(
                    field, bytestream, offset
                )

            # assign deserialized value to corresponding object field
            setattr(self, field, fieldValue)

            # Stop parsing data if there is a non-zero error code in the
            # response.
            if field == "u16_ErrorCode" and fieldValue != CmdErrCodes.ErrNone:
                break

        return offset

    def getDescription(self):
        """
        Returns a list with the command fields and their respective values

        Attributes
        ----------
            none

        Returns
        -------
            List of dictionaries with "name" and "field" keys.
        """
        cmdFields = []

        for field in getSerializableFields(self):
            fieldValue = getattr(self, field)
            if REC_ARRAY_PREFIX == field[0: len(UINT8_T_PREFIX)]:
                for i in range(len(fieldValue)):
                    cmdFields.extend(fieldValue[i].getDescription())
            elif field[0: len(UINT8_NUM_ARRAY_PREFIX)] in numArrayFieldTypes:
                for i in range(len(fieldValue)):
                    cmdFields.append(
                        {"name": field + f"_{i}", "value": hex(fieldValue[i])}
                    )
            elif STRING_PREFIX == field[0: len(UINT8_T_PREFIX)]:
                cmdFields.append({"name": field, "value": fieldValue})
            else:
                cmdFields.append({"name": field, "value": hex(fieldValue)})
        return cmdFields

    def _deserializeRecordArray(self, arrayFieldName, bytestream, offset):
        """
        Deserializes bytestream into an array of records based on the record
        type and array length specified in arrayTypes and arrayLengths,
        respectively.

        Parameters
        ----------
        arrayFieldName: str
            Array field name
        bytestream: bytes
            Input bytestream
        offset: int
            Offset of bytes to deserialize in bytestream

        Returns
        -------
        tuple
            Array of records and offset of last deserialized byte plus one
        """

        fieldValue = []

        # get the field's array length from arrayLengths dict
        fieldLen = self._arrayLengths[arrayFieldName]
        if not isinstance(self._arrayLengths[arrayFieldName], int):
            # another obj's attribute, use that attribute's value
            # instead
            fieldLen = getattr(self, self._arrayLengths[arrayFieldName])

        for i in range(fieldLen):
            # create an instance of the corresponding record class
            recordType = self._arrayTypes[arrayFieldName]
            recordObj = recordType()

            # deserialize record object and append it to array
            offset = recordObj.deserialize(bytestream, offset)
            fieldValue.append(recordObj)

        return fieldValue, offset

    def _deserializeNumberArray(self, arrayFieldName, bytestream, offset):
        """
        Deserializes input bytestream into an array of numbers based on its
        type prefix and length specified in arrayLengths. The number type in
        the array is extracted from the attribute's name prefix e.g. for
        "au16", the number type is given by substring "u16", and it is used
        to get the struct unpack format.

        Parameters
        ----------
        arrayFieldName: str
            Array field name
        bytestream: bytes
            Input bytestream
        offset: int
            Offset of bytes to deserialize in bytestream

        Returns
        -------
        tuple
            Array of numbers and offset of last deserialized byte plus one
        """

        fieldValue = []

        # get the field's array length from arrayLengths dict
        arrayLength = self._arrayLengths[arrayFieldName]
        if isinstance(arrayLength, str):
            # another obj's attribute, use that attribute's value instead
            fieldLen = getattr(self, arrayLength)
        elif isinstance(arrayLength, tuple):
            # another object's attribute that indicates a number of elements of
            # a fixed length, so calculate total array length from these two
            # values
            numberElements = getattr(self, arrayLength[0])
            elementByteLength = arrayLength[1]
            fieldLen = numberElements * elementByteLength
        elif isinstance(arrayLength, int):
            # fixed array length
            fieldLen = arrayLength
        else:
            raise errors.UnsupportedArrayLengthType

        (arrayElemFormat, arrayElemLen) = getFormatAndLenForField(
            arrayFieldName[1: len(UINT8_NUM_ARRAY_PREFIX)]
        )

        for i in range(fieldLen):
            subStream = bytestream[offset: offset + arrayElemLen]
            if len(subStream) != arrayElemLen:
                raise errors.NotEnoughBytesError

            (arrayElemValue,) = struct.unpack(arrayElemFormat, subStream)
            fieldValue.append(arrayElemValue)
            offset += arrayElemLen

        return fieldValue, offset

    def _deserializeString(self, stringFieldName, bytestream, offset):
        """
        Deserializes input bytestream into a string of the length specified in
        arrayLenghts. It removes the trailing null characters.

        Parameters
        ----------
        stringFieldName: str
            String field name
        bytestream: bytes
            Input bytestream
        offset: int
            Offset of bytes to deserialize in bytestream

        Returns
        -------
        tuple
            String value and offset of last deserialized byte plus one
        """

        fieldLen = self._arrayLengths[stringFieldName]
        subStream = bytestream[offset: offset + fieldLen]
        if len(subStream) != fieldLen:
            raise errors.NotEnoughBytesError

        # remove null characters at the end of the string
        # the assumption is that the first null char ends the string
        if b"\x00" in subStream:
            subStream = subStream[: subStream.index(b"\00")]

        fieldValue = subStream.decode("ascii")
        offset += fieldLen

        return fieldValue, offset

    def _deserializeNumber(self, numberFieldName, bytestream, offset):
        """
        Deserializes input bytestream into a number based on its type prefix.

        Parameters
        ----------
        numberFieldName: str
            Numeric field name
        bytestream: bytes
            Input bytestream
        offset: int
            Offset of bytes to deserialize in bytestream

        Returns
        -------
        tuple
            Numeric value and offset of last deserialized byte plus one
        """
        (fieldFormat, fieldLen) = getFormatAndLenForField(numberFieldName)
        subStream = bytestream[offset: offset + fieldLen]
        if len(subStream) != fieldLen:
            raise errors.NotEnoughBytesError

        (fieldValue,) = struct.unpack(fieldFormat, subStream)
        offset += fieldLen

        return fieldValue, offset


def getByteLenFromDataType(dataTypeStr):
    """
    Utility function to get number of bytes for serializable object fields
    based on their name prefix, to be used to specify number of bytes in struct
    functions.

    Parameters
    ----------
    dataTypeStr: str
        Serializable object attribute name prefix

    Returns
    -------
    int
        Number of bytes for data type
    """
    dataTypeFilter = filter(str.isdigit, dataTypeStr)
    numBits = "".join(dataTypeFilter)
    return int(numBits) >> 3


def getSerializableFields(serializableObj):
    """
    Utility function to get a list of the serializable object attributes
    names that correspond to command, response or record fields, based on the
    name prefix.

    Parameters
    ----------
    serializableObj: Serializable or Deserializable
        Objects as commands, responses and records

    Returns
    -------
    list
        Serializable field names
    """
    objAttr = list(vars(serializableObj).keys())
    filterObjAttr = filter(
        lambda x: x[0: len(UINT8_T_PREFIX)] in validFieldTypes
        or x[0: len(UINT8_NUM_ARRAY_PREFIX)] in validFieldTypes,
        objAttr,
    )

    fields = []
    for attr in filterObjAttr:
        fields.append(attr)
    return fields


def getFormatAndLenForField(field):
    """
    Utility function to get the format string used with struct functions for a
    single command or response field based on its name prefix. It also returns
    the number of bytes of the requested field.

    Parameters
    ----------
    field: str
        Serializable or Deserializable field name

    Returns
    -------
    tuple
        Field struct format and byte number
    """
    fieldNamePrefix = field[0: len(UINT8_T_PREFIX)]
    fieldFormat = "<"
    fieldLen = getByteLenFromDataType(fieldNamePrefix)
    fieldFormat += dataTypeToFormat[fieldNamePrefix]

    return fieldFormat, fieldLen


UINT8_T_PREFIX = "u8_"
UINT16_T_PREFIX = "u16"
UINT32_T_PREFIX = "u32"
UINT64_T_PREFIX = "u64"
INT8_T_PREFIX = "i8_"
INT16_T_PREFIX = "i16"
INT32_T_PREFIX = "i32"
INT64_T_PREFIX = "i64"
UINT8_NUM_ARRAY_PREFIX = "au8_"
UINT16_NUM_ARRAY_PREFIX = "au16"
UINT32_NUM_ARRAY_PREFIX = "au32"
STRING_PREFIX = "ac_"
REC_ARRAY_PREFIX = "ar_"

numArrayFieldTypes = [
    UINT8_NUM_ARRAY_PREFIX,
    UINT16_NUM_ARRAY_PREFIX,
    UINT32_NUM_ARRAY_PREFIX,
]

intPrefixTypes = [
    UINT8_T_PREFIX,
    UINT16_T_PREFIX,
    UINT32_T_PREFIX,
    UINT64_T_PREFIX,
    INT8_T_PREFIX,
    INT16_T_PREFIX,
    INT32_T_PREFIX,
    INT64_T_PREFIX,
]

validFieldTypes = [
    UINT8_T_PREFIX,
    UINT16_T_PREFIX,
    UINT32_T_PREFIX,
    UINT64_T_PREFIX,
    INT8_T_PREFIX,
    INT16_T_PREFIX,
    INT32_T_PREFIX,
    INT64_T_PREFIX,
    UINT8_NUM_ARRAY_PREFIX,
    UINT16_NUM_ARRAY_PREFIX,
    UINT32_NUM_ARRAY_PREFIX,
    STRING_PREFIX,
    REC_ARRAY_PREFIX,
]

dataTypeToFormat = {
    UINT8_T_PREFIX: "B",
    UINT16_T_PREFIX: "H",
    UINT32_T_PREFIX: "I",
    UINT64_T_PREFIX: "Q",
    INT8_T_PREFIX: "b",
    INT16_T_PREFIX: "h",
    INT32_T_PREFIX: "i",
    INT64_T_PREFIX: "q",
}
