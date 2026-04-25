import os
import glob
from pathlib import Path
from langchain_community.document_loaders import CSVLoader, DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


from dotenv import load_dotenv

MODEL = "gpt-4.1-nano"

DB_NAME = str(Path(__file__).parent.parent / "vector_db")
KNOWLEDGE_BASE = str(Path(__file__).parent.parent / "knowledge-base")
COLLECTION_NAME = "netflix_knowledge_base"

load_dotenv(override=True)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def fetch_documents():

    # Define the path to your specific CSV file
    file_path = KNOWLEDGE_BASE +"/netflix-dataset.csv"

    # Initialize the loader
    # Use 'metadata_columns' to automatically move the 'type' column into the metadata dict
    loader = CSVLoader(
        file_path=file_path,
        encoding='utf-8',
        metadata_columns=["type"]  # This extracts 'Movie' or 'TV Show' into metadata
    )

    # Load the data into document objects
    documents = loader.load()

    # Update the metadata key name to 'doc_type' as per your requirement
    for doc in documents:
        # 'type' is now in metadata because of the loader configuration above
        doc.metadata["show_type"] = doc.metadata.get("type")
        
        # Optional: Remove the original 'type' key if you only want 'doc_type'
        # del doc.metadata["type"]

    return documents


def create_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    return chunks


def create_embeddings(chunks):
    if os.path.exists(DB_NAME):
        Chroma(
            collection_name=COLLECTION_NAME,
            persist_directory=DB_NAME,
            embedding_function=embeddings,
        ).delete_collection()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_NAME,
        collection_name=COLLECTION_NAME,
    )

    collection = vectorstore._collection
    count = collection.count()

    sample_embedding = collection.get(limit=1, include=["embeddings"])["embeddings"][0]
    dimensions = len(sample_embedding)
    print(f"There are {count:,} vectors with {dimensions:,} dimensions in the vector store")
    return vectorstore


if __name__ == "__main__":
    documents = fetch_documents()
    chunks = create_chunks(documents)
    create_embeddings(chunks)
    print("Ingestion complete")