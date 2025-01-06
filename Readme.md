**Install Virtual enviroment**
python -m venv .venv

**Setting up the environment Variables**
Following enviorment variables are required and to be defined in the .env file: 

- EMBEDDING_MODEL: This defines the embedding model that you want to use from Ollama. Please make sure that you have pulled the model from Ollama. You can find a list of embedding models [HERE](https://ollama.com/search?c=embedding). *Example Value ->* "mxbai-embed-large" 
- OLLAMA_HOST: This defines the host of your Ollama instance. Per default it is "127.0.0.1:11434", but after changing the OLLAMA_HOST enviornment variable of your system it should point to your localhost, otherwise the Docker Container will no be able to access it. Further information on the same can be found [HERE](https://www.restack.io/p/ollama-answer-bind-to-0-0-0-0-cat-ai). *Example Value ->* "192.168.0.27:11434" 
- CHROMADB_HTTPS_ADDRESS: This is the address of your Chroma Docker container, that is used for the ChromaHttpClient within the streamlit App. When running the container (via docker run) for example with --port 8000:8000 the database will be exposed to your localhost and port that you defined in afore mentioned argument.  *Example Value ->* "192.168.0.27"
- CHROMADB_PORT: The port of the host on which the ChromaDb is running. *Example Value ->* 8000
- CHROMADB_COLLECTION=This is the name of the collection that you want to create inside of your chroma datbase. Further information of collections can be found [HERE](https://cookbook.chromadb.dev/core/collections/). *Example Value ->* "scientific_papers"


**Run App locall in Streamlit inside of venv** 

The below steps should work fine if you are using python:3.11 or higher

Required Steps:
- python -m venv .venv 
- .venv/scripts/activate
- pip install -r requirements.txt
- streamlit run main.py       


**Build docker image, e.g. after doing changes**
docker build -t thesis_rag_admin .

**Run the docker image py passing the env variables**

docker run  --env=EMBEDDING_MODEL=mxbai-embed-large --env=OLLAMA_HOST=192.168.0.27:11434 --env=CHROMADB_HTTPS_ADDRESS=192.168.0.27 --env=CHROMADB_PORT=8000 --env=CHROMADB_COLLECTION=scientific_papers   -p 8502:8502 -d thesis_rag_admin:latest

**Prequisites**
- Make sure to set OLLAMA_HOST environment variable to 0.0.0.0, otherwise the dockercontainer will not be able to access the ollama service
- Make sure that you are running version 0.6.2 of ChromaDB. There have been compatability issues between 0.6.2 and older chromadb Python libraries. [Guide to installing Chroma as a Docker Container](https://docs.trychroma.com/production/containers/docker)


