from worker import Work, create_workers, dismiss_workers
from asyncio import Queue
import asyncio
import logging
import readme
import random
import time
import copy
import os


# Get info from .env file
num_of_sleepers = int(os.getenv("SLEEPERS", 10))
num_of_workers = int(os.getenv("WORKERS", 2))
logging.basicConfig(level=logging.DEBUG)

# Populate queue
initial_queue = Queue()
total_sleep_time = 0
for _ in range(num_of_sleepers):
    sleep_for = random.uniform(0.05, 1.0)
    total_sleep_time += sleep_for
    initial_queue.put_nowait(sleep_for)


def test_sync_task_work():
    work = Work(
        name="sync_task_worker",
        queue=copy.deepcopy(initial_queue),
        task=time.sleep,
    )
    asyncio.run(work.run(num_of_workers))


def test_async_task_work():
    work = Work(
        name="async_task_worker",
        queue=copy.deepcopy(initial_queue),
        task=asyncio.sleep,
    )
    asyncio.run(work.run(num_of_workers))


async def run(name, queue, task):
    # Create workers
    workers = await create_workers(name, queue, task, num_of_workers)

    # Wait queue finish
    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel workers
    await dismiss_workers(workers)

    # Summmary
    logging.info(
        f"{num_of_workers} {name}s slept in parallel for {total_slept_for:.2f} seconds"
    )
    logging.info(f"total expected sleep time: {total_sleep_time:.2f} seconds")


def test_using_methods():
    name = "test_using_methods"
    queue = copy.deepcopy(initial_queue)
    task = asyncio.sleep

    asyncio.run(run(name, queue, task))


def test_readme():
    asyncio.run(readme.run())


if __name__ == "__main__":
    test_sync_task_work()
    test_async_task_work()
    test_using_methods()
    test_readme()
