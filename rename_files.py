"""
rename_files.py

这个脚本用于重命名指定目录中的所有文件。它将文件的扩展名添加到文件名的开头，以形成"扩展名.原始文件名"的格式。

用法：
    python rename_files.py /path/to/your/directory

注意：
    你需要将 "/path/to/your/directory" 替换为你的目标文件夹的实际路径。
"""

import os
import argparse

def rename_files_in_directory(target_dir):
    # 遍历目标文件夹中的所有文件
    for filename in os.listdir(target_dir):
        # 获得文件的扩展名
        ext = os.path.splitext(filename)[-1].lstrip('.').lower()

        # 创建新的文件名
        new_filename = f"{ext}.{filename}"

        # 获取文件的原始路径和新路径
        old_file_path = os.path.join(target_dir, filename)
        new_file_path = os.path.join(target_dir, new_filename)

        # 重命名文件
        os.rename(old_file_path, new_file_path)

# 创建一个解析器
parser = argparse.ArgumentParser(description='Rename files in a directory.')
# 添加一个命令行参数
parser.add_argument('directory', help='The directory where files will be renamed.')
# 解析命令行参数
args = parser.parse_args()

# 调用函数
rename_files_in_directory(args.directory)
s