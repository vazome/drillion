"""A queue worker. It takes jobs until it is told to stop, then finishes the one in hand.

`docker stop` sends SIGTERM to PID 1. This process only receives it if it *is* PID 1."""

import argparse
import signal
import time

parser = argparse.ArgumentParser()
parser.add_argument("--queue", required=True)
parser.add_argument("--concurrency", type=int, default=1)
args = parser.parse_args()

running = True


def stop(signum, frame):
    global running
    running = False


signal.signal(signal.SIGTERM, stop)
print(f"consuming {args.queue} with {args.concurrency} workers", flush=True)
while running:
    time.sleep(1)  # take a job, do it
print("drained, exiting", flush=True)
