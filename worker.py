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
        tasks = await create_tasks(self, num_of_workers)
        await self.queue.join()
        await cancel_tasks(tasks)


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


async def create_tasks(worker, num_of_workers):
    for i in range(num_of_workers):
        tasks = []
        task = asyncio.create_task(
            do_task(f"{worker.name}-{i}", worker.queue, worker.task)
        )
        tasks.append(task)
    return tasks


async def cancel_tasks(tasks):
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    logging.info(f"Tasks finished")
