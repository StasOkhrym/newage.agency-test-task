import time
from typing import Callable


def timer(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"\nElapsed in {round(run_time, 3)} seconds")
        return value

    return wrapper
