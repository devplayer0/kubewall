#!/usr/bin/env python3
import sys
import os.path
import signal
import subprocess

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

def log(msg):
    print(msg, file=sys.stderr)

def on_signal(num, frame):
    w.observer.stop()

class RulesWatcher(FileSystemEventHandler):
    def __init__(self, nft_file):
        self.nft_file = nft_file
        self.observer = Observer()

        self.__watch = None
        self.__next_watch()

    def apply(self):
        log(f'Applying nftables rules from {self.nft_file}')
        try:
            subprocess.check_call(['nft', '-c', '-f', self.nft_file])
            subprocess.check_call(['nft', '-f', self.nft_file])
        except subprocess.CalledProcessError:
            log('Failed to apply rules!')

    def __next_watch(self):
        if self.__watch:
            self.observer.unschedule(self.__watch)

        self.__real_nft_file = os.path.realpath(self.nft_file)
        self.__watch = self.observer.schedule(self, self.__real_nft_file)

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory or event.src_path != self.__real_nft_file:
            return

        self.apply()
        self.__next_watch()

if len(sys.argv) != 2:
    print(f'{sys.argv[0]} <nftables script>', file=sys.stderr)
    sys.exit(1)

w = RulesWatcher(sys.argv[1])
w.apply()
w.observer.start()

signal.signal(signal.SIGINT, on_signal)
signal.signal(signal.SIGTERM, on_signal)

log(f'Started watching {w.nft_file}')
w.observer.join()
