"""
rename_files.py

这个脚本用于重命名指定目录中的所有文件。它将文件的扩展名更改为指定的前缀，并将其添加到文件名的开头，以形成"新前缀.原始文件名.原始扩展名"的格式。

用法：
    python rename_files.py /path/to/your/directory

注意：
    你需要将 "/path/to/your/directory" 替换为你的目标文件夹的实际路径。

规则：
    匹配：^xlsx?(.*?)$ 替换：Excel\\1
    匹配：^docx?(.*?)$ 替换：Word\\1
    匹配：^pptx?(.*?)$ 替换：PPT\\1
    匹配：^txt(.*?)$ 替换：Text\\1
    匹配：^^(zip|7z|rar)(.*?)$ 替换：Archive\\2
    匹配：^pdf(.*?)$ 替换：PDF\\1
    匹配：^(json|xml|yaml|csv)(.*?)$ 替换：DataExchangeFormat\\2
    匹配：^(jpe?g|png|gif|bmp|svg)(.*?)$ 替换：Image\\2
    匹配：^(mp4|flv|webm|m4v|mov|mkv|avi)(.*?)$ 替换：Video\\2
    匹配：^(mp3|wav|flac|aac)(.*?)$ 替换：Audio\\2
    匹配：^colpkg(.*?)$ 替换：Anki\\1
    匹配：^vsdx?(.*?)$ 替换：Visio\\1
"""

import os
import argparse
import re

def rename_files_in_directory(target_dir):
    # 定义重命名规则
    rules = [
        (r'^xlsx?(.*?)$', 'Excel\\1'),
        (r'^docx?(.*?)$', 'Word\\1'),
        (r'^pptx?(.*?)$', 'PPT\\1'),
        (r'^txt(.*?)$', 'Text\\1'),
        (r'^(zip|7z|rar)(.*?)$', 'Archive\\2'),
        (r'^pdf(.*?)$', 'PDF\\1'),
        (r'^(json|xml|yaml|csv)(.*?)$', 'DataExchangeFormat\\2'),
        (r'^(jpe?g|png|gif|bmp|svg)(.*?)$', 'Image\\2'),
        (r'^(mp4|flv|webm|m4v|mov|mkv|avi)(.*?)$', 'Video\\2'),
        (r'^(mp3|wav|flac|aac)(.*?)$', 'Audio\\2'),
        (r'^colpkg(.*?)$', 'Anki\\1'),
        (r'^vsdx?(.*?)$', 'Visio\\1')
    ]

    # 遍历目标文件夹中的所有文件和文件夹
    for filename in os.listdir(target_dir):
        # 确保只处理文件
        if os.path.isfile(os.path.join(target_dir, filename)):
            # 获得文件的扩展名和基础名
            base_name = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[-1].lstrip('.').lower()

            # 对于每个规则，检查文件扩展名是否匹配
            for pattern, replacement in rules:
                if re.match(pattern, ext):
                    # 如果匹配，使用替换模式生成新的文件名
                    new_ext = re.sub(pattern, replacement, ext)
                    new_filename = f"{new_ext}.{base_name}.{ext}"
                    break
            else:
                # 如果没有任何规则匹配，保持原样
                new_filename = filename

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
