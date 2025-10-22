This program is a RAG agent that starts off by converting a batch of pdfs to markdown.
It then creates a vectorDB and stores the markdown files which could be files giving context about a business.
You are then able to run the rag agent to query the LLM and get accuracte information in regards to your business.

The workflow is as follows:

Step 1:
- Clone this repo so you have all relevant files 

Step 2: 
- Add relevent business pdf docs to the pdf_docs folder

Step 3:
- Have Docker desktop installed and open

Run the follow steps in the rag_agent_final dir in CLI

Step 4:
- docker compose up ollama -d

Step 5: 
- docker compose build rag-agent

Step 6: 
- docker-compose run --rm rag-agent python batch_converter.py
- for input path type in: /app/pdf_docs
- for output path type in: /app/md_docs

Step 7:
- docker-compose run --rm rag-agent
