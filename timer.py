import time


def wait(time_in_seconds):
    wait_to = time.time() + time_in_seconds
    while time.time() < wait_to:
        yield
