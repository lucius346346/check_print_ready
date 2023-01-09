# filters output
import argparse
import os
import subprocess
import time
import PyPDF2
import re


def convert_to_dict(line):
    # Decode the bytes object to a string
    line = line.decode()
    parts = line.split(':')
    name = parts[0]
    items = parts[1].split()
    d = {'name': name}
    for item in items:
        key, value = item.split('=')
        d[key] = value
    return d


def check_dpi_colorspace(page):

    global wrong_dpi
    global wrong_colorspace

    wrong_dpi = 0
    wrong_colorspace = 0

    current_page = page + 1
    command = 'pdfimages.exe'
    arguments = ['-list', '-f', f'{current_page}', '-l', f'{current_page}', f'{filename}', f'.tmp\\{current_page}']

    proc = subprocess.Popen([command] + arguments, stdout=subprocess.PIPE)
    proc.wait()

    while True:
        line = bytes(proc.stdout.readline())
        if not line:
            break
        # the real code does filter here
        d = convert_to_dict(line)

        resolution_x = round(float(d['vdpi']), 0)
        resolution_y = round(float(d['hdpi']), 0)
        color_space = d['colorspace']

        if resolution_x or resolution_y < 200:
            # print(f'Znaleziono obrazek z DPI mniejszym niż 200: {ResolutionX}x{ResolutionY}')
            wrong_dpi = wrong_dpi + 1

        if color_space == "DeviceRGB":
            wrong_colorspace = wrong_colorspace + 1

    if wrong_dpi > 0:
        print(f'Strona {current_page}: znaleziono obrazy ({wrong_dpi}) mniejsze niż 200 dpi.')

    if wrong_colorspace > 0:
        print(f'Strona {current_page}: znaleziono obrazy ({wrong_colorspace}) w trybie RGB')


def check_objects(page):
    global rgb_fill_number
    global rgb_outline_number

    rgb_fill_number = 0
    rgb_outline_number = 0

    current_page = page + 1

    command = 'pdfcpu.exe'
    arguments = ['extract', '-m', 'content',  '-p', f'{current_page}', f'{filename}', '.tmp']

    proc = subprocess.Popen([command] + arguments, stdout=subprocess.PIPE)
    proc.wait()

    name = os.path.basename(filename)
    name, extension = os.path.splitext(filename)

    # Initialize the count

    # Open the file
    with open(f'.tmp\\{name}_Content_page_{current_page}.txt', 'r') as f:
        # Read the contents of the file into a string
        contents = f.read()

        matches = re.findall(r"\d.*rg", contents)
        rgb_fill_number = rgb_fill_number + len(matches)

        matches = re.findall(r"\d.*RG", contents)
        rgb_outline_number = rgb_outline_number + len(matches)

        print(rgb_fill_number)

    if rgb_fill_number > 0:
        print(f'Strona {current_page}: znaleziono wypełnienia RGB ({rgb_fill_number}).')

    if rgb_outline_number > 0:
        print(f'Strona {current_page}: znaleziono obrysy RGB ({rgb_outline_number}).')


start_time = time.time()

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('filename', nargs='?')
args = parser.parse_args()

filename = args.filename
pdf = PyPDF2.PdfReader(filename)

if not os.path.exists(".tmp"):
    os.makedirs(".tmp")

wrong_dpi = 0
wrong_colorspace = 0
rgb_fill_number = 0
rgb_outline_number = 0

for page in range(len(pdf.pages)):
    check_dpi_colorspace(page)
    check_objects(page)

if wrong_dpi + wrong_colorspace + rgb_fill_number + rgb_outline_number == 0:
    print('Nie znaleziono problemów.')

end_time = time.time()
elapsed_time = end_time - start_time
print("\nOperacja ukończona w", round(elapsed_time, 2), "s.")
