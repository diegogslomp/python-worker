# Python Worker

Run sync/async tasks from a queue

Instead of creating a loop to run a task on each item in a list
```python
import time
import random

while True:
    random_numbers = []
    for _ in range(10):
        random_numbers.append(random.uniform(0.05, 1.0))

    for sleep_for in random_numbers:
        time.sleep(sleep_for)
```

Create workers to do the task from a queue of items
```python
from asyncio import Queue
from worker import Work
import asyncio
import logging
import random


def populate_queue(queue: Queue) -> None:
    for _ in range(10):
        sleep_for = random.uniform(0.05, 1.0)
        queue.put_nowait(sleep_for)


async def do_forever(work: Work) -> None:
    try:
        while True:
            populate_queue(work.queue)
            await work.queue.join()
            logging.debug("Queue done")
    finally:
        await work.dismiss_workers()


async def run() -> None:
    logging.basicConfig(level=logging.DEBUG)

    queue = Queue()
    work = Work(name="sleep_randomly", queue=queue, task=asyncio.sleep)

    await work.create_workers(3)
    await do_forever(work)


asyncio.run(run())
```
