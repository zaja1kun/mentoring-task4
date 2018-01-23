#!/usr/bin/env python3
import signal
import time
from multiprocessing import Process, Event, Lock, BoundedSemaphore
import _shared
from _shared import launch_consumer, launch_generator


def process_target(func):
    def _wrapper(*args, **kwargs):
        print(args)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        return func(*args, **kwargs)
    return _wrapper


def main():
    termination_event = Event()
    semaphore = BoundedSemaphore(_shared.CONSUMERS_SIMULTANEOUSLY)
    allow_consumation = Event()
    generator_lock = Lock()

    workers = []
    for generator_id in range(_shared.GENERATORS_COUNT):
        args=(generator_id, termination_event, semaphore, allow_consumation, generator_lock)
        workers.append(Process(target=process_target(launch_generator), args=args))
        workers[-1].start()
    for reader_id in range(_shared.CONSUMERS_COUNT):
        args=(reader_id, termination_event, semaphore, allow_consumation)
        workers.append(Process(target=process_target(launch_consumer), args=args))
        workers[-1].start()

    try:
        while not termination_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        termination_event.set()
    finally:
        for worker in workers:
            worker.join()


if __name__ == '__main__':
    main()
