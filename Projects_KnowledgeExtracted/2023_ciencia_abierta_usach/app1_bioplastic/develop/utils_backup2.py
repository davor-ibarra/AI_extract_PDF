# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 09:42:16 2023

@author: Usuario
"""

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import LlamaCpp
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import FAISS
import uuid
import sys
import os
import base64





def list_pdfs(folder_path='.'):
    return [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

def view_pdf(file_path, width):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width={str(width)} height={str(width*4/3)} type="application/pdf"></iframe>'
    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

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

def create_tmp_sub_folder() -> str:
    """
    Creates a temporary sub folder under tmp

    :return:
    """
    if not os.path.exists("tmp"):
        os.mkdir("tmp")
    tmp_sub_folder_name = str(uuid.uuid4())[:8]
    tmp_sub_folder_path = os.path.join("tmp", tmp_sub_folder_name)
    return tmp_sub_folder_path

def pdf_processing(pdf_path):
    pdf = PdfReader(pdf_path)
    text = ''
    for page in pdf.pages:
        text += page.extract_text()
    
    text_splitter = CharacterTextSplitter(
        separator='\n',
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len)
    chunks = text_splitter.split_text(text)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cpu'})
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    # Create the chain object
    #chain = create_conversational_chain(vector_store)
    
    return vector_store

def create_conversational_chain(vector_store):
    # Create llm
    llm = LlamaCpp(
    streaming = True,
    model_path="mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    temperature=0.75,
    top_p=1, 
    verbose=True,
    n_ctx=4096
)
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    chain = ConversationalRetrievalChain.from_llm(llm=llm, chain_type='stuff',
                                                 retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
                                                 memory=memory)
    return chain



