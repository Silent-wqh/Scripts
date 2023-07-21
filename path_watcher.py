"""
这是一个文件系统监控工具，它可以监控指定的目录，并在有文件或目录被创建、删除或移动时，更新一个输出文件和日志。你可以通过命令行参数指定配置文件的路径。如果没有指定，程序将使用默认的配置文件路径。

使用方式：
```
python path_watcher.py [-c CONFIG_FILE]
```

参数：
-c CONFIG_FILE, --config_file CONFIG_FILE
    指定配置文件的路径。默认为程序所在目录的config\path_watcher_config_py.json。

配置文件格式：
配置文件是一个JSON文件，包含以下字段：
```
{
    "path": "/path/to/directory",
    "output_file": "/path/to/output_file",
    "log_file": "/path/to/log_file",
    "log_level": "info",
    "recursive": false
}
```
- "path"：要监控的目录的路径。
- "output_file"：输出文件的路径。如果没有指定，将使用默认的路径。
- "log_file"：日志文件的路径。如果没有指定，将使用默认的路径。
- "log_level"：日志级别选项，可选值包括 "debug"、"info"。默认为 "info"，表示记录重要的监控事件和信息。
- "recursive"：递归监控选项，设置为 true 表示监控目录及其子文件夹的变化，设置为 false 表示仅监控一级文件夹和一级文件的变化。

输出文件格式：
输出文件是一个纯文本文件，记录了监控路径下一级文件夹和一级文件的变化列表。每个变化项占据一行，文件夹以斜杠结尾表示。

日志级别和对应级别输出内容：
- DEBUG（调试）：最详细的日志级别，用于输出程序的详细调试信息，包括每次监控事件的细节和更新的文件列表。这个级别适合在需要进行更深入的调试或详细追踪的情况下使用。
- INFO（信息）：默认的日志级别，用于输出程序的运行状态和监控结果的关键信息。在这个级别下，程序会输出目录发生的变化，以及其他重要的监控事件和信息。

请根据实际需要，选择合适的日志级别来控制日志输出的详细程度。在调试时，可以使用 DEBUG 级别来获取更详细的信息；在正常运行时，可以使用 INFO 级别来查看关键的监控结果和事件。

默认情况下，日志级别设置为 INFO，以提供主要的程序运行状态和监控结果。
"""

import os
import json
import logging
import argparse
import time
import signal
from typing import Any, Dict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, EVENT_TYPE_MOVED


class MyHandler(FileSystemEventHandler):
    def __init__(self, output_file: str, recursive: bool, path: str or list):
        self.entry_list = []  # List to store files and subdirectories in the directory
        self.output_file = output_file  # Path to the output file
        self.recursive = recursive  # Whether to monitor subdirectories recursively
        self.path = path  # Paths to be monitored

    def on_created(self, event):
        super().on_created(event)
        logging.info(f"{'Directory' if event.is_directory else 'File'} created: {event.src_path}")
        self.update_entry_list()
        self.save_entry_list_to_output()

    def on_deleted(self, event):
        super().on_deleted(event)
        logging.info(f"{'Directory' if event.is_directory else 'File'} deleted: {event.src_path}")
        self.update_entry_list()
        self.save_entry_list_to_output()

    def on_moved(self, event):
        super().on_moved(event)
        if event.event_type == EVENT_TYPE_MOVED:
            logging.info(f"{'Directory' if event.is_directory else 'File'} moved: {event.src_path} -> {event.dest_path}")
            self.update_entry_list()
            self.save_entry_list_to_output()

    def update_entry_list(self):
        self.entry_list = []
        paths = self.path if isinstance(self.path, list) else [self.path]
        for path in paths:
            if self.recursive:
                for root, dirs, files in os.walk(path):
                    for dir_name in dirs:
                        if dir_name != os.path.basename(path):
                            self.entry_list.append(os.path.relpath(os.path.join(root, dir_name), path) + "/")
                    for file_name in files:
                        self.entry_list.append(os.path.relpath(os.path.join(root, file_name), path))
            else:
                for entry in os.scandir(path):
                    if entry.is_dir() and not entry.is_symlink():
                        self.entry_list.append(entry.name + "/")
                    elif entry.is_file() and not entry.is_symlink():
                        self.entry_list.append(entry.name)

    def save_entry_list_to_output(self):
        with open(self.output_file, "w") as f:
            f.write("\n".join(self.entry_list))

    def on_any_event(self, event):
        if event.is_directory:
            if not self.recursive and not event.src_path.endswith("/"):
                return
            logging.debug(f"Directory changed: {event.src_path}")
        else:
            logging.debug(f"File changed: {event.src_path}")

        self.update_entry_list()
        self.save_entry_list_to_output()


def signal_handler(signal, frame):
    logging.info("Received interrupt signal. Stopping observer...")
    observer.stop()
    exit(0)  # Exit the program


def load_config(path_to_config_file: str) -> Dict[str, Any]:
    try:
        with open(path_to_config_file) as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Configuration file {path_to_config_file} not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error parsing configuration file {path_to_config_file}. Please check if it is a valid JSON file.")
        exit(1)

    return config


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor changes in a directory.')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config_file = os.path.join(script_dir, "config", "path_watcher_config_py.json")
    parser.add_argument('-c', '--config_file', default=default_config_file, help='Path to the configuration file.')
    args = parser.parse_args()

    config = load_config(args.config_file)

    path = config["path"]
    output_file = config.get("output_file", os.path.join(script_dir, "output", "path_watcher_output_py.txt"))
    log_file = config.get("log_file", os.path.join(script_dir, "log", "path_watcher_log_py.txt"))
    log_level = config.get("log_level", "info")
    recursive = config.get("recursive", False)

    logging.basicConfig(filename=log_file, level=log_level.upper(), format="%(asctime)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)

    event_handler = MyHandler(output_file, recursive, path)
    observer = Observer()

    if isinstance(path, list):
        for p in path:
            observer.schedule(event_handler, p, recursive=recursive)
    else:
        observer.schedule(event_handler, path, recursive=recursive)
    signal.signal(signal.SIGINT, signal_handler)

    logging.info("Starting observer...")
    observer.start()

    event_handler.update_entry_list()
    event_handler.save_entry_list_to_output()

    try:
        while True:
            time.sleep(1)  # Sleep to reduce CPU usage
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt. Stopping observer...")
        observer.stop()

    observer.join()
    logging.info("Observer stopped.")