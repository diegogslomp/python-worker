# Python Worker

Run sync/async tasks from a queue

Instead of
```python
import time
import random

some_list = []
for _ in range(10):
    some_list.append(random.uniform(0.05, 1.0))

for sleep_for in some_list:
    time.sleep(sleep_for)
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
    name="sleep_worker",
    queue=queue,
    task=asyncio.sleep,
)

# Run worker
asyncio.run(worker.run(num_of_workers=3))
```