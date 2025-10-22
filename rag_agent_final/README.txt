This program is a Retrieval-Augmented Generation (RAG) agent designed to process PDF documents, convert them to markdown, store them in a vector database (VectorDB), and enable querying with a large language model (LLM) to retrieve accurate, business-specific information. It is ideal for accessing contextual information from business-related documents.
Workflow Overview
The RAG agent operates in the following steps:

Clone the repository to access all necessary files.
Add your business-related PDF documents to the designated folder.
Use Docker to convert PDFs to markdown, store them in a VectorDB, and query the LLM for accurate responses.

Prerequisites

Docker Desktop: Ensure Docker Desktop is installed and running on your system.
PDF Documents: Prepare the business-related PDF files you want to process.
Command Line Interface (CLI): Basic familiarity with running commands in a terminal.

Setup and Usage Instructions

Step 1: Clone the Repository
Clone this repository to your local machine to access all required files:
git clone <repository-url>
cd rag_agent_final

Step 2: Add PDF Documents
Place your business-related PDF documents in the pdf_docs folder within the rag_agent_final directory.

Step 3: Ensure Docker Desktop is Running
Open Docker Desktop and ensure it is running before proceeding.

Step 4: Start the Ollama Service
In the rag_agent_final directory, run the following command to start the Ollama service in the background:
docker compose up ollama -d

Step 5: Build the RAG Agent
Build the RAG agent Docker image:
docker compose build rag-agent

Step 6: Convert PDFs to Markdown
Run the batch converter to transform your PDF files into markdown format:
docker-compose run --rm rag-agent python batch_converter.py

When prompted for the input path, enter: /app/pdf_docs
When prompted for the output path, enter: /app/md_docs
Note: This step may take several minutes as dependencies for docling are installed.

Step 7: Run the RAG Agent
Start the main program to store the converted markdown files in a VectorDB:
docker-compose run --rm rag-agent

Step 8: Query the LLM
Once the RAG agent is running, you can interact with the Ollama LLM:

When you see a "-" prompt, the system is waiting for your input.
Ask questions related to your business documents. The LLM will use the VectorDB and, if needed, perform web searches to provide accurate responses.

Step 9: Exit and Clean Up

To exit the program, type "q" at the prompt.
To stop and remove the Docker containers, run:
docker compose down

Notes

Ensure your PDF documents are placed in the pdf_docs folder before running the batch converter.
The conversion process may take time depending on the number and size of the PDFs.
The RAG agent leverages the Ollama LLM to provide context-aware responses based on your business documents.

Thank you for trying out the RAG Agent! If you have any questions or feedback, please feel free to open an issue in the repository.