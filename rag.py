# In this file we will process the data

# Operations perfromed in this file:
# 1. exporting data from URLs
# 2. Chunking data 
# 3. storing chunks into ChromaDB
# 4. Sending and Receiving Query/results from LLM


# Library required
from uuid import uuid4    # generate unique id for every chunk
from dotenv import load_dotenv     # read the .env file for API key
from pathlib import Path  # tell the path to store vectorDB
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

#loading the API key
load_dotenv()

# Initialize variables
CHUNK_SIZE = 1000
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VERTORSTORE_DIR = Path(__file__).parent/"resurces/vectorstore"
COLLECTION_NAME = "web_assistant"
llm = None
vector_store = None

def initialize_components():
    global llm, vector_store

    if llm is None:
        llm = ChatGroq(
            model = "openai/gpt-oss-20b",
            temperature = 0.7,  # control hallucination
            max_tokens = 1000  # max length of answer given by llm
        )

    if vector_store is None:
        embedding = HuggingFaceEmbeddings( model_name = EMBEDDING_MODEL )

        vector_store = Chroma(
            collection_name = COLLECTION_NAME,
            embedding_function = embedding,
            persist_directory = str(VERTORSTORE_DIR)
        )

def process_urls(urls):
    yield "Initialize components..."
    initialize_components()

    yield "Reseting the vector store..."
    vector_store.reset_collection()

    yield "loading data from URL's..."
    loader = UnstructuredURLLoader(urls = urls )
    document = loader.load()

    yield "creating chunks by splitting..."
    splitter = RecursiveCharacterTextSplitter(
        separator = ["\n\n", "\n", ".", " "],
        chunk_size = CHUNK_SIZE,
        chunk_overlap = 100
    )

    docs = splitter.split_documents(document)

    yield "Adding the chunks in ChromaDB..."
    ids = [str(uuid4()) for _ in range(len(docs))]

    vector_store.add_documents(docs, ids = ids)

    yield "Successfully store docs in ChromaDB"