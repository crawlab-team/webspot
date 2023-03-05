import os
from functools import wraps
import time

from webspot.logging import get_logger

logger = get_logger('webspot.utils.time')

is_debug = os.environ.get('WEBSPOT_DEBUG', 'false').lower() == 'true'


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        if is_debug:
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            total_time = (end_time - start_time) * 1e3
            logger.debug(f'[{total_time:.0f}ms] {func.__name__}{args} {kwargs}')
            return result
        else:
            return func(*args, **kwargs)

    return timeit_wrapper
