import io
import subprocess
import os

import PyPDF2
from pypdf import PdfReader
from wand.image import Image

# result = subprocess.run(['pdfcpu.exe', 'extract', '-m', 'image', "-unit", "in", 'D:\\Akcje\\test3.pdf', 'D:\\Akcje\\output\\'])


# # Set the minimum DPI that we want
# MIN_DPI = 300
#
# # Get the list of all files in the current directory
# files = os.listdir('D:\\Akcje\\output')
#
# # Iterate over the files
# for file in files:
#     # Check if the file is an image with a JPG, TIF, or PNG extension
#     if file.endswith((".jpg", ".tif", ".png")):
#         # Open the image
#         with Image(filename=f'D:\\Akcje\\output\\{file}') as img:
#             # img.save(filename='output.jpg')
#             # Get the DPI of the image
#             dpi = img.resolution
#             # Check if the DPI is less than the minimum
#             if dpi[0] < MIN_DPI:
#                 # Print a message if the DPI is too low
#                 print(f"Warning: {file} has a DPI of {dpi[0]}, which is below the minimum of {MIN_DPI}.")
#             print(f'{file} {dpi[0]}x{dpi[1]}')

#
# reader = PdfReader("D:\\Akcje\\test.pdf")
#
# page = reader.pages[0]
# count = 0
#
# for image_file_object in page.images:
#     with open(str(count) + image_file_object.name, "wb") as fp:
#         fp.write(image_file_object.data)
#         count += 1

# Open the PDF file in read-binary mode
with open('C:\\Akcje\\test2.pdf', 'rb') as file:
    # Create a PDF object
    pdf = PyPDF2.PdfReader(file)
    page = pdf.pages[0]

    page_start_x = float(page.trimbox[0])
    page_start_y = float(page.trimbox[1])
    page_end_x = float(page.trimbox[2])
    page_end_y = float(page.trimbox[3])
    pdf_width = float((page_end_x - page_start_x))
    pdf_height = float((page_end_y - page_start_y) * 0.352777778)

    print(pdf_width)
    print(pdf_height)

    # Iterate over every page in the PDF
    for page in range(len(pdf.pages)):
        # Extract the images from the page
        images = pdf.pages[page].get_object().get("/Resources").get("/XObject")

        # Iterate over all images in the page
        for image in images:
            # Check if the image is a DPI object
            if images[image].get("/Subtype") == "/Image":
                print(image)
                # Get the image data and size
                image_data = images[image].get_data()
                image_size = (images[image]['/Width'], images[image]['/Height'])
                print(image_size)
                # Check the DPI of the image
                dpi = round(float(images[image]['/DPI']) / 72, 2)
                print(f"Image size: {image_size} pixels, DPI: {dpi}")

                # # You can also use the image data and size to create a Pillow image object
                # im = Image.frombytes("RGB", image_size, image_data)


# with io.open('C:\\Akcje\\card3_składka.pdf', mode="rb") as f:
#     file = PdfReader(f)
#     page = file.pages[0]
#
#     page_start_x = float(page.mediabox[0])
#     page_start_y = float(page.mediabox[1])
#     page_end_x = float(page.mediabox[2])
#     page_end_y = float(page.mediabox[3])
#     pdf_width = float((page_end_x - page_start_x) * 0.352777778)
#     pdf_height = float((page_end_y - page_start_y) * 0.352777778)
#
#     print(pdf_width)
#     print(pdf_height)
#
#     images = file.pages[0].get_object().get("/Resources").get("/XObject")
#
#     # Iterate over all images in the page
#     for image in images:
#         # Check if the image is a DPI object
#         if images[image].get("/Subtype") == "/Image":
#             # Get the image data and size
#             image_data = images[image].getData()
#             print(image_data)
#             image_size = (images[image]['/Width'], images[image]['/Height'])
#             print(image_size)
#             # # Check the DPI of the image
#             # dpi = round(float(images[image]['/DPI']) / 72, 2)
#             # print(f"Image size: {image_size} pixels, DPI: {dpi}")
#             #
#             # # You can also use the image data and size to create a Pillow image object
#             # im = Image.frombytes("RGB", image_size, image_data)
