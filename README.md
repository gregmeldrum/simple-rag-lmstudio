# Simple RAG example using LM Studio Server

Start LM Studio server running on port `1234`.

This repo performs 3 functions:

1. Scrapes a website and follows links under the same path up to a maximum depth and outputs the scraped data to the data directory.
2. Runs an embedding model to embed the text into a Chroma vector database using disk storage (chroma_db directory)
3. Runs a Chat Bot that uses the embeddings to answer questions about the website
main.py runs all 3 functions. 
Once the scraper and embeddings have been completed once, they do not need to be run again. You can simply run the chatbot.py file.

## How to Run
Prerequisite: Run an [LM Studio Server](lmStudio.png)

Download the code:

```
git clone https://github.com/gregmeldrum/simple-rag-lmstudio.git
cd simple-rag-lmstudio
```

Optional - setup a virtual environment:

```
virtualenv venv
source venv/bin/activate
```

Download dependencies and run the functions

```
pip install -r requirements.txt
python main.py
```

Navigate to http://127.0.0.1:7860

After running `main.py` once, the embeddings are persisted, and you can comment out the scrape and embed lines when you re-run `main.py`.



