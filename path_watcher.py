"""
文件夹监控器

这个程序会监控指定的文件夹，并在文件或文件夹被创建、删除或移动时更新输出文件和日志。你可以通过命令行参数指定配置文件的路径。如果你没有指定，那么程序将使用默认的配置文件路径。

使用方式：
python path_watcher.py [-c CONFIG_FILE]

参数：
-c CONFIG_FILE, --config_file CONFIG_FILE
    指定配置文件的路径。默认为程序所在目录的config\path_watcher_config_py.json。

配置文件格式：
配置文件是一个JSON文件，包含以下字段：
{
    "path": "/path/to/directory",
    "log_level": "info",
    "recursive": false
}
- "path"：要监控的目录的路径。
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
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, EVENT_TYPE_MOVED
import signal

# 定义一个处理文件系统事件的类，继承自FileSystemEventHandler
class MyHandler(FileSystemEventHandler):
    def __init__(self, output_file, recursive):
        self.entry_list = []  # 用于存储目录下的文件和子目录
        self.output_file = output_file  # 输出文件的路径
        self.recursive = recursive  # 是否递归监控子目录

    # 当有文件或目录被创建时，会触发此方法
    def on_created(self, event):
        super().on_created(event)
        logging.info(f"{'Directory' if event.is_directory else 'File'} created: {event.src_path}")
        self.update_entry_list()
        self.save_entry_list_to_output()

    # 当有文件或目录被删除时，会触发此方法
    def on_deleted(self, event):
        super().on_deleted(event)
        logging.info(f"{'Directory' if event.is_directory else 'File'} deleted: {event.src_path}")
        self.update_entry_list()
        self.save_entry_list_to_output()

    # 当有文件或目录被移动（包括重命名）时，会触发此方法
    def on_moved(self, event):
        super().on_moved(event)
        if event.event_type == EVENT_TYPE_MOVED:
            logging.info(f"{'Directory' if event.is_directory else 'File'} moved: {event.src_path} -> {event.dest_path}")
            self.update_entry_list()
            self.save_entry_list_to_output()

    # 更新目录下的文件和子目录列表
    def update_entry_list(self):
        self.entry_list = []
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

    # 将目录下的文件和子目录列表保存到输出文件中
    def save_entry_list_to_output(self):
        with open(self.output_file, "w") as f:
            f.write("\n".join(self.entry_list))

    # 当有任何文件系统事件发生时，会触发此方法
    def on_any_event(self, event):
        if event.is_directory:
            if not self.recursive and not event.src_path.endswith("/"):
                return
            logging.debug(f"Directory changed: {event.src_path}")
        else:
            logging.debug(f"File changed: {event.src_path}")

        self.update_entry_list()
        self.save_entry_list_to_output()

if __name__ == "__main__":
    # 使用argparse库处理命令行参数
    parser = argparse.ArgumentParser(description='Monitor changes in a directory.')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config_file = os.path.join(script_dir, "config", "path_watcher_config_py.json")
    parser.add_argument('-c', '--config_file', default=default_config_file, help='Path to the configuration file.')
    args = parser.parse_args()

    # 读取配置文件
    try:
        with open(args.config_file) as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Configuration file {args.config_file} not found.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error parsing configuration file {args.config_file}. Please check if it is a valid JSON file.")
        exit(1)

    path = config["path"]
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "output", "path_watcher_output_py.txt")
    log_file = os.path.join(script_dir, "log", "path_watcher_log_py.txt")
    log_level = config.get("log_level", "info")
    recursive = config.get("recursive", False)

    # 配置日志
    logging.basicConfig(filename=log_file, level=log_level.upper(), format="%(asctime)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)

    # 创建事件处理器和观察者
    event_handler = MyHandler(output_file, recursive)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=recursive)

    # 定义信号处理函数，用于在接收到中断信号时停止观察者
    def signal_handler(signal, frame):
        logging.info("Received interrupt signal. Stopping observer...")
        observer.stop()
        exit(0)  # Add this line to exit the program

    signal.signal(signal.SIGINT, signal_handler)

    logging.info("Starting observer...")
    observer.start()

    event_handler.update_entry_list()
    event_handler.save_entry_list_to_output()

    # 主循环，等待键盘中断信号
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info("Received keyboard interrupt. Stopping observer...")
        observer.stop()

    observer.join()
    logging.info("Observer stopped.")
