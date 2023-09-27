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
        try:
            await self.queue.join()
        finally:
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
            worker_name = f"{self.name}-{i+1}"
            self.workers.append(
                asyncio.create_task(
                    do_task(name=f"{worker_name}", queue=self.queue, task=self.task)
                )
            )
            logging.debug(f"worker {worker_name} created")

    async def dismiss_workers(self) -> None:
        if not self.workers:
            return
        for worker in self.workers:
            worker.cancel()
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
