from asyncio import Queue
import asyncio
import logging
import inspect


class Work:
    def __init__(self, name: str, task: callable, queue=Queue()):
        self.name = name
        self.queue = queue
        self.task = task
        self.workers = []

    async def run_once(self, num_of_workers: int) -> None:
        await create_workers(self, num_of_workers)
        await self.queue.join()
        await dismiss_workers(self)

    async def run_forever(self, num_of_workers: int, queue_feeder: callable) -> None:
        await create_workers(self, num_of_workers)
        try:
            while True:
                queue_feeder(self.queue)
                await self.queue.join()
                logging.debug("queue done")
        finally:
            await dismiss_workers(self)


async def create_workers(worker, num_of_workers: int) -> None:
    for i in range(num_of_workers):
        new_worker = asyncio.create_task(
            coro=do_task(f"{worker.name}-{i}", queue=worker.queue, task=worker.task)
        )
        logging.debug(f"{worker.name}-{i} worker created")
        worker.workers.append(new_worker)


async def dismiss_workers(worker) -> None:
    if not worker.workers:
        return
    for old_worker in worker.workers:
        old_worker.cancel()
    await asyncio.gather(*worker.workers, return_exceptions=True)
    logging.debug(f"workers dismissed")


async def do_task(name: str, queue: Queue, task: callable) -> None:
    while True:
        item = await queue.get()
        if inspect.iscoroutinefunction(task):
            await task(item)
        else:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, task, item)
        queue.task_done()
        logging.debug(f"{name} done {item}")
