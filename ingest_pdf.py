# FILE 1: ingest_pdf.py
# This is the only file that needs to be updated.

import argparse
import os
import math
import sys
import fitz  # PyMuPDF
import chromadb
from tqdm import tqdm
from chromadb.utils import embedding_functions

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# <<< MODIFIED FUNCTION START >>>
def select_or_create_collection(client):
    """Lists existing collections and prompts the user to select one or create a new one."""
    print("--- Select or Create a Collection ---")
    existing_collections = client.list_collections()
    
    if not existing_collections:
        print("No existing collections found.")
    else:
        print("Available collections:")
        for i, col in enumerate(existing_collections):
            print(f"  [{i + 1}] {col.name}")

    print("\nOptions:\n  [c] Create a new collection\n  [q] Quit")

    while True:
        choice = input("Enter your choice (number, 'c', or 'q'): ").strip().lower()
        if choice == 'q': return None
        if choice == 'c': break
        if choice.isdigit():
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(existing_collections):
                    selected_collection = existing_collections[choice_idx]
                    print(f"✅ You selected collection: '{selected_collection.name}'")
                    return selected_collection.name
                else:
                    print("❌ Invalid number. Please try again.")
            except (ValueError, IndexError):
                print("❌ Invalid input. Please try again.")
        else:
            print("❌ Invalid input. Please try again.")
    
    # --- This is the loop with the new validation logic ---
    while True:
        new_collection_name = input("Enter the name for the new collection: ").strip()
        
        # 1. Check if the name is empty
        if not new_collection_name:
            print("❌ Collection name cannot be empty.")
            continue
        
        # 2. Check length constraints (ChromaDB's rule is 3 to 63 characters)
        if not 3 <= len(new_collection_name) <= 63:
            print("❌ Collection name must be between 3 and 63 characters long.")
            continue
            
        # 3. Check start/end character constraints
        if not new_collection_name[0].isalnum() or not new_collection_name[-1].isalnum():
            print("❌ Collection name must start and end with a letter or number.")
            continue
            
        # 4. Check for invalid characters in the name
        # This is a simplified check for common issues like consecutive dots
        if ".." in new_collection_name:
             print("❌ Collection name cannot contain consecutive dots '..'.")
             continue

        # If all checks pass, we can return the name
        print(f"✅ Creating and selecting new collection: '{new_collection_name}'")
        return new_collection_name
# <<< MODIFIED FUNCTION END >>>

def split_text_into_chunks(text, chunk_size=1000, chunk_overlap=200):
    """Splits a long text into smaller chunks with a specified overlap."""
    if not text: return []
    chunks = []
    start_index = 0
    while start_index < len(text):
        end_index = start_index + chunk_size
        chunks.append(text[start_index:end_index])
        start_index += chunk_size - chunk_overlap
    return chunks

def process_pdf(file_path, client, collection_name, chunk_size, chunk_overlap, batch_size):
    """Processes a PDF, chunks it, and stores it in ChromaDB using a specific embedding model."""
    print(f"\nProcessing PDF: {file_path}")
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        print(f"Error opening PDF: {e}"); return

    all_chunks, all_metadatas, all_ids = [], [], []
    chunk_counter = 0

    print("Extracting text and creating chunks...")
    for page_num, page in enumerate(tqdm(doc, desc="Processing pages")):
        page_text = page.get_text()
        if not page_text.strip(): continue
        page_chunks = split_text_into_chunks(page_text, chunk_size, chunk_overlap)
        base_name = os.path.basename(file_path)
        for chunk in page_chunks:
            all_chunks.append(chunk)
            all_metadatas.append({'source': base_name, 'page': page_num + 1})
            all_ids.append(f"{base_name}-p{page_num + 1}-c{chunk_counter}")
            chunk_counter += 1
    doc.close()

    if not all_chunks:
        print("No text could be extracted from the PDF."); return

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
    print(f"Loading collection '{collection_name}' with the '{EMBEDDING_MODEL_NAME}' model.")
    collection = client.get_or_create_collection(name=collection_name, embedding_function=sentence_transformer_ef)
    
    print(f"Adding {len(all_chunks)} chunks to the collection...")
    total_batches = math.ceil(len(all_chunks) / batch_size)
    for i in tqdm(range(0, len(all_chunks), batch_size), total=total_batches, desc="Uploading to ChromaDB"):
        end_index = i + batch_size
        collection.add(
            documents=all_chunks[i:end_index],
            metadatas=all_metadatas[i:end_index],
            ids=all_ids[i:end_index]
        )
    print(f"\n✅ Successfully added all chunks. Total documents in collection: {collection.count()}")

def main():
    parser = argparse.ArgumentParser(description="Read a PDF and store its content in a ChromaDB collection.")
    parser.add_argument("pdf_file", type=str, help="Path to the PDF file.")
    parser.add_argument("--db-path", type=str, default="./chroma_db", help="ChromaDB directory path.")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Size of text chunks.")
    parser.add_argument("--chunk-overlap", type=int, default=200, help="Overlap between chunks.")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for adding to ChromaDB.")
    args = parser.parse_args()

    if not os.path.exists(args.pdf_file):
        print(f"Error: File '{args.pdf_file}' not found."); return

    try:
        client = chromadb.PersistentClient(path=args.db_path)
        collection_name = select_or_create_collection(client)
        if collection_name:
            process_pdf(args.pdf_file, client, collection_name, args.chunk_size, args.chunk_overlap, args.batch_size)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()