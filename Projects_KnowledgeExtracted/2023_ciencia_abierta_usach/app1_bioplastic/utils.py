# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 09:42:16 2023

@author: Usuario
"""

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path



from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import LlamaCpp, OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS, Chroma
from langchain.docstore import InMemoryDocstore
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.callbacks import get_openai_callback
import uuid
import sys
import os
import base64
import requests


def list_pdfs(folder_path='.'):
    return [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

def list_txt(folder_path='.'):
    return [f for f in os.listdir(folder_path) if f.endswith('.txt')]

def view_pdf(file_path, width):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # Embedding PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width={str(width)} height={str(width*4/3)} type="application/pdf"></iframe>'
    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)
    
# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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

def create_tmp_sub_folder(pdf_path, folder_name) -> str:
    """
    Creates a temporary sub folder under tmp

    :return:
    """
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    tmp_sub_folder_name = 'tmp\\'+folder_name
    if not os.path.exists(tmp_sub_folder_name):
        os.mkdir(tmp_sub_folder_name)
    return tmp_sub_folder_name


def pdf_to_images(pdf_path):
    folder_name = ''.join(list(pdf_path.split("\\")[-1])[:-4])
    # Create temp files from images
    tmp_path = create_tmp_sub_folder(pdf_path, folder_name)
    # Extraction images from PDF
    pages = convert_from_path(pdf_path)
    for i in range(len(pages)):
        pages[i].save(tmp_path+'\\'+folder_name+'_'+str(i)+'.png')
    return folder_name

def vision_model(folder_name, user_question, api_key, api_org):
    pdf_images_path = 'tmp\\'+folder_name
    images_path = os.listdir(pdf_images_path)
    for image_path in images_path[:4]: ###HARDCODE PAGE SELECTION
        # Getting the base64 string
        base64_image = encode_image('tmp\\'+ folder_name +'\\'+image_path)
        # API JSON OpenAI
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {api_key}"}
        payload = {"model": "gpt-4-vision-preview", ##"gpt-4"
                   "messages": [{"role": "user",
                                 "content": [{"type": "text",
                                              "text": user_question},
                                             {"type": "image_url",
                                              "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                                              }
                                             ]
                                 }
                                ],
                   "max_tokens": 300
                   }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
    return response.json()


def pdf_processing_openAI(pdf_path, api_key, api_org):  ##Conectar historial
    pdf = PyPDFLoader(pdf_path)
    pages = pdf.load_and_split() ### content + metadata
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024,chunk_overlap=64)
    chunks = text_splitter.split_documents(pages) ### chunk content + metadata
    embeddings = OpenAIEmbeddings(openai_api_key=api_key, 
                                  openai_organization=api_org)
    vector_store = FAISS.from_documents(chunks, embedding=embeddings)#, persist_directory="db")    
    
    return vector_store
