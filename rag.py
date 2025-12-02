import os
import shutil
import re
import gc
import time
import stat
from sec_edgar_downloader import Downloader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def remove_readonly(func, path, exc_info):
    """
    Helper function to force remove read-only files (Windows fix).
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)

def cleanup_data(ticker: str):
    """
    Aggressively cleans up the database and filings.
    Uses Garbage Collection to free up file locks.
    """
    db_path = f"./chroma_db_{ticker}"
    filing_path = "sec-edgar-filings"
    
    # 1. Force Python to release memory references to Chroma
    gc.collect()
    
    # 2. Try to remove the Vector Database folder
    if os.path.exists(db_path):
        print(f"🧹 Attempting to delete DB: {db_path}")
        try:
            # First, try standard removal
            shutil.rmtree(db_path, onerror=remove_readonly)
        except Exception as e:
            print(f"⚠️ Lock detected. Waiting 1s to retry... ({e})")
            time.sleep(1.0)
            try:
                # Retry after wait
                shutil.rmtree(db_path, onerror=remove_readonly)
            except Exception as final_e:
                print(f"❌ Could not delete {db_path}: {final_e}")

    # 3. Try to remove the SEC Filings folder
    if os.path.exists(filing_path):
        try:
            shutil.rmtree(filing_path, onerror=remove_readonly)
        except Exception as e:
            print(f"⚠️ Could not delete filings folder: {e}")

def download_and_index_10k(ticker: str):
    # 1. NEW: Check if we already have the data.
    # If the database folder exists and isn't empty, we assume it's good to go.
    db_path = f"./chroma_db_{ticker}"
    if os.path.exists(db_path) and len(os.listdir(db_path)) > 0:
        print(f"✅ Found cached 10-K data for {ticker}. Skipping download.")
        return f"Using cached 10-K risks for {ticker}."

    # 2. If data is NOT there (or it's a new ticker), proceed with cleanup and download
    cleanup_data(ticker)
    print(f"📥 Downloading 10-K for {ticker}...")
    
    dl = Downloader("StudentProject", "nachiketaanand7@gmail.com")
    try:
        dl.get("10-K", ticker, limit=1)
    except Exception as e:
        return f"Error downloading 10-K: {e}"

    filing_path = None
    base_dir = f"sec-edgar-filings/{ticker}/10-K"
    if os.path.exists(base_dir):
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(".txt"):
                    filing_path = os.path.join(root, file)
                    break
    
    if not filing_path:
        return "10-K file not found."

    try:
        with open(filing_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_content = f.read()
            
        soup = BeautifulSoup(raw_content, "html.parser")
        clean_text = soup.get_text(separator=' ', strip=True)
        matches = list(re.finditer(r"Item\s+1A\.?\s+Risk\s+Factors", clean_text, re.IGNORECASE))
        
        if len(matches) > 1:
            start_index = matches[-1].start()
            final_text = clean_text[start_index : start_index + 15000]
        elif len(matches) == 1:
            start_index = matches[0].start()
            final_text = clean_text[start_index : start_index + 15000]
        else:
            mid_point = len(clean_text) // 4
            final_text = clean_text[mid_point : mid_point + 15000]
            
    except Exception as e:
        return f"Error processing file: {e}"

    doc = Document(page_content=final_text, metadata={"source": "10-K", "ticker": ticker})
    
    # Create VectorStore
    vectorstore = Chroma.from_documents(
        documents=[doc],
        embedding=embeddings,
        persist_directory=db_path
    )
    
    # Force connection release explicitly
    vectorstore = None
    del vectorstore
    gc.collect()
    
    return f"Successfully indexed 10-K risks for {ticker}."

def query_risks(ticker: str, query: str):
    db_path = f"./chroma_db_{ticker}"
    if not os.path.exists(db_path):
        return "No 10-K indexed yet."
    
    vectorstore = Chroma(persist_directory=db_path, embedding_function=embeddings)
    results = vectorstore.similarity_search(query, k=3)
    
    # Cleanup connection after query
    del vectorstore
    gc.collect()
    
    return "\n\n".join([doc.page_content for doc in results])