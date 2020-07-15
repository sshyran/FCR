#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from functools import wraps
from typing import Optional

from fbnet.command_runner_asyncio.CommandRunner import ttypes


def canonicalize(val):
    """
    A helper function to convert all 'str' to 'bytes' in given value. The
    values can either be a string or a list. We will recursively convert each
    member of the list.
    """
    if isinstance(val, list):
        return [canonicalize(v) for v in val]
    if isinstance(val, str):
        return val.encode("utf8")
    return val


def _check_device(device: Optional[ttypes.Device]) -> None:
    if not device:
        raise ttypes.SessionException(
            message="Required argument (device) cannot be None."
        )

    missing_list = []
    if not device.hostname:
        missing_list.append("hostname")

    if not device.username:
        missing_list.append("username")

    if not device.password:
        missing_list.append("password")

    if missing_list:
        raise ttypes.SessionException(
            message=f"Following required Device fields are missing: {missing_list}"
        )


def _check_session(session: Optional[ttypes.Session]) -> None:
    if not session:
        raise ttypes.SessionException(
            message="Required argument (session) cannot be None."
        )

    missing_list = []
    if not session.hostname:
        missing_list.append("hostname")

    if not session.id:
        missing_list.append("id")

    if not session.name:
        missing_list.append("name")

    if missing_list:
        raise ttypes.SessionException(
            message=f"Following required Session fields are missing: {missing_list}"
        )


def input_fields_validator(fn):  # noqa C901
    @wraps(fn)
    async def wrapper(self, *args, **kwargs):

        for i, arg in enumerate(args):

            if arg is None:
                raise ttypes.SessionException(
                    message=f"The ({i + 1})th argument cannot be None."
                )

            if isinstance(arg, ttypes.Device):
                _check_device(arg)

            if isinstance(arg, ttypes.Session):
                _check_session(arg)

        for argument, val in kwargs.items():
            if argument == "command" and not val:
                raise ttypes.SessionException(
                    message="Required argument (command) cannot be None."
                )

            if argument == "device":
                _check_device(val)

            if argument == "session":
                _check_session(val)

            if argument == "device_to_commands" or argument == "device_to_configlets":
                if not val:
                    raise ttypes.SessionException(
                        message=f"Required argument ({val}) cannot be None."
                    )

                for device in val:
                    _check_device(device)

        return await fn(self, *args, **kwargs)

    return wrapper
