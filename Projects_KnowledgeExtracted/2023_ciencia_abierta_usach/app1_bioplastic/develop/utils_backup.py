# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 09:42:16 2023

@author: Usuario
"""

import streamlit as st
import numpy as np
from PyPDF2 import PdfReader, PdfWriter
from PDFNetPython3.PDFNetPython import PDFDoc, Optimizer, SDFDoc, PDFNet
from PIL import Image
from pdf2jpg import pdf2jpg
import shutil
import uuid
import sys
import os
import base64




def list_pdfs(folder_path='.'):
    return [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

def view_pdf(file_path, width):
    file = compress_file(file_path)
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width={str(width)} height={str(width*4/3)} type="application/pdf"></iframe>'
    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)
    
def crop_white_space(arr: np.array):
    FOOTER_ROWS = 300
    WHITE_VALUE = 255
    white_pixels = (arr == WHITE_VALUE)
    white_rows = list(np.all(white_pixels, axis=(1, 2)))
    last_non_white_row_idx = max(loc for loc, val in enumerate(white_rows) if not val)
    merged_arr = arr[:last_non_white_row_idx + FOOTER_ROWS]
    return merged_arr

def create_tmp_sub_folder() -> str:
    """
    Creates a temporary sub folder under tmp

    :return:
    """
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    tmp_sub_folder_name = str(uuid.uuid4())[:8]
    tmp_sub_folder_path = os.path.join("tmp", tmp_sub_folder_name)
    os.mkdir(tmp_sub_folder_path)
    return tmp_sub_folder_path

def try_remove(path: str) -> None:
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass

def view_pdf2(file_path):
    # Create temporary folder for generated image
    tmp_sub_folder_path = create_tmp_sub_folder()

    # Save images in that sub-folder
    result = pdf2jpg.convert_pdf2jpg(file_path, tmp_sub_folder_path, pages="ALL")
    images = []
    for image_path in result[0]["output_jpgfiles"]:
        images.append(np.array(Image.open(image_path)))

    # Create merged image from all images + remove irrelevant whitespace
    merged_arr = np.concatenate(images)
    merged_arr = crop_white_space(merged_arr)
    merged_path = os.path.join(tmp_sub_folder_path, "merged.jpeg")
    Image.fromarray(merged_arr).save(merged_path)

    # Display the image
    st.image(merged_path)
    try_remove(tmp_sub_folder_path)

def compress_file(input_file: str):
    """Compress PDF file"""
    try:
        reader = PdfReader(input_file)
        writer = PdfWriter()
        for i in list(range(len(reader.pages))):
            page = reader.pages[i]
            writer.add_page(page);
        for i in list(range(len(reader.pages))):
            page.compress_content_streams()
        with open(input_file, "wb") as f:
            st.text("Finished!")
            writer.write(f)
    except Exception as e:
        st.text("Error compress_file="+ str(e))
        return False
    return True









