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
        await run_once(work=self, num_of_workers=num_of_workers)

    async def run_forever(self, num_of_workers: int, queue_feeder: callable) -> None:
        await run_forever(
            work=self, num_of_workers=num_of_workers, queue_feeder=queue_feeder
        )

    async def create_workers(self, num_of_workers: int) -> None:
        self.workers = await create_workers(
            name=self.name,
            queue=self.queue,
            task=self.task,
            num_of_workers=num_of_workers,
        )

    async def dismiss_workers(self) -> None:
        await dismiss_workers(self.workers)


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


async def run_once(work: Work, num_of_workers: int) -> None:
    await work.create_workers(num_of_workers)
    await work.queue.join()
    await work.dismiss_workers()


async def run_forever(work: Work, num_of_workers: int, queue_feeder: callable) -> None:
    await work.create_workers(num_of_workers)
    try:
        while True:
            queue_feeder(work.queue)
            await work.queue.join()
            logging.debug("Queue done")
    finally:
        await work.dismiss_workers()


async def create_workers(
    name: str, task: callable, num_of_workers: int, queue: Queue
) -> list:
    workers = []
    for i in range(num_of_workers):
        worker = asyncio.create_task(
            coro=do_task(f"{name}-{i}", queue=queue, task=task)
        )
        logging.debug(f"{name}-{i} worker created")
        workers.append(worker)
    return workers


async def dismiss_workers(workers: list) -> None:
    if not workers:
        return
    for worker in workers:
        worker.cancel()
    await asyncio.gather(*workers, return_exceptions=True)
    logging.debug(f"workers dismissed")
