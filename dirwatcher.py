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
                    format='[%(levelname)8s] [%(lineno)d]: %(asctime)s - %(message)s')

logger = logging.getLogger(__name__)

signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                if v.startswith('SIG') and not v.startswith('SIG_'))

def init_parser():
    """[summary]
    
    Returns:
        [type] -- [description]
    """
    p = argparse.ArgumentParser(
        description='Monitor a directory and log changes to monitored files')
    p.add_argument("--dir", type=str,
                help="Absolute or relative directory to monitor. NO preceeding text on relative paths ex './'", default=os.getcwd())
    p.add_argument("--ext", type=str,
                help="File extension to monitor ex .log .txt", default=".txt")
    p.add_argument("--int", type=int, help="Timeout interval in seconds", default=1)
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
    # log the associated signal name (the python3 way)
    logger.warning('Received ' + signal.Signals(sig_num).name)
    exit_event.set()
    


def watch_dir(args):
    """[summary]
    
    Arguments:
        args {[type]} -- [description]
    """
    file_list = []
    for file in os.listdir(os.getcwd()):
        if file.endswith(args.ext):
            file_list.append(file)
            find_files(file)
            read_new_lines(file, args)
    new_arr = set(file_list).difference(filedict.keys())



def find_files(file):
    """[summary]
    
    Arguments:
        file {[type]} -- [description]
    """
    if not file in filedict:
        logger.info(f"added file {file} to watch list")
        filedict[file] = {
            "mod_date": os.stat(file)[8],
            "first_read": True
        }
    

def read_new_lines(file, args):
    """[summary]
    
    Arguments:
        file {[type]} -- [description]
        args {[type]} -- [description]
    """
    current_mod_date = os.stat(file)[8]
    if not current_mod_date == filedict[file]['mod_date'] or filedict[file]['first_read']:
        filedict[file]['first_read'] = False
        filedict[file]['mod_date']   = current_mod_date
        with open(file, 'r') as f:
            line_no = 0
            if 'byte_read_offset' in filedict[file].keys():
                f.seek(filedict[file]["byte_read_offset"])
            for i, line in enumerate(f.readlines()):
                line_no = i
                if args.magicStr in line and "line_no" in filedict[file].keys():
                    logger.debug(f"Magic string found in {file} on line {filedict[file]['line_no']+i}")
                elif args.magicStr in line:
                    logger.debug(f"Magic string found in {file} on line {i+1}")
            filedict[file]["byte_read_offset"] = f.tell()
            if "line_no" in filedict[file].keys():
                filedict[file]["line_no"] += line_no
            else:
                filedict[file]["line_no"] = line_no


def main():
    """[summary]
    """
    args = init_parser()
    os.chdir(args.dir)
    polling_interval = args.int
    for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]:
        signal.signal(sig, signal_handler)

    logger.info(f"""
-----------------------------------------------
Dirwatcher Started @ {time.strftime("%Y/%m/%d, %H:%M:%S - %Z", time.localtime(time.time()))}
-----------------------------------------------""")
    logger.info(f"Log started with watched Dir {args.dir} Timeout {args.int} magicStr {args.magicStr} and extension {args.ext}")
    #TODO: log adding and removal of files

    while not exit_event.is_set():
        try:
            watch_dir(args)
        except Exception as e:
            logger.error(e)

        exit_event.wait(polling_interval)

    logger.info(f"""
---------------------------------------------
Dirwatcher Ended @ {time.strftime("%Y/%m/%d, %H:%M:%S - %Z", time.localtime(time.time()))}
---------------------------------------------""")



if __name__ == "__main__":
    main()