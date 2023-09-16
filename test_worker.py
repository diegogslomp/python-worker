from asyncio import Queue
import asyncio
import logging
import random
import time
import copy
import os
from worker import Worker, create_tasks, cancel_tasks


# Get info from .env file
logging.basicConfig(level=os.getenv("LOG_LEVEL", logging.DEBUG))
num_of_tasks = int(os.getenv("NUM_OF_TASKS", 10))
num_of_workers = int(os.getenv("NUM_OF_WORKERS", 2))

# Populate queue
initial_queue = Queue()
total_sleep_time = 0
for _ in range(num_of_tasks):
    sleep_for = random.uniform(0.05, 1.0)
    total_sleep_time += sleep_for
    initial_queue.put_nowait(sleep_for)


async def sleep_worker_test(name, queue, task):
    # Create task for each worker
    tasks = await create_tasks(name, queue, task, num_of_workers)

    # Wait queue finish
    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel tasks
    await cancel_tasks(tasks)

    # Summmary
    logging.info(
        f"{num_of_workers} {name}s slept in parallel for {total_slept_for:.2f} seconds"
    )
    logging.info(f"total expected sleep time: {total_sleep_time:.2f} seconds")


def test_sync_task_worker():
    sync_task_worker = Worker(
        name="sync_task_worker",
        queue=copy.deepcopy(initial_queue),
        task=time.sleep,
    )
    asyncio.run(sync_task_worker.run(num_of_workers))


def test_async_task_worker():
    async_task_worker = Worker(
        name="async_task_worker",
        queue=copy.deepcopy(initial_queue),
        task=asyncio.sleep,
    )
    asyncio.run(async_task_worker.run(num_of_workers))


def test_sleep_worker():
    name="sleep_worker"
    queue=copy.deepcopy(initial_queue)
    task=asyncio.sleep

    asyncio.run(sleep_worker_test(name, queue, task))


if __name__ == "__main__":
    test_sync_task_worker()
    test_async_task_worker()
    test_sleep_worker()
