from beeai_framework.backend.document_loader import DocumentLoader
from beeai_framework.backend.embedding import EmbeddingModel
from beeai_framework.backend.text_splitter import TextSplitter
from beeai_framework.backend.vector_store import VectorStore

async def setup_knowledge_base():
    # Create embedding model using Ollama
    embedding_model = EmbeddingModel.from_name("ollama:nomic-embed-text")
    
    # Create vector store
    vector_store = VectorStore.from_name(
        "beeai:TemporalVectorStore", 
        embedding_model=embedding_model
    )
    
    # Setup text splitter for chunking documents
    text_splitter = TextSplitter.from_name(
        "langchain:RecursiveCharacterTextSplitter", 
        chunk_size=1000, 
        chunk_overlap=200
    )
    
    return vector_store, text_splitter

async def load_documents(vector_store, text_splitter, file_paths):
    """Load documents into the vector store"""
    all_chunks = []
    
    for file_path in file_paths:
        try:
            # Load the document
            loader = DocumentLoader.from_name(
                "langchain:UnstructuredMarkdownLoader", 
                file_path=file_path
            )
            documents = await loader.load()
            
            # Split into chunks
            chunks = await text_splitter.split_documents(documents)
            all_chunks.extend(chunks)
            print(f"Loaded {len(chunks)} chunks from {file_path}")
        except Exception as e:
            print(f"Failed to load {file_path}: {e}")
    
    # Add all chunks to vector store
    if all_chunks:
        await vector_store.add_documents(all_chunks)
        print(f"Total chunks added: {len(all_chunks)}")
    
    return vector_store if all_chunks else None