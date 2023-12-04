# Learned most of this from https://docs.trychroma.com/getting-started

import chromadb
chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="my_collection")

# Adding documents to the collection. The first items in each of these lists corresponds to each other.
# ChromaDB will handle changing these into embeddings, it will also download a LLM model if needed
collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "my_source", "page":1}, {"source": "my_source"}],
    ids=["id1", "id2"]
)

results = collection.query(
    query_texts=["This is a query document"],
    n_results=2,
    include=['distances', 'metadatas', 'documents']
)

# Results are returned in order of how closely they matched
print(results)