"""
classify_files_by_type.py

这是一个Python脚本，它能根据文件的类型将文件分类到不同的类型文件夹中。目前支持的文件类型有视频、音频、图片、文档和压缩包，文件的类型是根据其扩展名来判断的。

这个脚本提供了一个命令行接口，只接受一个参数：
-c, --config-path：配置文件的路径，默认值是"./config/classify_files_by_type_config.yaml"。

这个脚本会从配置文件中读取配置，然后对目标文件夹下的文件进行分类。配置文件是一个YAML文件，包含了目标文件夹的路径、各类型文件夹的路径和各类型的文件扩展名。

配置文件是一个YAML格式的文件，包含以下字段：
- target_dirs：一个列表，包含一个或多个目标文件夹的路径。
- no_keep_current_year_files_in_root：一个布尔值，如果设置为true，那么当前年份的文件不会被保留在根目录中。

下面是一个配置文件的例子：

target_dirs: 
  - /path/to/target_dir1
  - /path/to/target_dir2
no_keep_current_year_files_in_root: true
"""



import os
import shutil
import argparse
import yaml
from datetime import datetime

def classify_files_and_folders_by_year(target_dirs, keep_current_year_files_in_root=True):
    for target_dir in target_dirs:
        # 获取目标文件夹下的所有文件和文件夹
        items = os.listdir(target_dir)
        current_year = datetime.now().year
        for item_name in items:
            # 获取项目的全路径
            item_path = os.path.join(target_dir, item_name)
            # 如果项目是文件夹，并且它的名字是四位数（例如"2021"或"2022"），那么直接跳过
            if os.path.isdir(item_path) and item_name.isdigit() and len(item_name) == 4:
                continue
            # 获取项目的创建时间和修改时间，并选择其中较早的一个，然后格式化为年份
            create_time = os.path.getctime(item_path)
            modify_time = os.path.getmtime(item_path)
            item_year = datetime.fromtimestamp(min(create_time, modify_time)).year
            # 如果启用了keep_current_year_files_in_root选项，并且项目的年份是当前年份，那么直接跳过
            if keep_current_year_files_in_root and item_year == current_year:
                continue
            # 创建对应年份的文件夹，如果文件夹已经存在则不会创建
            os.makedirs(os.path.join(target_dir, str(item_year)), exist_ok=True)
            # 移动项目到对应的年份文件夹
            shutil.move(item_path, os.path.join(target_dir, str(item_year), item_name))

def load_config(config_path):
    with open(config_path, 'r', encoding="utf8") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    # 创建一个命令行参数解析器
    parser = argparse.ArgumentParser(description='Classify files and folders by year.')
    parser.add_argument('-t', '--target-dirs', nargs='*', help='The target directories.')
    parser.add_argument('-c', '--config-path', default='./config/classify_files_by_year_config.yaml', help='The path of the configuration file.')
    parser.add_argument('--no-keep-current-year-files-in-root', action='store_true',
                        help='If specified, do not keep the items of the current year in the root directory.')

    # 解析命令行参数
    args = parser.parse_args()

    if args.target_dirs is None:
        # 如果没有在命令行参数中指定目标文件夹，那么从配置文件中读取
        config = load_config(args.config_path)
        args.target_dirs = config['target_dirs']
        if 'no_keep_current_year_files_in_root' in config:
            args.no_keep_current_year_files_in_root = config['no_keep_current_year_files_in_root']

    # 对目标文件夹下的文件和文件夹进行分类
    classify_files_and_folders_by_year(args.target_dirs, not args.no_keep_current_year_files_in_root)
