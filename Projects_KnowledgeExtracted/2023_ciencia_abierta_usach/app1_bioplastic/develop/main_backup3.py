# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:00:00 2023

@author: Davor Ibarra-Pérez
"""

import streamlit as st
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu
from streamlit_javascript import st_javascript

from langchain.agents.openai_assistant import OpenAIAssistantRunnable

from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.base import _get_chat_history
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.callbacks import get_openai_callback
#from openai.error import OpenAIError
from datetime import datetime
from pathlib import Path
import os
import io
import json

from utils import (list_pdfs,
                   list_txt,
                   view_pdf, 
                   compress_file, 
                   pdf_processing_huggingFace,
                   pdf_processing_openAI,
                   config_assistant,
                   agent_smith,
                   create_conversational_chain
                   )


st.set_page_config(page_title="Supervised_PaperExtraction", 
                   page_icon="📖", 
                   initial_sidebar_state="expanded", 
                   layout="wide")


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
    
    os.environ['OPENAI_API_KEY'] = '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'
    ## Panel lateral
    #st.sidebar.title("Navegación")
    app_page = option_menu(menu_title=None, 
                           options=["Home","Chatbot processing", "Contact"], 
                           icons=['house','book','envelope'], 
                           menu_icon='cast', 
                           default_index=0, 
                           orientation='horizontal')
    
    ### Página
    if app_page == "Home":
        st.title("Bienvenido a [Nombre de la App]")
        st.write("""
        Esta aplicación te permite interactuar con modelos de lenguaje como GPT-4 para generar resúmenes
        y recopilar información relevante de archivos PDF.
        """)
        
    elif app_page == "Chatbot processing":
        chatbot_interface()

    elif app_page == "Contact":
        contact_interface()

def chatbot_interface():
    st.title("Assisted PDF extraction")
    
    # Inicializa el JSON en el estado de la sesión si no existe
    if 'json_data' not in st.session_state:
        st.session_state['json_data'] = {}
        
    if 'label_name' not in st.session_state:
        st.session_state['label_name'] = {}
        
    if 'label_content' not in st.session_state:
        st.session_state['label_content'] = {}
    
    compl_prompt = None
    
    # Config model
    with st.sidebar:
        st.sidebar.subheader("Configuraciones del Modelo")
        type_model = st.radio("Tipo de modelo?", ("OpenAI","HuggingFace"),)

        if type_model == 'OpenAI':
            model_name = st.selectbox('Selecciona el modelo OpenAI',['gpt-4', 'gpt-3.5-turbo'])
            api_key = st.text_input("Ingresa tu clave API para modelos OpenAI:")
            st.markdown("""---""")
            st.sidebar.subheader("Tuning-parameters")
            temperature = st.slider("Temperatura:", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
            max_tokens = st.slider("Máximo de tokens:", min_value=20, max_value=2000, value=1000)
            top_p = st.slider("Top-p:", min_value=0.0, max_value=1.0, value=0.9, step=0.1)
            
        if type_model == "HuggingFace":
            model_name = st.selectbox('Selecciona el modelo HuggingFace',['Mistral', 'Falcon'])
            api_key = st.text_input("Ingresa tu clave API para modelos HuggingFace:")
            st.markdown("""---""")
            st.sidebar.subheader("Tuning-parameters")
            temperature = st.slider("Temperatura:", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
            max_tokens = st.slider("Máximo de tokens:", min_value=20, max_value=2000, value=1000)
            top_p = st.slider("Top-p:", min_value=0.0, max_value=1.0, value=0.9, step=0.1)
            
    # INPUT   
    ## File management
    with st.container():
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
    
    # PROCESSING
    ## Assisted PDF Extraction
    
    with st.container():
        agent_path = 'agents'
        st.markdown("""---""")
        col111, col222 = st.columns([1,1])
        with col111:
            if st.checkbox('Ver PDF'):
                ui_width = st_javascript("window.innerWidth")
                view_pdf(pdf_path, ui_width)
        with col222:
            if st.checkbox('Extracción asistida 💬'):
                if type_model == 'HuggingFace':
                    vector_store = pdf_processing_huggingFace(pdf_path)
                else:
                    vector_store = pdf_processing_openAI(pdf_path)
                    
                tab1, tab2 = st.tabs(['Crear Agente', 'Agente Smith'])
                ## TAB 1: Config Workflow
                with tab1:
                    st.subheader("Configura tu asistente virtual")
                    name_agent = st.text_input('Nombre del agente')
                    compl_prompt = st.text_area('Indica instrucciones detalladas')
                    if st.button('Guardar agente'):
                        txt_path = os.path.join(agent_path, name_agent+'.txt')
                        with open(txt_path, 'x') as f:
                            f.write(compl_prompt)
                
                ## TAB 2: Workflow
                with tab2:
                    agents_list = list_txt(agent_path)
                    assistant_list = st.multiselect('Activa los agentes',options=agents_list)
                    st.markdown("""Agentes activados: """+ str(len(assistant_list)))
                    st.markdown("""---""")
                    #memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                    #agent = agent_smith(compl_prompt, model_name, vector_store, memory)
                    user_question = st.text_input('En que puedo ayudarte hoy?')
                    #st.chat_input()
                    if user_question:
                        # open(txt_path, 'x') as f:
                        #    agent_instructions = f.read()
                        output = config_assistant(user_question, compl_prompt, vector_store)
                        
                        st.write(output)
                        
                        #search_info = vector_store.similarity_search(user_question)
                        #response = create_conversational_chain(vector_store = vector_store, 
                        #                                       prompt = user_question, 
                        #                                       compl_prompt = None)
                        #st.write(response)
    # OUTPUT
    ## Create JSON file
    with st.container():
        st.markdown("""---""")
        ### Output name
        file_name = st.text_input("Nombre del archivo:")
        col1, col2 = st.columns([2,1])
        
        ### Labels and content
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
        ### Buttons
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
        
        
                    
        

def contact_interface():
    st.title("Contacto")
    
    




if __name__ == "__main__":
    main()
