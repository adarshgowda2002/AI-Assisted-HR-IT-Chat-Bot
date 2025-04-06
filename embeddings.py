import os
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings
#from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz

class PDFLoader:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def load(self):
        documents = []
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".pdf"):
                file_path = os.path.join(self.folder_path, filename)
                try:
                    with fitz.open(file_path) as doc:
                        text = ""
                        for page in doc:
                            text += page.get_text()
                        documents.append({"content": text, "metadata": {"source": filename}})
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        return documents

# Document class to wrap the dictionaries
class Document:
    def __init__(self, content, metadata):
        self.page_content = content
        self.metadata = metadata

data_folder = "data"
try:
    loader = PDFLoader(data_folder)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents:")
    for doc in documents:
        print(f" - {doc['metadata']['source']}")
except Exception as e:
    print(f"Error loading documents: {e}")
    exit()

# Convert dictionaries to Document objects
document_objects = [Document(doc['content'], doc['metadata']) for doc in documents]


text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(document_objects)


# ---------------------------
# 2. Create embeddings and vector store
# ---------------------------
persist_directory = "chroma_db"
embeddings = OllamaEmbeddings(model="deepseek-r1")
#embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

vectorstore = Chroma.from_documents(
    chunks, embedding=embeddings, persist_directory=persist_directory
)

"""vectorstore = Chroma.from_documents(
    chunks, embedding=embeddings, persist_directory=persist_directory
)
"""
# Check Chroma contains all documents
print("Chroma DB contains:", vectorstore._collection.count())


def retrieve_context(query: str) -> str:
    """
    Searches the appropriate ChromaDB collection for relevant context.
    """
    results = vectorstore.similarity_search(query, k=3)  # Get top 3 relevant chunks

    if results:
        return " ".join([result.page_content for result in results])  # Return the most relevant chunks
    return "Policy not found. Please refine your query."

