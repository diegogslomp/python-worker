import time
import random


def get_list() -> list:
    random_numbers = []
    for _ in range(10):
        random_numbers.append(random.uniform(0.05, 1.0))
    return random_numbers

while True:
    random_numbers = get_list()
    for sleep_for in random_numbers:
        time.sleep(sleep_for)
        print(sleep_for)
