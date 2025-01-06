from utils.file_loader import chunker
from utils.vectorizer import add_documents
#from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from dotenv import load_dotenv
import chromadb
import streamlit as st
import os
import tempfile
import pandas as pd
from io import BytesIO

#Provide Environment Variables
load_dotenv()
CHROMADB_HTTPS_ADDRESS=os.getenv('CHROMADB_HTTPS_ADDRESS')
CHROMADB_PORT=os.getenv('CHROMADB_PORT')
CHROMADB_COLLECTION=os.getenv('CHROMADB_COLLECTION')
EMBEDDING_MODEL=os.getenv('EMBEDDING_MODEL')
OLLAMA_HOST=os.getenv('OLLAMA_HOST')
SELECTABLE_TOPICS="Learning Theories and Technologies,Intelligent Tutoring Systems,Student Modeling,Collaborative Learning,Artificial Intelligence in Education".split(sep=",")


def get_collection(client,collection_name:str) -> chromadb.Collection:
    collection = client.get_or_create_collection(name=collection_name)
    return collection

def get_metadata(collection:chromadb.Collection,metadata_field:str) ->list:

    doc_metadata = collection.get(include=["metadatas"])["metadatas"]
    try:
        doc_titles = list(set(list(map(lambda x: x[metadata_field],doc_metadata))))
    except:
        print("No metadate could be retrieved from the vector store")
        doc_titles = ["Nothing to dispaly"]
        pass
    return doc_titles

def init_session_state_variables(st_key:str,default:any)->None:
    if st_key not in st.session_state:
        st.session_state[st_key] = default

initial_session_states = {"select_chunk_size":500,"select_chunk_overlap":50,"selected_topic":SELECTABLE_TOPICS[0]}


def main():
    

    chroma_client = chromadb.HttpClient(
        host=CHROMADB_HTTPS_ADDRESS,
        port=CHROMADB_PORT
        )
    
    embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=OLLAMA_HOST
)
  
    collection_name=CHROMADB_COLLECTION
    collection = get_collection(client=chroma_client,collection_name=collection_name)

  
    st.set_page_config(page_title="Admin App",page_icon=":coffee:")
    st.header("	:coffee: Administer the RAG :coffee:")
    
    for key, value in initial_session_states.items():
        init_session_state_variables(st_key=key,default=value)
    
    env_var_summary_data = {"Parameters": ["OLLAMA_HOST","EMBEDDING_MODEL","CHROMADB_HTTPS_ADDRESS","CHROMADB_PORT","CHROMADB_COLLECTION","Chunk Size", "Chunk Overlap"],"Values":[OLLAMA_HOST,EMBEDDING_MODEL,CHROMADB_HTTPS_ADDRESS,CHROMADB_PORT,CHROMADB_COLLECTION,st.session_state.select_chunk_size,st.session_state.select_chunk_overlap]} 


    st.selectbox(label="Select Topic to assign the documents to",options=SELECTABLE_TOPICS,key="selected_topic")
    

    uploaded_files = st.file_uploader("Upload PDFs you want to add to the indexing",type=['pdf','pptx','docx'],key="files_to_upload",accept_multiple_files=True)
    
    #selected_chunk_size = st.number_input(label="Enter the Chunk Size with which you want to verctorize your Documents",key="select_chunk_size",step=10,placeholder=250)
    #selected_chunk_overlap = st.number_input(label="Enter the Chunk Overlap with which you want to verctorize your Documents",key="select_chunk_overlap",step=10,placeholder=25)

    if st.button(label="Upload files to Vector Store",use_container_width=True):
        chunk = chunker(ChunkSize=st.session_state.select_chunk_size,ChunkOverlap=st.session_state.select_chunk_overlap)
        with st.spinner("Processing"):
            with tempfile.TemporaryDirectory(prefix='__upl_files',dir='.') as tempdir:
                for f in uploaded_files:
                    #Write uploaded files to temporary directory for further processing
                    file_name = f.name
                    st.write(f"Working on uploaded file {file_name}")
                    file_path = f'{tempdir}/{file_name}'
                    file = open(file_path,'wb')
                    file.write(BytesIO(f.read()).getbuffer())
                    file.close()
                    file_extension = os.path.splitext(file_path)[-1]
                    if file_extension == '.pdf':
                        metadata = chunk.extract_pdf_metadata(file_path=file_path,file_name=file_name)
                    elif file_extension == '.docx':
                        metadata = chunk.extract_docx_metadata(file_path=file_path,file_name=file_name)
                    elif file_extension == '.pptx':
                        metadata = chunk.extract_pptx_metadata(file_path=file_path,file_name=file_name)
                    else: 
                        st.write(f"File {file_name} has an invalid extension -> {file_extension}. Continuing to next file")
                        continue
                    validation = chunk.metadata_checker(metadata=metadata)
                    for res in validation["validation_results"]:
                        st.write(res)
                    st.write(validation["status_description"])

                    if validation["status"] == "Failed":
                        st.write(f":black_right_pointing_double_triangle_with_vertical_bar: Skipping file {file_name} because of missing metadata")
                        continue
                    else:
                        text = chunk.document_converter_to_text(file_path=file_path,enable_ocr=False)
                        docs = chunk.document_load(text=text,metadata=metadata,Topic=st.session_state['selected_topic'])
                        add_documents(doc_list=docs,embeddings=embeddings,collection=collection)
                        st.write(f":magic_wand: Sucessfully added file {file_name} to the vector store")
                

            
    with st.container():
        delete_topics, delete_documents = st.columns(2)
        with delete_topics:
            st.selectbox(label="Select a topic which you want to delete",options=get_metadata(collection=collection,metadata_field="Topic"),key="topic_to_delete")
            if st.button(label="Delete selected topic"):
                with st.spinner(":male-factory-worker: Processing"):
                    print('Topics to delete',st.session_state.topic_to_delete)
                    collection.delete(ids=collection.get(where={"Topic":st.session_state.topic_to_delete})['ids'])
        with delete_documents:
            st.selectbox(label="Select a document which you want to delete",options=get_metadata(collection=collection,metadata_field="Title"),key="title_to_delete")
            if st.button(label="Delete selected Document"):
                with st.spinner(":male-factory-worker: Processing"):
                    collection.delete(ids=[],where={"Title":st.session_state.title_to_delete})
            


    
    if st.button(label="Delete All Documents from the Vector Store",use_container_width=True):
        with st.spinner(":male-factory-worker: Processing"):
            chroma_client.delete_collection(collection_name)
    
    st.write("Parameters set for the running application")
    st.table(pd.DataFrame.from_dict(env_var_summary_data))
    
    

    
if __name__ == '__main__':
    main()