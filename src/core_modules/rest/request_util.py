"""
File containing helper methods to interact with the argument object passed to the api classes.
"""
from core_modules.logging.lis_logging import get_logger

log = get_logger(__name__)


def get_string_from_args_obj(arg_name: str, args_obj, default: str = None):
    """
    Method to extract a str argument from the args_obj.
    :param arg_name: The argument to extract
    :param args_obj: The args_obj passed to the api handler
    :param default: The default value to return if the value could not be found. Default: None
    :return: The argument as a str or the default value if it was not found.
    """
    if arg_name in args_obj:
        return _decode_value(args_obj[arg_name])
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
            return int(_decode_value(args_obj[arg_name]))
        except ValueError:
            log.error(str(args_obj[arg_name] + " is not an int!"))
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
        val = (_decode_value(args_obj[arg_name])).lower()
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
        log.error(str(value) + " could not be decoded!")
        raise


def remap_request_args(args: dict) -> dict:
    """
    The tornado framework parses the arguments of a request as lists in case an argument is used multiple times.
    While this feature makes sense, it only complicates the usage of the values most of the time, so this method
    remaps the argument dict so that only the first element in the list is used as the actual argument.
    :param args: The arguments to remap
    :return: The remapped dictionary containing the arguments of the request.
    """
    new_dict = {}
    for key in args:
        new_dict[key] = args[key][0]
    return new_dict
