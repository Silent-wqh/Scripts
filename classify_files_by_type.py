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
