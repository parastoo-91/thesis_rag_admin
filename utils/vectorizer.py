import chromadb
from uuid import uuid4


# Create logger
#logger = logging.getLogger('vectorizer')
#logger.setLevel(level=logging.INFO)


def add_documents(doc_list:list,embeddings, collection:chromadb.Collection) -> None:
    """
    Adds a list of documents to a specified ChromaDB collection by embedding them using OpenAI embeddings.

    Args:
        doc_list (list): A list of documents to be added, where each document is expected to have 
                         `page_content` and `metadata` attributes.
        embeddings (): An instance of Embeddings used to generate document embeddings. Should be from langchain, as otherwise the embed_query method will not work within this function. 
        collection (chromadb.Collection): The ChromaDB collection where the documents will be stored.

    Returns:
        None: This function does not return any value. It directly adds documents to the collection.

    Raises:
        Exception: May raise exceptions if embedding the documents or adding them to the collection fails.
    """
    #logger.info('Adding document list to the collection')
    print('adding documents')
    for d in doc_list:
        response = embeddings.embed_query(d.page_content)
        embedding = response
        collection.add(
            ids=[str(uuid4())],
            embeddings=[embedding],
            documents=[d.page_content],
            metadatas=[d.metadata]
        )




