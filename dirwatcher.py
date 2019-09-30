#!/usr/bin/env python3
import time
from threading import Event
import signal
import argparse
import os
import logging


filedict = {}
exit_event = Event()
logging.basicConfig(filename="watcher.log", level=logging.DEBUG,
                    format='[%(levelname)7s] [%(lineno)d]: %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def init_parser():
    """Creates then returns the CLI for DirWatcher

    Returns:
        dict -- Parsed comand line arguments
    """
    p = argparse.ArgumentParser(
        description='Monitor a directory and log changes to monitored files')
    p.add_argument("--dir", type=str,
                   help="Absolute or relative directory to monitor. NO preceeding text on relative paths ex './'", default=os.getcwd())
    p.add_argument("--ext", type=str,
                   help="File extension to monitor ex .log .txt", default=".txt")
    p.add_argument("--int", type=int,
                   help="Timeout interval in seconds", default=1)
    p.add_argument("magicStr", type=str,
                   help="String to log if discovered in monitored directory")

    return p.parse_args()


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name (the python3 way)
    logger.warning('Received ' + signal.Signals(sig_num).name)
    exit_event.set()


def watch_dir(args):
    """control logic for monitoring dir

    Arguments:
        args {dict} -- args parsed from command line
    """
    file_list = []
    for file in os.listdir(os.getcwd()):
        if file.endswith(args.ext):
            file_list.append(file)
            update_file_dict(file)
            read_new_lines(file, args)
    diff_set = set(filedict.keys()).difference(file_list)
    if diff_set:
        for item in diff_set:
            del filedict[item]
            logger.warn(
                f"{item} was deleted from {args.dir} and was removed from watch list")


def update_file_dict(file):
    """Adds File to global filedict object

    Arguments:
        file {str} -- string representing path to file
    """
    if not file in filedict:
        logger.info(f"added file {file} to watch list")
        filedict[file] = {
            "mod_date": os.stat(file)[8],
            "first_read": True
        }


def read_new_lines(file, args):
    """Reads lines that have been added to any watched documents since the last
       time this function has run. Including all lines in new files.

    Arguments:
        file {str} -- string representing path to file
        args {dict} -- parsed command line args
    """
    current_mod_date = os.stat(file)[8]

    if not current_mod_date == filedict[file]['mod_date'] or filedict[file]['first_read']:
        filedict[file]['first_read'] = False
        filedict[file]['mod_date'] = current_mod_date

        with open(file, 'r') as f:
            line_no = 0
            if 'byte_read_offset' in filedict[file].keys():
                f.seek(filedict[file]["byte_read_offset"])

            for i, line in enumerate(f.readlines()):
                line_no = i
                if args.magicStr in line and "line_no" in filedict[file].keys():
                    logger.debug(
                        f"Magic string found in {file} on line {filedict[file]['line_no']+i}")
                elif args.magicStr in line:
                    logger.debug(f"Magic string found in {file} on line {i+1}")

            filedict[file]["byte_read_offset"] = f.tell()
            if "line_no" in filedict[file].keys():
                filedict[file]["line_no"] += line_no
            else:
                filedict[file]["line_no"] = line_no


def main():
    """Main function that calls other functions and contains main loop
    """
    args = init_parser()

    polling_interval = args.int
    for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]:
        signal.signal(sig, signal_handler)

    logger.info(
        f"""\n{"-"*47}\nDirwatcher Started @ {time.strftime('%Y/%m/%d, %H:%M:%S - %Z', time.localtime(time.time()))}\n{"-"*47}""")
    logger.info(
        f"Log started with \x7B dir : '{args.dir}', timeout : {args.int}s, magicStr : '{args.magicStr}', extension : '{args.ext}' \x7D")

    while not exit_event.is_set():
        try:
            if not os.getcwd().endswith(args.dir):
                os.chdir(args.dir)
            watch_dir(args)
        except Exception as e:
            logger.error(e)

        exit_event.wait(polling_interval)

    logger.info(
        f"\n{'-'*45}\nDirwatcher Ended @ {time.strftime('%Y/%m/%d, %H:%M:%S - %Z', time.localtime(time.time()))}\n{'-'*45}")


if __name__ == "__main__":
    main()
