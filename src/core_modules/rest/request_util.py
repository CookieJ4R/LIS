"""
File containing helper methods to interact with the argument object passed to the api classes.
"""


def get_string_from_args_obj(arg_name: str, args_obj, default: str = None):
    """
    Method to extract a str argument from the args_obj.
    :param arg_name: The argument to extract
    :param args_obj: The args_obj passed to the api handler
    :param default: The default value to return if the value could not be found. Default: None
    :return: The argument as a str or the default value if it was not found.
    """
    if arg_name in args_obj:
        return _decode_value(args_obj[arg_name][0])
    return default


def get_int_from_args_obj(arg_name: str, args_obj, default: int = None):
    """
    Method to extract an int argument from the args_obj.
    :param arg_name: The argument to extract
    :param args_obj: The args_obj passed to the api handler
    :param default: The default value to return if the value could not be found. Default: None
    :return: The argument as an int or the default value if it was not found.
    :raises ValueError:
    """
    if arg_name in args_obj:
        try:
            int(_decode_value(args_obj[arg_name][0]))
        except ValueError:
            raise
    return default


def get_bool_from_args_obj(arg_name: str, args_obj, default: bool = None):
    """
    Method to extract a bool argument from the args_obj.
    :param arg_name: The argument to extract
    :param args_obj: The args_obj passed to the api handler
    :param default: The default value to return if the value could not be found or is in the wrong format. Default: None
    :return: The argument as a bool or the default value if it was not found.
    """
    if arg_name in args_obj:
        val = (_decode_value(args_obj[arg_name][0])).lower()
        if val == "true" or val == "false":
            return val == "true"
    return default


def _decode_value(value: bytes) -> [None, str]:
    """
    Helper method to decode the byte argument with utf-8.
    :param value: The value to decode.
    :return: The decoded value.
    :raises UnicodeDecodeError:
    """
    try:
        return value.decode("utf-8")
    except UnicodeDecodeError:
        print(str(value) + " could not be decoded!")
        raise
