from typing import Literal, Callable, Type, Union

MSG_FORMAT = "PYALERT: {method_name} MSG: {e}"
TAKES_ATTR = "_takes"
RAISE_ERROR_ATTR = "_raise_error"


def alert_conf(takes: Literal["input", "output"] = "input", raise_error: bool = False):
    """Decorator to configure alert methods."""

    def alert_conf_decorator(func: Callable) -> Callable:
        setattr(func, TAKES_ATTR, takes)
        setattr(func, RAISE_ERROR_ATTR, raise_error)
        return func

    return alert_conf_decorator


class PyAlerts:
    """Base class for PyAlerts."""

    def __init__(self):
        """Takes all alert methods and stores them in lists."""
        self._input_alerts = []
        self._input_alerts_raise = []
        self._output_alerts = []
        self._output_alerts_raise = []

        for method_name in dir(self):
            method = getattr(self, method_name)
            if callable(method):
                if (
                    hasattr(method, TAKES_ATTR)
                    and getattr(method, TAKES_ATTR) == "input"
                ):
                    if getattr(method, RAISE_ERROR_ATTR) is True:
                        self._input_alerts_raise.append(method)
                    else:
                        self._input_alerts.append(method)
                elif (
                    hasattr(method, TAKES_ATTR)
                    and getattr(method, TAKES_ATTR) == "output"
                ):
                    if getattr(method, RAISE_ERROR_ATTR) is True:
                        self._output_alerts_raise.append(method)
                    else:
                        self._output_alerts.append(method)


def pyalert(pyalerts: Union[PyAlerts, Type[PyAlerts]]) -> Callable:
    """Decorator to wrap functions with PyAlerts"""
    if isinstance(pyalerts, type):
        pyalerts = pyalerts()
    if not isinstance(pyalerts, PyAlerts):
        raise TypeError("pyalerts does not inherit from PyAlerts")

    def pyalert_decorator(func):
        def wrapper(*args, **kwargs):

            # execute raise input alerts
            for method in pyalerts._input_alerts_raise:
                try:
                    method(*args, **kwargs)
                except Exception as e:
                    raise ValueError(  # FIXME write custom pyalert exception
                        MSG_FORMAT.format(method_name=method.__name__, e=e)
                    )
            # execute regular input alerts
            for method in pyalerts._input_alerts:
                try:
                    method(*args, **kwargs)
                except Exception as e:
                    print(
                        MSG_FORMAT.format(method_name=method.__name__, e=e)
                    )

            output = func(*args, **kwargs)

            # execute raise output alerts
            for method in pyalerts._output_alerts_raise:
                try:
                    method(output)
                except Exception as e:
                    raise ValueError(  # FIXME write custom pyalert exception
                        MSG_FORMAT.format(method_name=method.__name__, e=e)
                    )
            # execute regular output alerts
            for method in pyalerts._output_alerts:
                try:
                    method(output)
                except Exception as e:
                    print(
                        MSG_FORMAT.format(method_name=method.__name__, e=e)
                    )

            return output

        return wrapper

    return pyalert_decorator
