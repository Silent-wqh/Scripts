"""
classify_files_by_year.py

这是一个Python脚本，它能根据文件的创建或者修改时间（取其中最早的一项）将文件分类到不同的年份文件夹中。它可以处理一个或者多个目标文件夹，同时也可以处理目标文件夹中的子文件夹。

这个脚本提供了一个命令行接口，可以接受以下参数：
-t, --target-dirs：一个或者多个目标文件夹的路径。
-c, --config-path：配置文件的路径，默认值是"./config/classify_files_by_year_config.yaml"。
--no-keep-current-year-files-in-root：如果设置了这个选项，那么当前年份的文件不会被保留在根目录中。

如果没有在命令行参数中指定目标文件夹，那么脚本会从配置文件中读取目标文件夹的路径。配置文件是一个YAML文件，包含了目标文件夹的路径和其他选项。

配置文件是一个YAML格式的文件，包含以下字段：
- target_dir：目标文件夹的路径。
- type_dirs：一个映射，键是文件类型的名称，值是对应类型文件夹的路径。
- type_exts：一个映射，键是文件类型的名称，值是一个列表，包含了该类型的所有文件扩展名。

下面是一个配置文件的例子：

target_dir: /path/to/target_dir
type_dirs:
  视频: /path/to/video/dir
  音频: /path/to/audio/dir
  图片: /path/to/image/dir
  文档: /path/to/document/dir
  压缩包: /path/to/archive/dir
type_exts:
  视频: [.mp4, .mkv, .flv, .avi, .mov, .wmv]
  音频: [.mp3, .wav, .flac, .aac, .ogg, .wma]
  图片: [.jpg, .jpeg, .png, .gif, .bmp, .tiff, .ico]
  文档: [.txt, .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx]
  压缩包: [.zip, .rar, .7z, .tar, .gz]
"""


import os
import shutil
import argparse
import yaml

def classify_files_by_type(target_dir, type_dirs, type_exts):
    # 获取目标文件夹下的所有文件
    files = os.listdir(target_dir)
    for file_name in files:
        # 获取文件的全路径
        file_path = os.path.join(target_dir, file_name)
        # 如果是文件夹，跳过
        if os.path.isdir(file_path):
            continue
        # 获取文件的扩展名
        file_ext = os.path.splitext(file_name)[-1].lower()
        # 判断文件的类型，并移动到对应的文件夹
        for type_name, exts in type_exts.items():
            if file_ext in exts:
                target_type_dir = type_dirs[type_name]
                os.makedirs(target_type_dir, exist_ok=True)
                shutil.move(file_path, os.path.join(target_type_dir, file_name))
                break

def load_config(config_path):
    with open(config_path, 'r', encoding="utf8") as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    # 创建一个命令行参数解析器
    parser = argparse.ArgumentParser(description='Classify files by type.')
    parser.add_argument('-c', '--config-path', default='./config/classify_files_by_type_config.yaml', help='The path of the configuration file.')

    # 解析命令行参数
    args = parser.parse_args()

    # 从配置文件中读取配置
    config = load_config(args.config_path)

    # 对目标文件夹下的文件进行分类
    classify_files_by_type(config['target_dir'], config['type_dirs'], config['type_exts'])
