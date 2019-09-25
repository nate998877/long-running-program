#!/usr/bin/env python3
import threading
import time
import signal
import asyncio
import argparse
import os
import logging

from datetime import timedelta

"""
DONE: implement cmd line args {watchDir:dir, magicStr:str} (argparse)
TODO: implement Timed loop to monitor watchDir (threading + time)
TODO: implement signal handling (signal)
TODO: implement file cacheing (dict)
TODO: implement async dir searching (asyncio)
TODO: implement logger
TODO: implement logging for file remove/add/magic string
TODO: implement graceful exit
"""


exit_flag = False
WAIT_TIME_SECONDS = 1
FileDict = {}


class ProgramKilled(Exception):
    pass


def foo():
    print(time.ctime())


def signal_handler(signum, frame):
    raise ProgramKilled


class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.stopped.set()
        self.join()

    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)



def init_parser():
    p = argparse.ArgumentParser(
        description='Monitor a directory and log changes to monitored files')
    p.add_argument("--dir", type=str,
                    help="Directory to monitor", default=os.getcwd())
    p.add_argument("--ext", type=str,
                    help="File extension filter", default="txt")
    p.add_argument("--int", type=int, help="Timeout interval", default=5)
    p.add_argument("magicStr", type=str, help="String to monitor for")

    return p.parse_args()


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    global exit_flag
    exit_flag = True
    logger = logging.getLogger("watcher")
    # log the associated signal name (the python3 way)
    print(str(sig_num))
    logger.warning('Received ' + signal.Signals(sig_num).name)
    # log the signal name (the python2 way)
    signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                    if v.startswith('SIG') and not v.startswith('SIG_'))
    logger.warning('Received ' + signames[sig_num])


def main():
    polling_interval = 10
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    while not exit_flag:
        try:
            print(exit_flag)
            # call my directory watching function..
        except Exception as e:
            print("bar")
            # This is an UNHANDLED exception
            # Log an ERROR level message here

            # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(polling_interval)

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start.

#     job = Job(interval=timedelta(seconds=WAIT_TIME_SECONDS), execute=foo)
#     job.start()

#     while True:
#         try:
#             time.sleep(1)
#         except ProgramKilled:
#             print("Program killed: running cleanup code")
#             job.stop()
#             break


if __name__ == "__main__":
    main()
