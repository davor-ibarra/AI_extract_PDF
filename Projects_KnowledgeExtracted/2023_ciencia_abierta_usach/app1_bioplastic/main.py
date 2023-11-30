# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:00:00 2023

@author: Davor Ibarra-Pérez
"""

import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_javascript import st_javascript
#from openai.error import OpenAIError
import os
import json

from utils import (list_pdfs,
                   list_txt,
                   view_pdf, 
                   compress_file,
                   pdf_to_images,
                   vision_model
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
    st.session_state['json_data'] = {}
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
def save_json(file_name):
    with open("output/"+str(file_name)+'.json', 'w') as outfile:
        json.dump(st.session_state.json_data, outfile)
    st.success('Archivo JSON guardado con éxito.')

# Streamlit app

def main():
    
    #os.environ['OPENAI_API_KEY'] = 'You API KEY' ## Save API KEY in ".env" file
    ## Page
    app_page = option_menu(menu_title=None, 
                           options=["Home","Chatbot processing", "Contact"], 
                           icons=['house','book','envelope'], 
                           menu_icon='cast', 
                           default_index=0, 
                           orientation='horizontal')
    
    ### Página
    if app_page == "Home":
        st.title("Bienvenido a IA_extract_PDF")
        intro_text = """
        Esta aplicación permite el desarrollo de un flujo de trabajo mediante 
        interacción con modelos de Lenguaje de Memoria Larga (LLM) como GPT-4 de OpenAI 
        y los modelos de acceso abierto de HuggingFace, para 
        generar resúmenes y recopilar información relevante desde artículos
        científicos que se encuentren en formato PDF. \n 
        
        - En la primera sección podrás subir tus archivos PDF, previo a su almacenamiento
        en la carpeta correspondiente esta opción cuenta con una función que comprime el PDF.
        Evitando de esta forma, errores por tamaño (Puedes evitar este paso subiendo los archivos previamente 
                                     en la carpeta correspondiente). \n
        
        - Luego, se recomienda iterar y lograr un set de instrucciones para guiar al asistente
        hacia respuestas específicas del contenido que se requiere registrar. \n
        
        - Una vez que haya configurado su asistente,vaya registrando el contenido en la
        sección inferior, donde podrá crear sus propias etiquetas seleccionando la
        opción de "other", tambien puedes utilizar las etiquetas propuestas en la lista desplegada.
        Finalmente, podras exportar tu archivo JSON personalizado con la sistematización del conocimiento que te hayas propuesto.
        """
        
        col1, col2, col3 = st.columns([1,6,1])

        with col1:
            st.write("")
        
        with col2:
            st.write(intro_text)
            st.image("resources/structure_app.png",width=800)
        
        with col3:
            st.write("")
            
        st.write("""
        \n
        APP EN DESARROLLO \n
        POR HACER:\n
            - Utilizar variables de estado para mejorar velocidad.\n
            - Conectar Modelos de HuggingFace.\n
            - Conectar tunning parameters.\n
            - Implementar más de un agente.\n
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
            api_key = st.text_input("Ingresa tu clave API-KEY para modelos OpenAI:")
            api_org = st.text_input("Ingresa tu clave API-ORG para modelos OpenAI:")
            st.markdown("""---""")
            st.sidebar.subheader("Tuning-parameters")
            temperature = st.slider("Temperatura:", min_value=0.0, max_value=1.0, value=0.5, step=0.1) # EN DESARROLLO
            max_tokens = st.slider("Máximo de tokens:", min_value=20, max_value=2000, value=1000) # EN DESARROLLO
            top_p = st.slider("Top-p:", min_value=0.0, max_value=1.0, value=0.9, step=0.1) # EN DESARROLLO
            
        if type_model == "HuggingFace": # EN DESARROLLO
            model_name = st.selectbox('Selecciona el modelo HuggingFace',['Mistral', 'Falcon'])
            api_key = st.text_input("Ingresa tu clave API para modelos HuggingFace:")
            st.markdown("""---""")
            st.sidebar.subheader("Tuning-parameters")
            temperature = st.slider("Temperatura:", min_value=0.0, max_value=1.0, value=0.5, step=0.1) # EN DESARROLLO
            max_tokens = st.slider("Máximo de tokens:", min_value=20, max_value=2000, value=1000) # EN DESARROLLO
            top_p = st.slider("Top-p:", min_value=0.0, max_value=1.0, value=0.9, step=0.1) # EN DESARROLLO
            
    # INPUT   
    ## File management
    with st.container():
        st.write('INPUT')
        folder_path = 'pdf_folder'
        uploader_file = st.checkbox('Cargar Archivo')
        if uploader_file:
            # Upload a PDF file
            pdf = st.file_uploader("Upload your PDF", type='pdf')
            if pdf is not None:
                pdf_path = os.path.join(folder_path, pdf.name)
                with open(pdf_path, 'wb') as f:
                        f.write(pdf.read())
                compress_file(pdf_path)
            
        selection_file = st.checkbox('Seleccionar Archivo')
        if selection_file:
            pdf_files = list_pdfs(folder_path)
            selected_pdf = st.selectbox('Elige un archivo PDF:', pdf_files)
            pdf_path = os.path.join(folder_path, selected_pdf)
            pdf_images_name = pdf_to_images(pdf_path)
            
    
    # PROCESSING
    ## Assisted PDF Extraction
    
    with st.container():
        agent_path = 'agents'
        st.markdown("""---""")
        st.write('PROCESSING')
        col111, col222 = st.columns([1,1])
        with col111:
            if st.checkbox('Ver PDF'):
                ui_width = st_javascript("window.innerWidth")
                view_pdf(pdf_path, ui_width)
        with col222:
            if st.checkbox('Extracción asistida 💬'):
                    
                tab1, tab2 = st.tabs(['Crear Agente', 'Agente Smith'])
                ## TAB 1: Config Workflow
                with tab1:
                    st.subheader("Configura tu asistente virtual")
                    name_agent = st.text_input('Nombre del agente')
                    compl_prompt = st.text_area('Indica instrucciones detalladas') ## EN DESARROLLO
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
                    
                    user_question = st.text_input('En que puedo ayudarte hoy?')
                    if user_question:
                        output = vision_model(pdf_images_name, user_question, api_key, api_org) ## CONECTAR VARIABLES
                        
                        st.write(output)
                        
    # OUTPUT
    ## Create JSON file
    with st.container():
        st.markdown("""---""")
        st.write('OUTPUT')
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
                add_item(str(st.session_state.label_name), str(st.session_state.label_content))
        with col22:
            if st.button("Limpiar JSON", key='clean_json_a'):
                clear_json()
        with col33:
            # Botón para guardar el archivo JSON completo
            if st.button("Guardar archivo JSON", key='save_json_a'):
                save_json(file_name)
        with col44:
            # add view checkbox
            view_json = st.checkbox("Ver JSON", key='see_a')
        
        if view_json:
            with open("output/"+str(file_name)+'.json') as f:
                data = json.load(f)
                st.json(data)
        
        clear_field()
        
        
                    
        

