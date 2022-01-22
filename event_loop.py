import inspect
from dataclasses import dataclass
from typing import Generator, Optional, Any


@dataclass
class Result:
    value: Any


@dataclass
class Task:
    generator: Generator
    result: Optional[Result] = None
    exception: Optional[Result] = None

    @property
    def is_finished(self):
        return bool(self.result or self.exception)


class EventLoop:

    def __init__(self):
        self.tasks = []

    def add_new_task(self, generator: Generator):
        self.tasks.append(Task(generator))

    def _run_task(self, task: Task):
        while not task.is_finished:
            self._push_task(task)

    def _push_task(self, task: Task):
        try:
            new_generator = task.generator.send(None)
            if new_generator is None:
                
            elif not inspect.isgenerator(new_generator):
                raise TypeError(
                    f"Object yielded from {task} was not a generator!"
                )
            new_task = Task(new_generator)
            self._run_task(new_task)
            if new_task.exception:
                task.generator.throw(new_task.exception.value)
            else:
                task.generator.send(new_task.result.value)
        except Exception as exception:
            if isinstance(exception, StopIteration):
                task.result = Result(exception.value)
            else:
                task.exception = Result(exception)

    def _roll_next_task(self):
        """
        Exception received => propagate to caller
                              (or raise from here if there is no caller)
        Result received => propagate to caller
        New generator received => add to loop as a task and return
        """
        value_to_send = None
        exception_to_throw = None
        task: Task = self.tasks.pop()
        while task:
            # noinspection PyBroadException
            try:
                if exception_to_throw is None:
                    saved_value_to_send = value_to_send
                    value_to_send = None
                    new_generator = task.generator.send(saved_value_to_send)
                else:
                    saved_exception_to_throw = exception_to_throw
                    exception_to_throw = None
                    new_generator = task.generator.throw(
                        saved_exception_to_throw.__class__,
                        saved_exception_to_throw,
                        saved_exception_to_throw.__traceback__
                    )
            except Exception as exception:
                if isinstance(exception, StopIteration):
                    value_to_send = exception.value
                else:
                    if task.caller is None:
                        raise
                    else:
                        exception_to_throw = exception
                task = task.caller
            else:
                if inspect.isgenerator(new_generator):
                    self.tasks.append(Task(new_generator, caller=task))
                    return
                else:
                    raise TypeError(
                        f"Object yielded from {task} was not a generator!"
                    )

    def run_until_complete(self, generator: Generator):
        task = Task(generator)
        self._run_task(task)
        while self.tasks:
            self._roll_next_task()
        

    def run(self):
