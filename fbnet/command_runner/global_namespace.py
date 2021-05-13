#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import contextvars


class GlobalNamespace:
    """
    This class is not meant to be instantiated. It is a namespace class with
    only class methods to store and share some info/options throughout the
    service. You can use this class for
        1. Sharing server level context among different threads/coroutines (e.g.,
           is the server running in prod mode or dev mode?)
        2. Sharing thread/coroutine level context (e.g., request uuid, as each
           request will be handled by a separate thread/coroutine) along the
           function call chains in the same thread/coroutine.

    Usage: You can import it anywhere you need access to these info as

    from global_namespace import GlobalNamespace
    uuid = GlobalNamespace.get_request_uuid()
    """

    # NOTE: contextvars is a module added in Python 3.7, which is compatible for
    # both async/non-async codes
    # https://docs.python.org/3/library/contextvars.html#module-contextvars
    # By using the ContextVar, we can share thread/coroutine level context (e.g.,
    # request uuid, as each request will be handled by a separate thread)
    # along the function call chains in the same thread. For example, if we
    # have a function call chain like A->B->C->D->E. If we want to pass,
    # say, uuid from A to E, instead of add an additional argument for each
    # method, we can just store the data in thread local so everything along
    # the call chain can pick it up for free.
    _request_uuid = contextvars.ContextVar("request_uuid", default="N/A")

    @classmethod
    def set_request_uuid(cls, uuid: str) -> None:
        """Store uuid as thread local data"""
        cls._request_uuid.set(uuid)

    @classmethod
    def get_request_uuid(cls) -> str:
        return cls._request_uuid.get()