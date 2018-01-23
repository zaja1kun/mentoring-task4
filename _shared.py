import time
import random
from contextlib import contextmanager


FILEPATH = 'working.sock'
CONSUMERS_COUNT = 10
CONSUMERS_SIMULTANEOUSLY = 3
GENERATORS_COUNT = 2
GENERATORS_MAXSLEEPTIME = 50


@contextmanager
def acquire_semaphore(semaphore):
    acquired_level = 0
    try:
        while acquired_level < CONSUMERS_SIMULTANEOUSLY:
            semaphore.acquire()
            acquired_level += 1
        yield
    finally:
        for _ in range(acquired_level):
            semaphore.release()


def launch_generator(generator_id, termination_event, semaphore, allow_consumation, generator_lock):
    counter = 0
    while not termination_event.is_set():
        with generator_lock:
            allow_consumation.clear()
            with acquire_semaphore(semaphore):
                with open(FILEPATH, mode='w') as fileobj:
                    fileobj.write(f'Generator {generator_id}: {counter}')
                counter += 1
            allow_consumation.set()
        time.sleep(random.random() * GENERATORS_MAXSLEEPTIME / 1000)


def launch_consumer(reader_id, termination_event, semaphore, allow_consumation):
    while not termination_event.is_set():
        allow_consumation.wait()
        with semaphore:
            with open(FILEPATH, mode='r') as fileobj:
                file_contents = fileobj.read()
            print(f'Reader {reader_id}: {file_contents}')
