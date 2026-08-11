# -*- coding: utf-8 -*-
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Author: Mauro Soria

from __future__ import annotations

import threading

from functools import wraps
from time import time
from typing import Any, Callable, TypeVar, cast

_lock = threading.Lock()
_cache: dict[int, tuple[float, Any]] = {}
_cache_lock = threading.Lock()

F = TypeVar("F", bound=Callable[..., Any])


def cached(timeout: int | float = 100) -> Callable[[F], F]:
    def _cached(func: F) -> F:
        @wraps(func)
        def with_caching(*args: Any, **kwargs: Any) -> Any:
            key = id(func)
            for arg in args:
                key += id(arg)
            for k, v in kwargs.items():
                key += id(k) + id(v)

            # If it was cached and the cache timeout hasn't been reached
            if key in _cache and time() - _cache[key][0] < timeout:
                return _cache[key][1]

            with _cache_lock:
                result = func(*args, **kwargs)
                _cache[key] = (time(), result)

            return result

        return cast(F, with_caching)

    return _cached


def locked(func: F) -> F:
    def with_locking(*args: Any, **kwargs: Any) -> Any:
        with _lock:
            return func(*args, **kwargs)

    return cast(F, with_locking)
