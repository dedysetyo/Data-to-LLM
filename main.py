#!/usr/bin/python3

import os
import gradio as gr
import chromadb

from dotenv import load_dotenv

from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.core import (
        VectorStoreIndex,
        SimpleDirectoryReader,
        StorageContext,
        )
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.memory import ChatMemoryBuffer

load_dotenv(override=True)

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

CHROMA_DIR = os.getenv('CHROMA_DIR')
DB_NAME = os.getenv('DATA_NAME').replace(" ", "")
TITLE = os.getenv('DATA_NAME').capitalize()

text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=10)

Settings.llm = OpenAI(temperature=0.2, model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.chunk_size = 512
Settings.text_splitter = text_splitter

def initiate_db():
    db = chromadb.PersistentClient(path=CHROMA_DIR)
    chroma_collection = db.get_or_create_collection(DB_NAME)

    return chroma_collection

def chatbot(input_text, history):
    memory = ChatMemoryBuffer.from_defaults(token_limit=3900)
    response = index.as_chat_engine(chat_mode="condense_plus_context", memory=memory, verbose=False).chat(input_text)

    return response.response

if not os.path.exists(CHROMA_DIR):
    print("Creating index...")

    documents = SimpleDirectoryReader("data").load_data()
    chroma_collection = initiate_db()
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
        documents, storage_context=storage_context, transformations=[text_splitter]
    )
else:
    print("Index found, loading...")
    chroma_collection = initiate_db()
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
    )

chat = gr.ChatInterface(fn=chatbot, title=TITLE + " ChatBot")

chat.launch(share=False, server_name='0.0.0.0', ssl_verify=False)
