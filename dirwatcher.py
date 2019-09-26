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
                    format='[%(levelname)8s] [%(lineno)d]: %(asctime)s - %(message)s')



def init_parser():
    p = argparse.ArgumentParser(
        description='Monitor a directory and log changes to monitored files')
    p.add_argument("--dir", type=str,
                help="Absolute or relative directory to monitor. NO preceeding text on relative paths ex './'", default=os.getcwd())
    p.add_argument("--ext", type=str,
                help="File extension to monitor ex .log .txt", default=".txt")
    p.add_argument("--int", type=int, help="Timeout interval in seconds", default=5)
    p.add_argument("magicStr", type=str, help="String to log if discovered in monitored directory")

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
    logging.warning('Received ' + signal.Signals(sig_num).name)
    # log the signal name (the python2 way)
    signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                    if v.startswith('SIG') and not v.startswith('SIG_'))
    logging.warning('Received ' + signames[sig_num])


def watch_dir(args):
    for file in os.listdir(args.dir):
        if not os.path.isabs(file):
            file = f'{os.getcwd()}/{args.dir}/{file}'
        find_files(file)
        read_new_lines(file, args)


def find_files(file):
    if not file in filedict:
        filedict[file] = {
            "mod_date": os.stat(file)[8],
            "first_read": True
        }

def read_new_lines(file, args):
    print(filedict)
    current_mod_date = os.stat(file)[8]
    if not current_mod_date == filedict[file]['mod_date'] or filedict[file]['first_read']:
        filedict[file]['first_read'] = False
        filedict[file]['mod_date']   = current_mod_date
        print(file)
        with open(file, 'r') as f:
            if "byte_read_offset" in filedict.keys():
                f.seek(filedict[file]["byte_read_offset"])
            for line in f.readlines():
                if args.magicStr in line:
                    logging.debug(f"Magic string found in {file} at byte offset {f.tell()}") #I don't know how to convert byte offset to line #. I assume enumerate won't work
            filedict[file]["byte_read_offset"] = f.tell()
            print(filedict, "two")

def main():
    args = init_parser()
    polling_interval = args.int
    for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]:
        signal.signal(sig, signal_handler)

    logging.info(f"""
-----------------------------------------------
Dirwatcher Started @ {time.strftime("%Y/%m/%d, %H:%M:%S - %Z", time.localtime(time.time()))}
-----------------------------------------------""")

    while not exit.is_set():
        # try:
        watch_dir(args)
        # except Exception as e:
        #     logging.error(e)

        exit.wait(polling_interval)

    logging.info(f"""
---------------------------------------------
Dirwatcher Ended @ {time.strftime("%Y/%m/%d, %H:%M:%S - %Z", time.localtime(time.time()))}
---------------------------------------------""")



if __name__ == "__main__":
    main()
