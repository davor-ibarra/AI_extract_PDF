# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:00:00 2023

@author: Davor Ibarra-Pérez
"""

import streamlit as st
import streamlit.components.v1 as components
from streamlit_chat import message
from streamlit_javascript import st_javascript
from openai.error import OpenAIError
import os
import io
import json

from utils import (list_pdfs, 
                   view_pdf2, 
                   #text_split,
                   #parse_pdf,
                   #get_embeddings,
                   #get_sources,
                   #get_answer,
                   #get_condensed_question
                   )


st.set_page_config(page_title="PaperExtraction", page_icon="📖", layout="wide")

# Inicialización de la variable global para almacenar información
metadata_dict = {}

# Funciones

def clear_submit():
    st.session_state["submit"] = False

# Streamlit app

def main():
    
    ## Panel lateral
    st.sidebar.title("Navegación")
    app_mode = st.sidebar.selectbox("Elige la página de la aplicación:",
                                    ["Home", "PDF Chatbot", "Output"])
    
    ### Página
    if app_mode == "Home":
        st.title("Bienvenido a [Nombre de la App]")
        st.write("""
        Esta aplicación te permite interactuar con modelos de lenguaje como GPT-4 para generar resúmenes
        y recopilar información relevante de archivos PDF.
        """)

    elif app_mode == "PDF Chatbot":
        chatbot_interface()

    elif app_mode == "Output":
        json_output_interface()

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
    
    # Menú desplegable para las etiquetas
    folder_path = 'pdf_folder'
    # Carpeta donde se encuentran los PDFs
    pdf_files = list_pdfs(folder_path)
    selected_pdf = st.selectbox('Elige un archivo PDF:', pdf_files)
    pdf_path = os.path.join(folder_path, selected_pdf)
    
    col1, col2 = st.columns(spec=[2, 1], gap="small")
    
    with col1:
        ui_width = st_javascript("window.innerWidth")
        #view_pdf(pdf_path, ui_width -10)
        view_pdf2(pdf_path)
    
    
#    tab1, tab2 = st.tabs(["PDF", "Chatbot"])

    #with tab1:
    #    # Menú desplegable para las etiquetas
    #    folder_path = 'pdf_folder'  
    #    # Carpeta donde se encuentran los PDFs
    #    pdf_files = list_pdfs(folder_path)
    #    selected_pdf = st.selectbox('Elige un archivo PDF:', pdf_files)
    #    pdf_path = os.path.join(folder_path, selected_pdf)
    #
    #    check_view_pdf = st.checkbox("Ver PDF")
    #    if check_view_pdf:
    #        view_pdf(pdf_path)
        
#    with tab2:
#        # Campo de texto para el prompt
#        user_input = st.text_input("Escribe tu prompt aquí:")
#   
#        # Checkbox para el modo de descubrimiento de espacios latentes
#        discovery_mode = st.checkbox("Activar modo de descubrimiento de espacios latentes")
#    
#        # Menú desplegable para las etiquetas
#        label = st.selectbox("Elige una etiqueta:", ["Título", "Autor", "Año", "Doi", "Abstract", "Introducción", "Método y Metodología", "Resultados", "Conclusión", "Referencias", "Información Relevante Extraída", "Información Relevante Discutida"])
#    
#        # Campo para copiar contenido relevante
#        copied_content = st.text_area("Copia aquí el contenido relevante:")
#    
#        # Botón para guardar la información
#        if st.button("Guardar información"):
#            metadata_dict[label] = copied_content
#            st.success(f"Información guardada bajo la etiqueta {label}")


def json_output_interface():
    st.title("Output en Formato JSON")

    # Sección para revisar y validar campos
    for label, content in metadata_dict.items():
        st.subheader(label)
        updated_content = st.text_area("Editar contenido:", content)
        metadata_dict[label] = updated_content

    # Campo para añadir contenido específico adicional
    additional_content = st.text_area("Añadir contenido específico adicional al JSON:")

    # Botón para guardar el archivo JSON completo
    if st.button("Guardar archivo JSON"):
        if additional_content:
            metadata_dict["Contenido Adicional"] = additional_content
        
        with open("output.json", "w") as f:
            json.dump(metadata_dict, f)
        st.success("Archivo JSON guardado con éxito.")




if __name__ == "__main__":
    main()
