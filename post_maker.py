import ollama
import chromadb
from docx import Document
import random
import string
collection_name = ""
def extract_text_from_docx(file_path):
    doc = Document(file_path)
    text = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text.strip())
    return text

def make_post(document):
    documents = extract_text_from_docx(document)

    global collection_name
    collection_name = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
    client = chromadb.Client()
    collection = client.create_collection(name=collection_name)
    

    for i, d in enumerate(documents):
        response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
        embedding = response["embedding"]
        collection.add(
            ids=[str(i)],
            embeddings=[embedding],
            documents=[d]
        )


    prompt = "Напиши пост для блога"


    response = ollama.embeddings(
    prompt=prompt,
    model="mxbai-embed-large"
    )
    results = collection.query(
    query_embeddings=[response["embedding"]],
    n_results=1
    )
    data = results['documents'][0][0]



    output = ollama.generate(
    model="llama3.1",
    prompt=f"Using this file data: {data}. Respond to this prompt: {prompt}"
    )
    
    client.delete_collection(collection_name)
    return output['response']