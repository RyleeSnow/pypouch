from __future__ import annotations

import functools
import inspect


def filter_kwargs(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        valid_keys = sig.parameters.keys()
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_keys}
        return func(*args, **filtered_kwargs)

    return wrapper
