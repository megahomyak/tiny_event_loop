import time
from collections import deque

import pytest

from event_loop import EventLoop


def raises_value_error():
    raise ValueError
    # noinspection PyUnreachableCode
    yield


def calling_exception_raising_function():
    yield raises_value_error()


def return_something():
    return 5
    # noinspection PyUnreachableCode
    yield


def return_something_through_another_function():
    return (yield return_something())


def wait(time_in_seconds):
    wait_to = time.time() + time_in_seconds
    while time.time() < wait_to:
        yield


def wait_and_add_a_value_to_list(time_in_seconds, list_):
    yield wait(time_in_seconds)
    list_.append(time_in_seconds)


def test_event_loop():
    event_loop = EventLoop()
    with pytest.raises(ValueError):
        event_loop.run(calling_exception_raising_function())
        assert event_loop.unfinished_tasks == deque([])
    with pytest.raises(ValueError):
        event_loop.run_until_complete(calling_exception_raising_function())
        assert event_loop.unfinished_tasks == deque([])
    assert event_loop.run(return_something_through_another_function()) == 5
    assert event_loop.unfinished_tasks == deque([])
    numbers = []
    event_loop.create_task(wait_and_add_a_value_to_list(3, numbers))
    event_loop.create_task(wait_and_add_a_value_to_list(1, numbers))
    event_loop.create_task(wait_and_add_a_value_to_list(2, numbers))
    event_loop.create_task(wait_and_add_a_value_to_list(4, numbers))
    event_loop.create_task(wait_and_add_a_value_to_list(5, numbers))
    event_loop.run_all_tasks()
    assert event_loop.unfinished_tasks == deque([])
    assert numbers == [1, 2, 3, 4, 5]
