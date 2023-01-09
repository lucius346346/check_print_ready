# filters output
import argparse
import os
import shutil
import subprocess
import time
import PyPDF2
import re

# TODO rozdzielić sprawdzanie DPI i trybu kolor, dodać osobną funkcję do ekstrakcji PDF

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

def check_bitmaps():

    for page in range(len(pdf.pages)):

        wrong_dpi = False
        wrong_colorspace = False
        global wrong_dpi_pages
        global wrong_colorspace_pages

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

            if (resolution_x or resolution_y < 200) and wrong_dpi is False:
                # print(f'Znaleziono obrazek z DPI mniejszym niż 200: {ResolutionX}x{ResolutionY}')
                # wrong_dpi_pages = wrong_dpi_pages + 1
                if wrong_dpi_pages:
                    wrong_dpi_pages += ', '
                wrong_dpi_pages += f'{current_page}'
                wrong_dpi = True

            if color_space in ("DeviceRGB", "ICCBased", "DeviceGray") and wrong_colorspace is False:
                # wrong_colorspace_pages = wrong_colorspace_pages + 1
                if wrong_colorspace_pages:
                    wrong_colorspace_pages += ', '
                wrong_colorspace_pages += f'{current_page}'
                wrong_colorspace = True

            if wrong_dpi and wrong_colorspace is True:
                break

        # if wrong_dpi_pages > 0:
        #     print(f'Strona {current_page}: znaleziono obrazy ({wrong_dpi_pages}) mniejsze niż 200 dpi.')
        #
        # if wrong_colorspace_pages > 0:
        #     print(f'Strona {current_page}: znaleziono obrazy ({wrong_colorspace_pages}) w trybie RGB')


def check_objects():
    for page in range(len(pdf.pages)):
        global rgb_fill_pages
        global rgb_outline_pages

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

            matches = re.search(r"\d.* rg|\d.* scn", contents)
            if matches is not None:
                if rgb_fill_pages:
                    rgb_fill_pages += ', '
                rgb_fill_pages += f'{current_page}'

            matches = re.search(r"\d.* RG|\d.* SCN", contents)
            if matches is not None:
                if rgb_outline_pages:
                    rgb_outline_pages += ', '
                rgb_outline_pages += f'{current_page}'


        # if rgb_fill_pages > 0:
        #     print(f'Strona {current_page}: znaleziono wypełnienia RGB ({rgb_fill_pages}).')
        #
        # if rgb_outline_pages > 0:
        #     print(f'Strona {current_page}: znaleziono obrysy RGB ({rgb_outline_pages}).')


start_time = time.time()

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('filename', nargs='?')
args = parser.parse_args()

filename = args.filename
pdf = PyPDF2.PdfReader(filename)

if not os.path.exists(".tmp"):
    os.makedirs(".tmp")

wrong_dpi_pages = ""
wrong_colorspace_pages = ""
rgb_fill_pages = ""
rgb_outline_pages = ""

# check_dpi_colorspace(page)
check_objects()
check_bitmaps()

with open("result.log", "w") as f:
    if rgb_fill_pages:
        log = f'Ostrzeżenie: strona zawiera wypełnienia inne niż CMYK: {rgb_fill_pages}'
        print(log)
        f.write(f'{log}\n')
    if rgb_outline_pages:
        log = f'Ostrzeżenie: strona zawiera kontury inne niż CMYK: {rgb_outline_pages}'
        print(log)
        f.write(f'{log}\n')
    if wrong_dpi_pages:
        print(f'Błąd: strona zawiera bitmapy o rozdzielczości mniejszej niż 200 dpi: {wrong_dpi_pages}')
        print(log)
        f.write(f'{log}\n')
    if wrong_colorspace_pages:
        log = f'Ostrzeżenie: strona zawiera bitmapy w trybie innym niż CMYK: {wrong_colorspace_pages}'
        print(log)
        f.writelines(f'{log}\n')

    if all(not s for s in (rgb_fill_pages, rgb_outline_pages, wrong_dpi_pages, wrong_colorspace_pages)):
        log = 'Nie znaleziono problemów.'
        print(log)
        f.write(f'{log}\n')

f.close()

shutil.rmtree('.tmp', ignore_errors=False, onerror=None)

# if wrong_dpi + wrong_colorspace + rgb_fill_pages + rgb_outline_pages == 0:
#     print('Nie znaleziono problemów.')

end_time = time.time()
elapsed_time = end_time - start_time
print("\nOperacja ukończona w", round(elapsed_time, 2), "s.")
