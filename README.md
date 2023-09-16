# Python Worker

Run sync/async tasks from a queue

Instead of creating a loop to run a task on each item in a list
```python
import time
import random

some_list = []
for _ in range(10):
    some_list.append(random.uniform(0.05, 1.0))

for sleep_for in some_list:
    time.sleep(sleep_for)
```

Create workers to do the task from a queue of items
```python
from worker import Work
from asyncio import Queue
import asyncio
import random
import logging


async def run():
    logging.basicConfig(level=logging.DEBUG)

    # Populate a queue
    queue = Queue()
    for _ in range(10):
        sleep_for = random.uniform(0.05, 1.0)
        queue.put_nowait(sleep_for)

    # Create a work
    work = Work(name="sleep_randonly", queue=queue, task=asyncio.sleep)

    # Create 3 workers to do the task
    await work.create_workers(3)

    # Wait queue finish
    await queue.join()

    # Dismiss workers
    await work.dismiss_workers()


# Run
asyncio.run(run())
```
