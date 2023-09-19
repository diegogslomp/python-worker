from asyncio import Queue
from worker import Work
import asyncio
import logging
import readme
import random
import time
import copy


num_of_sleepers = 10
num_of_workers = 5

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s"
)

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
    asyncio.run(work.run_once(num_of_workers))


def test_async_task_work():
    work = Work(
        name="async_task_worker",
        queue=copy.deepcopy(initial_queue),
        task=asyncio.sleep,
    )
    asyncio.run(work.run_once(num_of_workers))


def test_manual_task_work():
    async def run():
        work = Work(
            name="manual_task_worker",
            queue=copy.deepcopy(initial_queue),
            task=asyncio.sleep,
        )
        await work.create_workers(num_of_workers)
        await work.queue.join()
        await work.dismiss_workers()

    asyncio.run(run())


def test_readme():
    asyncio.run(readme.run())


if __name__ == "__main__":
    try:
        test_sync_task_work()
        test_async_task_work()
        test_manual_task_work()
        test_readme()
    except (KeyboardInterrupt, SystemExit):
        pass
