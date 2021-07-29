#!/usr/bin/env python3
import sys
import signal
import subprocess

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

def log(msg):
    print(msg, file=sys.stderr)

def on_signal(num, frame):
    observer.stop()

class Handler(FileSystemEventHandler):
    def __init__(self, nft_file):
        self.nft_file = nft_file

    def apply(self):
        log(f'Applying nftables rules from {self.nft_file}')
        try:
            subprocess.check_call(['nft', '-f', self.nft_file])
        except subprocess.CalledProcessError:
            log('Failed to apply rules!')

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory or event.src_path != self.nft_file:
            return

        self.apply()

if len(sys.argv) != 2:
    print(f'{sys.argv[0]} <nftables script>', file=sys.stderr)
    sys.exit(1)

h = Handler(sys.argv[1])
h.apply()

observer = Observer()
observer.schedule(h, h.nft_file)
observer.start()

signal.signal(signal.SIGINT, on_signal)
signal.signal(signal.SIGTERM, on_signal)

log(f'Started watching {h.nft_file}')
observer.join()