import inspect
from collections import deque
from dataclasses import dataclass
from typing import Generator, Optional, Any, Deque


@dataclass
class Result:
    exception: Exception = None
    returned_value: Any = None


@dataclass
class Task:
    generator: Generator
    caller: Optional["Task"] = None
    result: Optional[Result] = None


class EventLoop:

    def __init__(self):
        self.unfinished_tasks: Deque[Task] = deque()

    def create_task(self, generator: Generator):
        if not inspect.isgenerator(generator):
            raise TypeError(
                f"Task can be created only from a generator, not from "
                f"{generator}!"
            )
        task = Task(generator)
        self.unfinished_tasks.append(task)
        return task

    def _poll_task(self, task: Task, poll_with: Result) -> Optional[Result]:
        """
        Exception received => propagate to caller
                              (or raise from here if there is no caller)
        Result received => propagate to caller
        New generator received => add to loop as a task and return
        """
        try:
            if poll_with.exception is None:
                new_generator = task.generator.send(poll_with.returned_value)
            else:
                new_generator = task.generator.throw(poll_with.exception)
        except Exception as e:
            if isinstance(e, StopIteration):
                return Result(returned_value=e.value)
            else:
                return Result(exception=e)
        else:
            if new_generator is not None:
                self.unfinished_tasks.append(
                    Task(new_generator, caller=task)
                )
            else:
                self.unfinished_tasks.append(task)
            return None

    def _roll_task(self):
        task = self.unfinished_tasks.popleft()
        poll_with = Result()
        while True:
            poll_with = self._poll_task(task, poll_with)
            if poll_with is None:
                break
            else:
                if task.caller is None:
                    task.result = poll_with
                    break
                task = task.caller

    def run_all_tasks(self):
        while self.unfinished_tasks:
            self._roll_task()

    def run_until_complete(self, generator: Generator):
        task = self.create_task(generator)
        self.run_all_tasks()
        return self._deal_with_result(task.result)

    def run(self, generator: Generator):
        task = self.create_task(generator)
        while task.result is None:
            self._roll_task()
        self.unfinished_tasks.clear()
        # noinspection PyTypeChecker
        return self._deal_with_result(task.result)

    # noinspection PyMethodMayBeStatic
    def _deal_with_result(self, result: Result):
        if result.exception:
            raise result.exception
        else:
            return result.returned_value
