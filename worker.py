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

    async def run(self, num_of_workers):
        tasks = []
        for i in range(num_of_workers):
            task = asyncio.create_task(
                work_forever(f"{self.name}-{i}", self.queue, self.task)
            )
            tasks.append(task)
        await self.queue.join()
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logging.info(f"{num_of_workers} {self.name} done")


async def work_forever(name: str, queue: Queue, task: Callable) -> None:
    while True:
        item = await queue.get()
        if inspect.iscoroutinefunction(task):
            await task(item)
        else:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, task, item)
        queue.task_done()
        logging.debug(f"{name} done {item}")
