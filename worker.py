from collections.abc import Callable
from asyncio import Queue
import asyncio
import logging
import inspect


class Work:
    def __init__(self, name: str, queue: Queue, task: Callable):
        self.name = name
        self.queue = queue
        self.task = task
        self.workers = []

    async def run(self, num_of_workers: int) -> None:
        self.workers = await self.create_workers(num_of_workers)
        await self.queue.join()
        await self.dismiss_workers()

    async def create_workers(self, num_of_workers: int) -> list:
        if self.workers:
            await self.dismiss_workers()
        self.workers = await create_workers(
            self.name, self.queue, self.task, num_of_workers
        )

    async def dismiss_workers(self) -> None:
        await dismiss_workers(self.workers)


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


async def create_workers(
    name: str, queue: Queue, task: Callable, num_of_workers: int
) -> list:
    for i in range(num_of_workers):
        workers = []
        worker = asyncio.create_task(do_task(f"{name}-{i}", queue, task))
        workers.append(worker)
    return workers


async def dismiss_workers(workers: list) -> None:
    if not workers:
        return
    for worker in workers:
        worker.cancel()
    await asyncio.gather(*workers, return_exceptions=True)
    logging.info(f"Workers dismissed")
