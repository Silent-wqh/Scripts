'''
图片拼接脚本

这个 Python 脚本用于将指定文件夹中的多张图片进行拼接。图片可以横向或纵向进行拼接。该脚本支持不同大小的图片，它们会在保持原始宽高比的情况下被调整大小。结果图片的高度（用于横向拼接）或宽度（用于纵向拼接）将等于原始图片中最大的高度或宽度。尺寸较小的图片将被放大以匹配最大的高度或宽度。

该脚本支持常见的图片格式，如 PNG，JPEG，JFIF，BMP，PPM 和 TIFF。

使用方法：
$ python3 image_concatenation.py [image_folder] [direction]

参数：
- image_folder： 包含需要拼接的图片的文件夹的路径。
- direction： 拼接的方向。可以是 'horizontal'（横向）或 'vertical'（纵向）。

拼接后的图片将以 'output.png' 的形式保存在原始图片的文件夹中。

需求：
- Python 3
- PIL 库
'''

import os
import sys
from PIL import Image

def concatenate_images(image_folder, direction='horizontal', output_name='output.png'):
    # Read all images in the folder
    image_files = os.listdir(image_folder)
    images = [Image.open(os.path.join(image_folder, image_file)) for image_file in image_files if image_file.endswith(('png', 'jpg', 'jpeg', 'jfif', 'bmp', 'ppm', 'tiff'))]
    
    # Initialize max_height and max_width
    max_height = 0
    max_width = 0
    
    # Resize images while maintaining aspect ratio
    if direction == 'horizontal':
        max_height = max(image.height for image in images)
        images = [image.resize((int(image.width * max_height / image.height), max_height)) for image in images]
    else:  # vertical
        max_width = max(image.width for image in images)
        images = [image.resize((max_width, int(image.height * max_width / image.width))) for image in images]
    
    # Concatenate images
    total_width = sum(image.width for image in images)
    total_height = sum(image.height for image in images)
    if direction == 'horizontal':
        new_image = Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for image in images:
            new_image.paste(image, (x_offset, 0))
            x_offset += image.width
    else:  # vertical
        new_image = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for image in images:
            new_image.paste(image, (0, y_offset))
            y_offset += image.height
    
    # Save the image
    output = os.path.join(image_folder, output_name)
    new_image.save(output)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 image_concatenation.py [image_folder] [direction]")
        sys.exit(1)

    image_folder = sys.argv[1]
    direction = sys.argv[2]
    if direction not in ['horizontal', 'vertical']:
        print("Direction must be either 'horizontal' or 'vertical'")
        sys.exit(1)

    concatenate_images(image_folder, direction)