from functools import wraps
import time


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = (end_time - start_time) * 1e3
        print(f'[{total_time:.0f}ms] {func.__name__}{args} {kwargs}')
        return result

    return timeit_wrapper
