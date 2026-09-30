# RAG based Website assistant

import streamlit as st
from rag import process_urls

st.title("RAG based Website assistant")

url1 = st.sidebar.text_input("URL-1")
url2 = st.sidebar.text_input("URL-2")
url3 = st.sidebar.text_input("URL-3")

placeholder = st.empty()

process_url_button = st.sidebar.button("Process URL's")

if process_url_button:
    urls = [url for url in (url1, url2, url3) if url!=""]

    if len(urls) == 0:
        placeholder.text("Please mention atleast one URL")
    else:
        for status in process_urls(urls):
            placeholder.text(status)