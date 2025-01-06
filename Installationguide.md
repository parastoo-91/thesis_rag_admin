# Installation Guide

In order to setup the  the RAG a few steps are required. Follow the steps in the below defined order.


## 1. Setup Chroma Docker Container
- Pull the docker image with version 0.5.23 from the docker hub: `docker pull chromadb/chroma:0.5.23`
- Run the image `docker run -p 8000:8000 chromadb/chroma:0.5.23` 
- Always rerun the container that you initially created, as it will have the data stored. Running the same docker run command again, will create a new container in which no data is stored. 
- The Chroma database should then be accessible via localhost:8000

## 2. Setup Ollama
- Setup the environment varilable OLLAMA_HOST on your system. Make sure that it is set to `0.0.0.0`. This ensures that Ollama is network wide available. The standard port is `:11434`
- Download [Ollama](https://ollama.com/)
- pull a LLM (i.e. [llama 3.2](https://ollama.com/library/llama3.2))and embedding model (i.e. [mxbai-embed-large](https://ollama.com/library/mxbai-embed-large)) for Ollama
- Check if Ollama is running correctly by navigating to `http:\\[YOUR HOST IP ADRESS]::11434`. Your should see a message "Ollama is running"
- check if you pulled your models correctly by checking `ollama list` in your terminal
 

## 3. Setup Container for the Admin App
- Pull the code from the [Github Repo](https://github.com/parastoo-91/thesis_rag_admin)
- navigate to the pulled repository in your repo and run the docker build command: `docker build -t rag_admin_app .`. Running the build command can take some time (even up to 30 minutes). 
- Now run the image by passing all the environment variables into the docker run command `docker run  --env=EMBEDDING_MODEL=mxbai-embed-large --env=OLLAMA_HOST=http://192.168.0.27:11434 --env=CHROMADB_HTTPS_ADDRESS=192.168.0.27 --env=CHROMADB_PORT=8000 --env=CHROMADB_COLLECTION=scientific_papers  -p 8502:8502 -d thesis_rag_admin:latest`
- It is important to set the enviornment variables so that the application works on your system. Check all the IP adresses and make sure that the models you specify are installed in your Ollama. When providing the IP adress for the Ollama host make sure that it has `http:\\` in front, otherwise the langchain_ollama library will throw an error. 
- Open the App and check if everything is running as expected by uploading a document and seeing that it is succesfully passing the metadata check and being uploaded to the Vector database. 

## 4. Setup Container for the Students frontend
- Pull the code from the [Github Repo](https://github.com/parastoo-91/RAG)
- navigate to the pulled repository in your repo and run the docker build command: `docker build -t thesis_rag .`. Running the build command here should take less time than the previous image.
- Now run the image by passing all the environment variables into the docker run command `docker run  --env=EMBEDDING_MODEL=mxbai-embed-large --env=OLLAMA_HOST=http://192.168.0.27:11434 --env=CHROMADB_HTTPS_ADDRESS=192.168.0.27 --env=CHROMADB_PORT=8000 --env=CHROMADB_COLLECTION=scientific_papers --env=RETRIEVER_K_NUMBER=20 --env=RETRIEVER_RELEVANCE_SCORE=0.2 --env=LLM_MODEL=llama3.2:3b --mount type=bind,src=F:\Dokumente\rag_logs,dst=/thesis_rag/logs  -p 8504:8504 -d rag_thesis:latest`
- The enviornment variables are similar to the Admin app, but here we can see a few additional ones. Detailed info on the same can be found in the respective Readme of the repo. **Make sure that you pass the correct arguments when setting up the mount** after the `--mount` command, as this will enable that **student chats are tracked**.
- Check the app by opening a chat, selecting documents and seeing that the logs are stored on your desired location. 