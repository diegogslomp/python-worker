from asyncio import Queue
from collections.abc import Callable
import asyncio
import logging
import inspect


class Worker:
    def __init__(self, name: str, queue: Queue, task: Callable):
        self.name = name
        self.queue = queue
        self.task = task
        self.tasks = []

    async def run(self, num_of_workers: int) -> None:
        self.tasks = await self.create_tasks(num_of_workers)
        await self.queue.join()
        await self.cancel_tasks()

    async def create_tasks(self, num_of_workers: int) -> list:
        if self.tasks:
            await self.cancel_tasks()
        self.tasks = await create_tasks(
            self.name, self.queue, self.task, num_of_workers
        )

    async def cancel_tasks(self) -> None:
        await cancel_tasks(self.tasks)


async def do_task(name: str, queue: Queue, task: Callable) -> None:
    while True:
        item = await queue.get()
        if inspect.iscoroutinefunction(task):
            await task(item)
        else:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, task, item)
        queue.task_done()
        logging.debug(f"{name} done {item}")


async def create_tasks(
    name: str, queue: Queue, task: Callable, num_of_workers: int
) -> list:
    for i in range(num_of_workers):
        tasks = []
        t = asyncio.create_task(do_task(f"{name}-{i}", queue, task))
        tasks.append(t)
    return tasks


async def cancel_tasks(tasks: list) -> None:
    if not tasks:
        return
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    logging.info(f"Tasks finished")
