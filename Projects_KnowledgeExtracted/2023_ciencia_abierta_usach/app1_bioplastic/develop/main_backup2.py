# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:00:00 2023

@author: Davor Ibarra-Pérez
"""

import streamlit as st
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript
from langchain.llms import LlamaCpp, OpenAI
from langchain.chains.question_answering import load_qa_chain
from tempfile import NamedTemporaryFile
#from openai.error import OpenAIError
from datetime import datetime
from pathlib import Path
import os
import io
import json

from utils import list_pdfs, view_pdf, compress_file, pdf_processing


st.set_page_config(page_title="Supervised_PaperExtraction", page_icon="📖", layout="wide")


# Funciones

def clear_field():
    st.session_state['json_data'] = False
    st.session_state['label_name'] = False
    st.session_state['label_content'] = False
    
# Función para agregar un nuevo ítem al JSON
def add_item(label_name, label_content):
    if label_name and label_content:
        st.session_state.json_data[label_name] = label_content
        st.success('Ítem agregado con éxito')
    else:
        st.error('Por favor, complete el nombre y contenido de la etiqueta')

# Función para limpiar el JSON
def clear_json():
    st.session_state.json_data = {}
    st.success('JSON limpiado con éxito')

# Función para guardar el JSON en un archivo
def save_json():
    with open('data.json', 'w') as outfile:
        json.dump(st.session_state.json_data, outfile)
    st.success('JSON guardado con éxito en data.json')

# Streamlit app

def main():
    
    ## Panel lateral
    st.sidebar.title("Navegación")
    app_mode = st.sidebar.selectbox("Elige la página de la aplicación:",
                                    ["Home", "Input", "Chatbot processing", "Output"])
    
    ### Página
    if app_mode == "Home":
        st.title("Bienvenido a [Nombre de la App]")
        st.write("""
        Esta aplicación te permite interactuar con modelos de lenguaje como GPT-4 para generar resúmenes
        y recopilar información relevante de archivos PDF.
        """)
        
    elif app_mode == "Input":
        json_input_interface()
        
    elif app_mode == "Chatbot processing":
        chatbot_interface()

    elif app_mode == "Output":
        json_output_interface()

def json_input_interface():
    st.title("Input en Formato JSON")
    
    # Inicializa el JSON en el estado de la sesión si no existe
    if 'json_data' not in st.session_state:
        st.session_state['json_data'] = {}
        
    if 'label_name' not in st.session_state:
        st.session_state['label_name'] = {}
        
    if 'label_content' not in st.session_state:
        st.session_state['label_content'] = {}
    
    tab1, tab2 = st.tabs(['Contenido Específico', 'Extracción PDF asistida'])
    
    ## TAB 1
    with tab1:
        st.header("Contenido Específico")
        file_name = st.text_input("Nombre del archivo:")
        col1, col2 = st.columns([2,1])
        with col1:
            # Campo para etiqueta comun
            st.session_state.label_name = st.selectbox("Selecciona etiqueta", ["type", 
                                                                               "title", 
                                                                               "author", 
                                                                               "year", 
                                                                               "doi", 
                                                                               "abstract",
                                                                               "introduction", 
                                                                               "material_and_methods", 
                                                                               "result_and_discussion", 
                                                                               "conclusion", 
                                                                               "references", 
                                                                               "other"], key='label_name_a')
            if st.session_state.label_name == "other":
                # Campo para la etiqueta del contenido específico
                st.session_state.label_name = st.text_input("Nombre de la etiqueta:", key='other_a')
                # Campo para añadir contenido específico adicional
                st.session_state.label_content = st.text_area("Añadir contenido:", key='content_a')
            else:
                # Campo para añadir contenido específico adicional
                st.session_state.label_content = st.text_area("Añadir contenido:", key='content_a')
        with col2:
            # type content
            if st.session_state.label_name == "type":
                st.session_state.label_content = st.selectbox("Selecciona tipo de documento científico", ["article", 
                                                                                                          "book", 
                                                                                                          "thesis", 
                                                                                                          "other"],key='type_a')
        
        col11, col22, col33, col44 = st.columns([1.5,1,1.5,1])
        with col11:
            # add item
            if st.button("Guardar Item", key='save_item_a'):
                add_item(st.session_state.label_name, st.session_state.label_content)
        with col22:
            if st.button("Limpiar JSON", key='clean_json_a'):
                clear_json()
        with col33:
            # Botón para guardar el archivo JSON completo
            if st.button("Guardar archivo JSON", key='save_json_a'):
                with open(str(file_name)+'.json', 'w') as outfile:
                    json.dump(st.session_state.json_data, outfile)
                st.success("Archivo JSON guardado con éxito.")
        with col44:
            # add view checkbox
            view_json = st.checkbox("Ver JSON", key='see_a')
        
        if view_json:
            with open(str(file_name)+'.json') as f:
                data = json.load(f)
                st.json(data)
        
        clear_field()
        
        ## TAB 2
        with tab2:
            folder_path = 'pdf_folder'
            uploader_file = st.checkbox('Cargar Archivo')
            if uploader_file:
                # Upload a PDF file
                pdf = st.file_uploader("Upload your PDF", type='pdf')
                pdf_path = os.path.join(folder_path, pdf.name)
                if pdf is not None:
                    with open(pdf_path, 'wb') as f:
                            f.write(pdf.read())
                    compress_file(pdf_path)
                
            selection_file = st.checkbox('Seleccionar Archivo')
            if selection_file:
                pdf_files = list_pdfs(folder_path)
                selected_pdf = st.selectbox('Elige un archivo PDF:', pdf_files)
                pdf_path = os.path.join(folder_path, selected_pdf)
                
                
                col111, col222 = st.columns([1,1])
                with col111:
                    if st.checkbox('Ver PDF'):
                        ui_width = st_javascript("window.innerWidth")
                        view_pdf(pdf_path, ui_width -10)
                with col222:
                    #with st.expander('ChatbotPDF:'):
                    vector_store = pdf_processing(pdf_path)
                    user_question = st.text_input('En que puedo ayudarte hoy?', key='user_question_b')
                    #st.chat_input()
                    if user_question:
                        search_info = vector_store.similarity_search(user_question)
                        
                        chain = load_qa_chain(OpenAI(openai_api_key="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", 
                                                     openai_organization="org-tRRrVBRW1HaBMqOfzDv9xnFn"), 
                                              chain_type='stuff')
                        response = chain.run(input_documents=search_info, question=user_question)
                        st.write(response)
                    
                    
                col1, col2 = st.columns([2,1])
                with col1:
                    # Campo para etiqueta comun
                    st.session_state.label_name = st.selectbox("Selecciona etiqueta", ["type", 
                                                                                       "title", 
                                                                                       "author", 
                                                                                       "year", 
                                                                                       "doi", 
                                                                                       "abstract",
                                                                                       "introduction", 
                                                                                       "material_and_methods", 
                                                                                       "result_and_discussion", 
                                                                                       "conclusion", 
                                                                                       "references", 
                                                                                       "other"], key='label_name_b')
                    if st.session_state.label_name == "other":
                        # Campo para la etiqueta del contenido específico
                        st.session_state.label_name = st.text_input("Nombre de la etiqueta:", key='other_a')
                        # Campo para añadir contenido específico adicional
                        st.session_state.label_content = st.text_area("Añadir contenido:", key='content_b')
                    else:
                        # Campo para añadir contenido específico adicional
                        st.session_state.label_content = st.text_area("Añadir contenido:", key='content_b')
                with col2:
                    # type content
                    if st.session_state.label_name == "type":
                        st.session_state.label_content = st.selectbox("Selecciona tipo de documento científico", ["article", 
                                                                                                                  "book", 
                                                                                                                  "thesis", 
                                                                                                                  "other"],
                                                                                                                 key='type_b')
                
                col11, col22, col33, col44 = st.columns([1.5,1,1.5,1])
                with col11:
                    # add item
                    if st.button("Guardar Item", key='save_item_b'):
                        add_item(st.session_state.label_name, st.session_state.label_content)
                with col22:
                    if st.button("Limpiar JSON", key='clean_json_b'):
                        clear_json()
                with col33:
                    # Botón para guardar el archivo JSON completo
                    if st.button("Guardar archivo JSON", key='save_json_b'):
                        with open(str(selected_pdf.split('.')[0])+'.json', 'w') as outfile:
                            json.dump(st.session_state.json_data, outfile)
                        st.success("Archivo JSON guardado con éxito.")
                with col44:
                    # add view checkbox
                    view_json = st.checkbox("Ver JSON", key='see_b')
                
                if view_json:
                    with open(str(selected_pdf.split('.')[0])+'.json') as f:
                        data = json.load(f)
                        st.json(data)
        
def chatbot_interface():
    # Initial conditions
    if "generated" not in st.session_state:
        st.session_state["generated"] = []

    if "past" not in st.session_state:
        st.session_state["past"] = []
    
    
    ## Panel lateral
    ### Configuraciones del modelo
    with st.sidebar:
        st.sidebar.subheader("Configuraciones del Modelo")
    
        model_name = st.radio("Select the model", ("Llama 2",
                                                   "Falcon",
                                                   "gpt-3.5-turbo", 
                                                   "gpt-4"))

        if model_name == "gpt-3.5-turbo" or "gpt-4":
            api_key = st.text_input("Ingresa tu clave API para modelos OpenAI:")

        temperature = st.slider("Temperatura:", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        max_tokens = st.slider("Máximo de tokens:", min_value=20, max_value=2000, value=1000)
        top_p = st.slider("Top-p:", min_value=0.0, max_value=1.0, value=0.9, step=0.1)
    
    ## Página
    st.title("PDF Chatbot")
    
    
    
    col1, col2 = st.columns(spec=[2, 1], gap="small")
    
    #with col1:
    return

def json_output_interface():
    st.title("Output en Formato JSON")
    
    




if __name__ == "__main__":
    main()
