import os
import shutil
import argparse
from datetime import datetime

def classify_files_by_year(target_dir, keep_current_year_files_in_root=True):
    # 获取目标文件夹下的所有文件
    files = os.listdir(target_dir)
    current_year = datetime.now().year
    for file_name in files:
        # 获取文件的全路径
        file_path = os.path.join(target_dir, file_name)
        # 获取文件的创建时间和修改时间，并选择其中较早的一个，然后格式化为年份
        create_time = os.path.getctime(file_path)
        modify_time = os.path.getmtime(file_path)
        file_year = datetime.fromtimestamp(min(create_time, modify_time)).year
        # 如果启用了keep_current_year_files_in_root选项，并且文件的年份是当前年份，那么直接跳过
        if keep_current_year_files_in_root and file_year == current_year:
            continue
        # 创建对应年份的文件夹，如果文件夹已经存在则不会创建
        os.makedirs(os.path.join(target_dir, str(file_year)), exist_ok=True)
        # 移动文件到对应的年份文件夹
        shutil.move(file_path, os.path.join(target_dir, str(file_year), file_name))

if __name__ == "__main__":
    # 创建一个命令行参数解析器
    parser = argparse.ArgumentParser(description='Classify files by year.')
    parser.add_argument('target_dir', help='The target directory.')
    parser.add_argument('--no-keep-current-year-files-in-root', action='store_true',
                        help='If specified, do not keep the files of the current year in the root directory.')

    # 解析命令行参数
    args = parser.parse_args()

    # 对目标文件夹下的文件进行分类
    classify_files_by_year(args.target_dir, not args.no_keep_current_year_files_in_root)
