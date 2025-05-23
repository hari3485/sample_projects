import os
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader

def get_retrieved_context(temp_path, query):
    """
    Loads the input PDF or TXT file, splits it into chunks,
    embeds and indexes it using FAISS, and retrieves the top relevant chunks.

    Args:
        temp_path (str): Path to the input file (.pdf or .txt).
        query (str): User query to search within the document.

    Returns:
        List[str]: A list of page content strings relevant to the query.
    """
    # Choose appropriate loader based on file type
    if temp_path.endswith(".pdf"):
        loader = PyPDFLoader(temp_path)
    else:
        loader = TextLoader(temp_path)

    # Load and split the document into chunks
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    pages = splitter.split_documents(docs)

    # Initialize OpenAI embeddings
    embedding = OpenAIEmbeddings()

    # Create FAISS vector store from chunks
    vector_store = FAISS.from_documents(pages, embedding)

    # Use the retriever to fetch top-k relevant chunks
    retriever = vector_store.as_retriever(search_kwargs={"k": 6})
    retrieved_docs = retriever.get_relevant_documents(query)

    return [doc.page_content for doc in retrieved_docs]
