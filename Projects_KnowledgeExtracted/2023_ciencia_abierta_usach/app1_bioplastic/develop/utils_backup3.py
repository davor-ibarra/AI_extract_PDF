# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 09:42:16 2023

@author: Usuario
"""

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter

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

def pdf_processing_huggingFace(pdf_path):
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
    
    #pdf = PyPDFLoader(pdf_path)
    #pages = pdf.load_and_split()
    #text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024,chunk_overlap=64)
    #chunks = text_splitter.split_documents(pages)
    #embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
    #                                   model_kwargs={'device': 'cpu'})
    #vector_store = FAISS.from_documents(chunks, embedding=embeddings, persist_directory="db")   
    
    return vector_store

def pdf_processing_openAI(pdf_path):
    pdf = PyPDFLoader(pdf_path)
    pages = pdf.load_and_split() ### content + metadata
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024,chunk_overlap=64)
    chunks = text_splitter.split_documents(pages) ### chunk content + metadata
    embeddings = OpenAIEmbeddings(openai_api_key="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", 
                                  openai_organization="org-tRRrVBRW1HaBMqOfzDv9xnFn")
    vector_store = FAISS.from_documents(chunks, embedding=embeddings)#, persist_directory="db")    
    
    return vector_store

def config_assistant(user_question, agent_instructions, vector_store):
    
    # Template for system and human prompts
    system_prompt_template = agent_instructions
    human_prompt_template = user_question
    
    # Creating prompt templates
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_prompt_template)

    # Setting up the AI model
    gpt_4 = ChatOpenAI(temperature=0.02, model_name="gpt-4",openai_api_key="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")

    # Retrieving relevant documents
    relevant_nodes = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 4})

    # Generating and formatting the prompt
    conversation = [system_message_prompt, human_message_prompt]
    chat_prompt = ChatPromptTemplate.from_messages(conversation)
    response = gpt_4(chat_prompt.format_prompt(context=relevant_nodes, text=user_question).to_messages())

    return response

    
def agent_smith(compl_prompt, model_name, vector_store, memory):
    '''
    template = """
                
                Assistant is a large language model trained by OpenAI.
                Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
                Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
                Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
                
                {history}
                Human: {human_input}
                Assistant:"""
    
    
    llm = OpenAI(model_name=model_name, 
                 openai_api_key="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", 
                 openai_organization="org-tRRrVBRW1HaBMqOfzDv9xnFn")
    
        chain = ConversationalRetrievalChain.from_llm(llm=llm, chain_type='stuff',
                                                 retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
                                                 memory=memory)
    
    
    '''
    
    
    
    
    chat = ChatOpenAI(model="gpt-3.5-turbo-1106").bind(response_format={"type": "json_object"})
    
    output = chat.invoke(
        [
            SystemMessage(
                content="Extract the 'name' and 'origin' of any companies mentioned in the following statement. Return a JSON list."
            ),
            HumanMessage(
                content="Google was founded in the USA, while Deepmind was founded in the UK"
            ),
        ]
    )



def create_conversational_chain_simple(vector_store):
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


def create_conversational_chain(vector_store, prompt, compl_prompt):    
    # Chat memory
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    # LLM
    llm = OpenAI(openai_api_key="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", 
                 openai_organization="org-tRRrVBRW1HaBMqOfzDv9xnFn")
    # Prompt + Hystory
    if compl_prompt is None:
        chain = ConversationalRetrievalChain.from_llm(llm=llm, chain_type='stuff',
                                                      retriever=vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 2}),
                                                      memory=memory)
        with get_openai_callback() as c_p:
                response = chain.run(prompt)
                print(c_p)
    # Prompt + Hystory + Complementary prompt
    else:
        messages = [SystemMessagePromptTemplate.from_template(compl_prompt),
                    HumanMessagePromptTemplate.from_template(prompt)
                    ]
        qa_prompt = ChatPromptTemplate.from_messages(messages)
        chain = ConversationalRetrievalChain.from_llm(llm=llm, chain_type='stuff',
                                                      retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
                                                      memory=memory, 
                                                      combine_docs_chain_kwargs={'prompt': qa_prompt})
        with get_openai_callback() as c_p:
                response = chain.run(prompt)
                print(c_p)
    return response
