from event_loop import EventLoop


def raises_value_error():
    raise ValueError
    # noinspection PyUnreachableCode
    yield


def calling_exception_raising_function():
    yield raises_value_error()


def test_event_loop():
    event_loop = EventLoop()
    event_loop.add_new_task(calling_exception_raising_function())
