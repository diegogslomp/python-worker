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
        await self.create_workers(num_of_workers)
        await self.queue.join()
        await self.dismiss_workers()

    async def run_forever(self, num_of_workers: int, queue_feeder: callable) -> None:
        await self.create_workers(num_of_workers)
        try:
            while True:
                queue_feeder(self.queue)
                await self.queue.join()
                logging.debug("queue done")
        finally:
            await self.dismiss_workers()

    async def create_workers(self, num_of_workers: int) -> None:
        for i in range(num_of_workers):
            new_worker = asyncio.create_task(
                coro=do_task(f"{self.name}-{i}", queue=self.queue, task=self.task)
            )
            logging.debug(f"{self.name}-{i} worker created")
            self.workers.append(new_worker)

    async def dismiss_workers(self) -> None:
        if not self.workers:
            return
        for old_worker in self.workers:
            old_worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
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
