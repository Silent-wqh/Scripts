import argparse
import base64
import mimetypes
import os
import re
import pdfkit
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup


def get_date_from_filename(filename):
    match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
    if match is None:
        return None
    date_string = match.group(0)
    return datetime.strptime(date_string, '%Y-%m-%d')

def convert_to_data_url(filepath):
    mime_type, _ = mimetypes.guess_type(filepath)
    with open(filepath, 'rb') as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    return f'data:{mime_type};base64,{encoded_string}'

def process_html_file(html_file, resource_dirs):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    tags = soup.find_all(['link', 'script', 'img'])
    for tag in tags:
        attrs = ['href', 'src']
        for attr in attrs:
            if attr in tag.attrs:
                resource_path = tag[attr]
                if not bool(urlparse(resource_path).netloc):
                    for dir in resource_dirs:
                        abs_path = os.path.join(dir, resource_path)
                        if os.path.exists(abs_path):
                            tag[attr] = convert_to_data_url(abs_path)
                            break

    return str(soup.prettify())

def main():
    parser = argparse.ArgumentParser(description='Merge HTML files.')
    parser.add_argument('dir', type=str, help='The directory containing the HTML files.')
    args = parser.parse_args()
    dir_path = args.dir

    html_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and f.endswith('.html')]
    html_files = [f for f in html_files if get_date_from_filename(f) is not None]
    html_files.sort(key=get_date_from_filename)

    resource_dirs = ['css', 'font', 'image']
    combined_html = ''
    for html_file in html_files:
        combined_html += process_html_file(html_file, resource_dirs)

    combined_html_path = os.path.join(dir_path, 'combined.html')
    with open(combined_html_path, 'w', encoding='utf-8') as f:
        f.write(combined_html)

    # Convert the combined HTML file to a PDF file
    config = pdfkit.configuration(wkhtmltopdf='C:\\ProgramData\\chocolatey\\bin\\wkhtmltopdf.exe')  # use the correct path to your wkhtmltopdf
    pdfkit.from_file(combined_html_path, os.path.join(dir_path, 'combined.pdf'), configuration=config)

if __name__ == '__main__':
    main()