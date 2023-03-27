class NotEnoughBytesError(Exception):
    """Not enough bytes in object to properly deserialize"""

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass


class UnsupportedArrayLengthType(Exception):
    """
    Unsupported array length setting type. Supported types include string to
    indicate an object's attribute value, a tuple to indicate a constant int
    and an object's attribute value, and a constant int.
    """

    def __init__(self, *args, **kwargs):  # real signature unknown
        pass
