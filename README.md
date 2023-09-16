# Python Worker

Run sync/async tasks from a queue

Instead of
```python
def do(thing):
    # Do thing
    pass

some_list = []
for x in some_list:
    do(x)
```

Create workers to do tasks from a queue of items
```python
from worker import Worker
from asyncio import Queue
import asyncio
import random
import logging

logging.basicConfig(level=logging.DEBUG)

# Populate a queue
queue = Queue()
for _ in range(10):
    sleep_for = random.uniform(0.05, 1.0)
    queue.put_nowait(sleep_for)

# Create a worker
worker = Worker(
    name="async_sleep_worker",
    queue=queue,
    task=asyncio.sleep,
)

# Run worker
asyncio.run(worker.run(num_of_workers=3))
```