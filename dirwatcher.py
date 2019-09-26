#!/usr/bin/env python3
import time
from threading import Event
import signal
import asyncio
import argparse
import os
import logging


"""
DONE: implement cmd line args {watchDir:dir, magicStr:str} (argparse)
DONE: implement signal handling (signal)
DONE: implement Timed loop to monitor watchDir (threading + time)
DONE: implement file cacheing (dict)
DONEish: implement logging
TODO: implement graceful exit
TODO: implement async dir searching (asyncio)
TODO: implement logging for file remove/add/magic string
"""


exit_flag = False
WAIT_TIME_SECONDS = 1
filedict = {}
exit = Event()
logging.basicConfig(filename="watcher.log", level=logging.DEBUG,
                    format='%(levelname)s : %(asctime)s - %(message)s')



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
    exit.set()
    global exit_flag
    exit_flag = True
    # log the associated signal name (the python3 way)
    print(str(sig_num))
    logging.warning('Received ' + signal.Signals(sig_num).name)
    # log the signal name (the python2 way)
    signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                    if v.startswith('SIG') and not v.startswith('SIG_'))
    logging.warning('Received ' + signames[sig_num])


def watch_dir(dir):
    for path in os.listdir(dir):
        path = f'{os.getcwd()}/{path}'
        print(path)
        find_files(path)
        read_new_lines(path)


def find_files(file):
    if not file in filedict:
        filedict[file] = {
            "mod_date": os.stat(file)[8]
        }

def read_new_lines(file):
    current_mod_date = os.stat(file)[8]
    if not current_mod_date == filedict[file]['mod_date']:
        with os.open(file, 'r') as f:
            "byte_read_offset" in filedict.keys()



def main():
    args = init_parser()
    polling_interval = args.int
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

    while not exit.is_set():
        try:
            watch_dir(args.dir)
        except Exception as e:
            logging.error(e)

        exit.wait(polling_interval)



if __name__ == "__main__":
    main()
