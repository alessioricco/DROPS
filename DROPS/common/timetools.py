from datetime import datetime, timezone
import time

def now() -> datetime:
    return datetime.now(timezone.utc)



def time_execution(func):
    """
    A decorator that logs the execution time of the wrapped function.
    """
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        print(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result
    return wrapper

# Example usage
# @time_execution
# def test_function(n):
#     """
#     Example function that simply sums the numbers from 1 to n.
#     """
#     return sum(range(1, n + 1))

# # Call the decorated function
# print(test_function(1000000))

