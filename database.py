import os
import logging
from dotenv import load_dotenv
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, RecursiveUrlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COMPANY_WEBSITE_URL = #Insert website URL here 

def get_db_connection_string():
    """Retrieves the database connection string from environment variables."""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set. Please set it in .env file.")
    return db_url

def init_vector_store():
    """Initializes the PGVector store."""
    connection_string = get_db_connection_string()
    embeddings = OpenAIEmbeddings()
    
    # Collection name for the RAG data
    collection_name = RAG_data

    vector_store = PGVector(
        embeddings=embeddings,
        collection_name=collection_name,
        connection=connection_string,
        use_jsonb=True,
    )
    return vector_store

def load_pdf_to_vector_store(path: str):
    """Loads PDF(s) from a file or directory, splits them, and adds to the vector store."""
    if not os.path.exists(path):
        logger.error(f"Path not found: {path}")
        return

    files_to_process = []
    if os.path.isdir(path):
        logger.info(f"Scanning directory {path} for PDFs...")
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    files_to_process.append(os.path.join(root, file))
    else:
        files_to_process.append(path)

    if not files_to_process:
        logger.warning(f"No PDF files found in {path}")
        return

    try:
        vector_store = init_vector_store()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)

        for pdf_file in files_to_process:
            try:
                logger.info(f"Loading PDF from {pdf_file}...")
                loader = PyPDFLoader(pdf_file)
                docs = loader.load()
                splits = text_splitter.split_documents(docs)
                
                if splits:
                    vector_store.add_documents(splits)
                    logger.info(f"Successfully added {len(splits)} chunks from {pdf_file}")
                else:
                    logger.warning(f"No content extracted from {pdf_file}")
            except Exception as e:
                logger.error(f"Error processing file {pdf_file}: {e}")

    except Exception as e:
        logger.error(f"Error initializing vector store or processing batch: {e}")

def load_website_to_vector_store(url: str, max_depth: int = 2):
    """Loads a website and its sub-tabs, splits them, and adds to the HappSales knowledge base."""
    logger.info(f"Starting web ingestion for HappSales URL: {url} with max_depth {max_depth}...")
    
    try:
        vector_store = init_vector_store()
        
        # Use simple BeautifulSoup as extractor to get clean text
        def extractor(html: str) -> str:
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text()

        loader = RecursiveUrlLoader(
            url=url, 
            max_depth=max_depth, 
            extractor=extractor,
            prevent_outside=True # Stay on the same domain
        )
        
        docs = loader.load()
        logger.info(f"Loaded {len(docs)} pages from {url}")
        
        if not docs:
            logger.warning(f"No content found at {url}")
            return

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        if splits:
            batch_size = 100
            for i in range(0, len(splits), batch_size):
                batch = splits[i:i + batch_size]
                vector_store.add_documents(batch)
                logger.info(f"Successfully added batch {i//batch_size + 1} ({len(batch)} chunks) from {url}")
            logger.info(f"Successfully completed ingestion for {url}")
        else:
            logger.warning(f"No content extracted from {url}")


    except Exception as e:
        logger.error(f"Error during web ingestion for {url}: {e}")