def contact_interface():
    st.title("Investigadores")
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Mg. Davor Matías Ibarra Pérez")
        st.write("Ph.D (s) en Automática, Robótica e Informática Industrial - UPV")
        st.write("Facultad de Ingeniería - USACH")
        st.write("")
        st.write("")
        st.write("📧 Correo Electrónico: davor.ibarra@usach.cl")
    with col2:
        st.subheader("Dra. María José Galotto López")
        st.write("Ph.D en Farmacia Especialidad Ciencia e Ingeniería de Alimentos - UPV")
        st.write("Departamento de Ingeniería en Alimentos - Facultad Tecnológia - USACH")
        st.write("📧 Correo Electrónico: maria.galotto@usach.cl")
        st.write("🔗 [Sitio Web](https://www.labenchile.cl/)")
    with col3:
        st.subheader("Dra. Alysia Garmulewickz")
        st.write("Ph.D in Management - Saïd Business School, University of Oxford")
        st.write("Economía Circular - Facultad de Administración y Economía - USACH")
        st.write("📧 Correo Electrónico: alysia.garmulewicz@usach.cl ")
        st.write("🔗 [Sitio Web](https://www.garmulewicz.com/)")
    
    
    st.write("---")
    # Custom CSS 
    with st.container():
        st.header("Agradecimientos")
        st.subheader("Desarrollodo por:")
        col1, col2 = st.columns(2)
        with col1:
            st.image("resources/laben.png", width=200)
        with col2:
            st.image("resources/Materiom.png", width=350)
        st.subheader("Financiado por:")
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            st.image("resources/usach.png", width=150)
        with col2:
            st.image("resources/vriic.png", width=400)
        with col3:
            st.image("resources/anid_rojo_azul.png", width=150)



if __name__ == "__main__":
    main()
