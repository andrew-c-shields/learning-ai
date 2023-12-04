# Learned most of this from https://docs.trychroma.com/getting-started and https://www.youtube.com/watch?v=QSW2L8dkaZk
# Sample CSV can be found https://github.com/johnnycode8/chromadb_quickstart

import csv
import chromadb
from chromadb.utils import embedding_functions

# Load the CSV file
with open(r'C:\Users\Andrew\Documents\Desktop\AI\Sample Data\06_menu_items.csv') as file:
    lines = csv.reader(file)

    documents = []
    metadatas = []
    ids = []
    id = 1

    # Iterate through each line of the CSV file
    for i, line in enumerate(lines):
        # Skip the header row
        if i == 0:
            continue

        # line[0] is the item id from the menu
        # line[1] is the item name
        documents.append(line[1])
        metadatas.append({"item_id": line[0]})
        ids.append(str(id))
        id+=1

chroma_client = chromadb.Client()

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-mpnet-base-v2") # default -> model_name="all-MiniLM-L6-v2"
collection = chroma_client.create_collection(name="my_collection", embedding_function=sentence_transformer_ef)

# Adding documents to the collection. The first items in each of these lists corresponds to each other.
# ChromaDB will handle changing these into embeddings, it will also download a LLM model if needed
# Default LLM is all-MiniLM-L6-v2
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

results = collection.query(
    query_texts=["shrimp"], # Asking for shrimp as the model has no dishes with the word "shrimp" in the names
    n_results=5,
    include=["documents"]
)

# Results are returned in order of how closely they matched
print(results["documents"])