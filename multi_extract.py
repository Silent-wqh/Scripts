"""
multi_extract.py
功能：
    本程序用于递归解压指定路径下的所有压缩文件，包括多层嵌套的压缩文件。
    支持的压缩文件类型包括：rar、zip、tgz、tar。解压完成后会删除原来的压缩文件。

使用方法：
    运行命令：python multi_extract.py <目标路径>
    例如：python multi_extract.py "your/path"

注意事项：
    1. 确保 7z 的可执行文件在系统的 PATH 环境变量中可用。
    2. 程序会删除所有解压后的原压缩文件，请确保备份重要数据。
    3. 本程序会递归解压所有子目录下的压缩文件，但会忽略以点（.）开头的文件。
"""

import os
import subprocess
import sys

def extract_files(path):
    # 支持的压缩文件扩展名
    extensions = ['.rar', '.zip', '.tgz', '.tar']
    total_files = 0

    # 循环检查路径，直到没有新的压缩文件
    while True:
        extracted_files = False

        # 遍历路径下的所有文件和子目录
        for root, _, files in os.walk(path):
            for file in files:
                if any(file.endswith(ext) for ext in extensions) and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    print(f'Extracting {file_path}...')
                    total_files += 1

                    # 调用 7z 命令来解压文件
                    result = subprocess.run(['7z', 'x', file_path, f'-o{root}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    # 检查是否成功解压
                    if result.returncode != 0:
                        print(f"An error occurred while extracting {file_path}: {result.stderr.decode().strip()}")
                    else:
                        # 删除原压缩文件
                        os.remove(file_path)
                        print(f"Progress: {total_files}")
                        extracted_files = True

        # 如果在这一轮中没有解压任何文件，则退出循环
        if not extracted_files:
            break

    print('Extraction complete.')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python multi_extract.py <path>")
        sys.exit(1)

    path = sys.argv[1]
    extract_files(path)
