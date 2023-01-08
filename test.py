# filters output
import argparse
import subprocess
import time
import PyPDF2


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


start_time = time.time()

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('filename', nargs='?')
args = parser.parse_args()

filename = args.filename

pdf = PyPDF2.PdfReader(filename)

wrong_dpi = 0
wrong_colorspace = 0

for page in range(len(pdf.pages)):
    wrong_dpi = 0
    wrong_colorspace = 0

    current_page = page + 1
    command = 'pdfimages.exe'
    arguments = ['-list', '-f', f'{current_page}', '-l', f'{current_page}', f'{filename}', f'.tmp\\{current_page}']

    proc = subprocess.Popen([command] + arguments, stdout=subprocess.PIPE)

    while True:
        line = bytes(proc.stdout.readline())
        if not line:
            break
        # the real code does filtering here
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

if wrong_dpi + wrong_colorspace == 0:
    print('Nie znaleziono problemów.')

end_time = time.time()
elapsed_time = end_time - start_time
print("\nOperacja ukończona w", round(elapsed_time, 2), "s.")
