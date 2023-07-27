# -*- coding: utf-8 -*-
"""
此Python脚本的目的是读取指定文件夹中的HTML文件，将其中的CSS，图像和字体内嵌到HTML中，并将结果写入一个新的HTML文件。此外，它还会从HTML中删除所有class为"footer-container"的div元素。

使用方法：
1. 确保你的Python环境已经安装了beautifulsoup4和argparse两个库。
2. 通过命令行运行此脚本，并提供要处理的资源文件夹的路径作为参数。例如：
   python combine_html.py /path/to/resource_folder

资源文件夹的结构应如下所示：
resource_folder
│
├── html
│   ├── page1.html
│   ├── page2.html
│   └── ...
│
├── css
│   ├── style1.css
│   ├── style2.css
│   └── ...
│
├── font
│   ├── font1.woff
│   ├── font2.woff2
│   └── ...
│
└── image
    ├── image1.png
    ├── image2.jpg
    └── ...

在这个结构中，"html"文件夹包含所有HTML文件，"css"文件夹包含所有CSS样式文件，"font"文件夹包含所有字体文件，而"image"文件夹包含所有图像文件。这四个子文件夹必须直接位于资源文件夹下。
"""

import os
import base64
import argparse
from bs4 import BeautifulSoup

def read_and_combine_html_files(html_folder):
    html_files = [f for f in os.listdir(html_folder) if f.endswith('.html')]
    combined_html_content = ''
    for file in html_files:
        with open(f"{html_folder}/{file}", 'r', encoding='utf-8') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        for div in soup.find_all("div", {"class": "footer-container"}):
            div.extract()
        combined_html_content += str(soup)
    return combined_html_content

def inline_css(soup, css_folder):
    css_files = [f for f in os.listdir(css_folder) if f.endswith('.css')]
    for file in css_files:
        with open(f"{css_folder}/{file}", 'r', encoding='utf-8') as f:
            css_content = f.read()
            style_tag = soup.new_tag("style")
            style_tag.string = css_content
            soup.head.append(style_tag)
    return soup

def inline_images(soup, img_folder):
    img_files = [f for f in os.listdir(img_folder) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    for img_file in img_files:
        img_file_path = os.path.join(img_folder, img_file)
        with open(img_file_path, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode('utf-8')
        for img in soup.findAll('img'):
            if img_file in img['src']:
                file_extension = os.path.splitext(img_file)[1][1:]
                img['src'] = f"data:image/{file_extension};base64, {encoded_string}"
    return soup

def inline_fonts(soup, font_folder):
    font_files = [f for f in os.listdir(font_folder) if f.endswith(('.woff', '.woff2', '.ttf', '.otf'))]
    for font_file in font_files:
        with open(f"{font_folder}/{font_file}", "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode('utf-8')
            for style in soup.findAll('style'):
                style.string = style.string.replace(font_file, "data:font/woff;base64, " + encoded_string)
    return soup

def main(resource_folder):
    html_folder = f"{resource_folder}/html"
    css_folder = f"{resource_folder}/css"
    font_folder = f"{resource_folder}/font"
    img_folder = f"{resource_folder}/image"

    combined_html_content = read_and_combine_html_files(html_folder)
    soup = BeautifulSoup(combined_html_content, 'html.parser')

    soup = inline_css(soup, css_folder)
    soup = inline_images(soup, img_folder)
    soup = inline_fonts(soup, font_folder)

    with open("combined.html", "w", encoding='utf-8') as f:
        f.write(str(soup))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("resource_folder", help="The path to the resource folder")
    args = parser.parse_args()
    main(args.resource_folder)