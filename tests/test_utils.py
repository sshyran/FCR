#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from typing import Dict, List, Optional

from fbnet.command_runner.utils import (
    _check_device,
    _check_session,
    canonicalize,
    input_fields_validator,
)
from fbnet.command_runner_asyncio.CommandRunner import ttypes

from .testutil import AsyncTestCase, async_test


class CanonicalizeTest(unittest.TestCase):
    def test_canonicalize(self):
        self.assertEqual(canonicalize("abc"), b"abc")
        self.assertEqual(canonicalize(b"abc"), b"abc")
        self.assertEqual(canonicalize(["abc", "xyz", b"123"]), [b"abc", b"xyz", b"123"])


class InputFieldsValidatorTest(AsyncTestCase):
    def test_check_device(self) -> None:
        with self.assertRaises(ttypes.SessionException) as ex:
            _check_device(device=None)

        self.assertEqual(
            ex.exception.message, "Required argument (device) cannot be None."
        )

        with self.assertRaises(ttypes.SessionException) as ex:
            _check_device(device=ttypes.Device())

        missing_list = ["hostname", "username", "password"]
        for missing_field in missing_list:
            self.assertIn(missing_field, ex.exception.message)

    def test_check_session(self) -> None:
        with self.assertRaises(ttypes.SessionException) as ex:
            _check_session(session=None)

        self.assertEqual(
            ex.exception.message, "Required argument (session) cannot be None."
        )

        with self.assertRaises(ttypes.SessionException) as ex:
            _check_session(session=ttypes.Session())

        missing_list = ["hostname", "id", "name"]
        for missing_field in missing_list:
            self.assertIn(missing_field, ex.exception.message)

    @async_test
    async def test_input_fields_validator(self) -> None:
        @input_fields_validator
        async def test_command(self, command: Optional[str]) -> None:
            return

        @input_fields_validator
        async def test_device(self, device: ttypes.Device) -> None:
            return

        @input_fields_validator
        async def test_session(self, session: ttypes.Session) -> None:
            return

        @input_fields_validator
        async def test_device_to_commands(
            self, device_to_commands: Dict[ttypes.Device, List[str]]
        ) -> None:
            return

        @input_fields_validator
        async def test_device_to_configlets(
            self, device_to_configlets: Dict[ttypes.Device, List[str]]
        ) -> None:
            return

        with self.assertRaises(ttypes.SessionException):
            await test_command(self, command=None)

        with self.assertRaises(ttypes.SessionException):
            await test_device(self, device=ttypes.Device(hostname="test-device"))

        with self.assertRaises(ttypes.SessionException):
            await test_session(self, session=ttypes.Session(hostname="test-device"))

        with self.assertRaises(ttypes.SessionException):
            await test_device_to_commands(
                self,
                device_to_commands={ttypes.Device(hostname="test-device"): ["command"]},
            )

        with self.assertRaises(ttypes.SessionException):
            await test_device_to_configlets(
                self,
                device_to_configlets={
                    ttypes.Device(hostname="test-device"): ["configs"]
                },
            )
