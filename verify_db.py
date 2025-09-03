# FILE 2: verify_db.py
# This file correctly uses a spinner for the query, as it's not an iterable process.

import chromadb
import argparse
import time
import sys
import threading
import itertools
from chromadb.utils import embedding_functions

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# <<< SPINNER FOR INDETERMINATE WAIT >>>
# This function provides the "in-progress" feedback during the database query.
def spinner_animation(event, message):
    """Displays a spinner animation in the console."""
    spinner = itertools.cycle(['-', '\\', '|', '/'])
    sys.stdout.write(f"{message} ")
    while not event.is_set():
        sys.stdout.write(next(spinner)); sys.stdout.flush(); sys.stdout.write('\b'); time.sleep(0.1)
    sys.stdout.write('\b \b'); sys.stdout.flush()
    print(f"\n{message.replace('...', ' complete!')}")

def select_collection(client):
    """Lists existing collections and prompts the user to select one."""
    print("\n--- Collection Selection ---")
    collections = client.list_collections()
    if not collections:
        print("❌ No collections found. Please ingest data first."); return None

    print("Available collections:")
    for i, col in enumerate(collections):
        print(f"  [{i + 1}] {col.name} ({col.count()} documents)")
    print("  [q] Quit")

    while True:
        choice = input("Select a collection by number or 'q' to quit: ").strip().lower()
        if choice == 'q': return None
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(collections):
                collection_name = collections[choice_idx].name
                sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
                print(f"Loading collection '{collection_name}' with the '{EMBEDDING_MODEL_NAME}' model.")
                collection = client.get_collection(name=collection_name, embedding_function=sentence_transformer_ef)
                return collection
            else:
                print("❌ Invalid number. Please try again.")
        except (ValueError, IndexError):
            print("❌ Invalid input. Please enter a number.")

def perform_query(collection, query_text, n_results, delay):
    """Performs a query on a given collection and displays results."""
    num_to_retrieve = min(n_results, collection.count()) if n_results != -1 else collection.count()
    print(f"\nQuerying for '{query_text}' and retrieving the top {num_to_retrieve} results.")

    stop_event = threading.Event()
    results_container = {}
    def query_chroma():
        results_container['results'] = collection.query(query_texts=[query_text], n_results=num_to_retrieve)
    
    # The spinner thread gives the user feedback while the main thread waits for the query
    spinner_thread = threading.Thread(target=spinner_animation, args=(stop_event, "Searching database..."))
    query_thread = threading.Thread(target=query_chroma)
    spinner_thread.start(); query_thread.start(); query_thread.join(); stop_event.set(); spinner_thread.join()

    results = results_container.get('results')
    if not results or not results.get('documents') or not results['documents'][0]:
        return False
    
    print("\n--- Query Results ---")
    try:
        for i, doc in enumerate(results['documents'][0]):
            print(f"\n--- Result {i+1} of {len(results['documents'][0])} ---")
            print(f"  Distance: {results['distances'][0][i]:.4f}")
            print(f"  Source:   '{results['metadatas'][0][i].get('source', 'N/A')}'")
            print(f"  Document: '{doc}'")
            time.sleep(delay)
        return True
    except KeyboardInterrupt:
        print("\n\nSkipped remaining results."); return True

def main():
    parser = argparse.ArgumentParser(description="Interactively query a Chroma database collection.")
    parser.add_argument("--db-path", type=str, default="./chroma_db", help="ChromaDB directory path.")
    parser.add_argument("--n-results", type=int, default=5, help="Number of query results to return. Use -1 for all.")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between displaying results.")
    args = parser.parse_args()

    try:
        client = chromadb.PersistentClient(path=args.db_path)
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}"); sys.exit(1)

    while True:
        collection = select_collection(client)
        if collection is None: break
        print(f"\n✅ Switched to collection: '{collection.name}'")
        while True:
            query_text = input(f"\nEnter your query for '{collection.name}' (or type 'back' to change collection, 'quit' to exit): ").strip()
            if not query_text: continue
            if query_text.lower() == 'quit': print("Exiting."); sys.exit(0)
            if query_text.lower() == 'back': break
            
            if not perform_query(collection, query_text, args.n_results, args.delay):
                print(f"\nℹ️ No matching documents found in '{collection.name}'.")

    print("\nGoodbye!")

if __name__ == "__main__":
    main()