# PDF Semantic Search with ChromaDB

This project provides a set of Python scripts to extract text from PDF documents, store it in a ChromaDB vector database, and then perform interactive semantic searches on the content. It's designed to be user-friendly, with interactive menus and progress indicators for a smooth experience.

## Table of Contents
- [Features](#features)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
  - [Step 1: Ingest a PDF into the Database](#step-1-ingest-a-pdf-into-the-database)
  - [Step 2: Interactively Query the Database](#step-2-interactively-query-the-database)
- [File Structure](#file-structure)

## Features

- **PDF Text Extraction**: Uses PyMuPDF (`fitz`) to efficiently extract all text content from PDF files.
- **Intelligent Text Chunking**: Splits large documents into smaller, overlapping chunks suitable for vector embedding.
- **Persistent Vector Storage**: Utilizes ChromaDB to create a local, persistent vector database.
- **Interactive Collection Management**: Allows users to select an existing database collection or create a new one on the fly.
- **Interactive Semantic Search**: Provides a command-line interface to continuously query the database until you choose to exit.
- **User-Friendly Feedback**: Displays progress bars for data ingestion and a spinner animation for search queries.
- **Consistent Embedding Model**: Explicitly uses the `all-MiniLM-L6-v2` model for both ingestion and querying to ensure accurate and relevant search results.

## How It Works

1.  **Ingestion (`ingest_pdf.py`)**:
    - The script reads a PDF file page by page.
    - Text from each page is split into smaller, manageable chunks.
    - Each text chunk is converted into a numerical vector (an "embedding") using the `all-MiniLM-L6-v2` sentence-transformer model. This vector represents the semantic *meaning* of the text.
    - These vectors, along with their original text and metadata (source file, page number), are stored in a specified ChromaDB collection.

2.  **Querying (`verify_db.py`)**:
    - The script connects to the same ChromaDB database.
    - The user selects a collection to search within.
    - When the user types a query (e.g., "what are the project's key risks?"), that query is also converted into a vector using the *exact same model*.
    - ChromaDB then performs a similarity search, finding the text chunks whose vectors are mathematically closest to the query's vector.
    - The most relevant results are returned to the user, demonstrating a search based on meaning rather than just keywords.

## Prerequisites

- Python (3.8 or higher)
- `pip` package manager

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Unix/macOS
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required packages:**
    A `requirements.txt` file is provided for convenience.
    ```bash
    pip install -r requirements.txt
    ```

    If you don't have a `requirements.txt` file, create one with the following content:
    ```
    chromadb
    PyMuPDF
    tqdm
    sentence-transformers
    ```

## Usage

The workflow is a two-step process: first ingest your documents, then query them.

### Step 1: Ingesting data into vector database

Use the `ingest_pdf.py ` load document into the vector database.

**Command:**
```bash
python3 ingest_pdf.py '/read/practical-nestjs-develop-clean-mvc-web-applications-9798410685962_compress.pdf' 
```

**on the terminal :**
```bash
--- Select or Create a Collection ---
Available collections:
  [1] nodejs
  [2] typescript
  [3] reactjs

Options:
  [c] Create a new collection
  [q] Quit
Enter your choice (number, 'c', or 'q'): 
```

** to create new collection, called nestjs :**
```bash
Enter your choice (number, 'c', or 'q'): c
Enter the name for the new collection: nestjs
```

** after the creation of new collection, the document is uploaded:**
```bash
✅ Creating and selecting new collection: 'nestjs'

Processing PDF: /read/practical-nestjs-develop-clean-mvc-web-applications-9798410685962_compress.pdf
Extracting text and creating chunks...
Processing pages: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████| 121/121 [00:00<00:00, 506.22it/s]
Loading collection 'nestjs' with the 'all-MiniLM-L6-v2' model.
Adding 334 chunks to the collection...
Uploading to ChromaDB:   0%|                                                                                                               | 0/4 [00:00<?, ?it/s]/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages/torch/nn/modules/module.py:1762: FutureWarning: `encoder_attention_mask` is deprecated and will be removed in version 4.55.0 for `BertSdpaSelfAttention.forward`.
  return forward_call(*args, **kwargs)
Uploading to ChromaDB: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:04<00:00,  1.01s/it]

✅ Successfully added all chunks. Total documents in collection: 334
````


### Step 2: Verify data from the vector database

Use the `verify_db.py ` script to see the content from the vector database.

**Command:**
```bash
python verify_db.py 
```

**on the terminal :**
```bash
--- Collection Selection ---
Available collections:
  [1] nodejs (61 documents)
  [2] nestjs (334 documents)
  [3] typescript (1632 documents)
  [4] reactjs (4009 documents)
  [q] Quit
Select a collection by number or 'q' to quit: 
```

**Based on the selection:**
```bash
---- Collection Selection ---
Available collections:
  [1] nodejs (61 documents)
  [2] nestjs (334 documents)
  [3] typescript (1632 documents)
  [4] reactjs (4009 documents)
  [q] Quit
Select a collection by number or 'q' to quit: nestjs
❌ Invalid input. Please enter a number.
Select a collection by number or 'q' to quit: 2
Loading collection 'nestjs' with the 'all-MiniLM-L6-v2' model.

✅ Switched to collection: 'nestjs'

Enter your query for 'nestjs' (or type 'back' to change collection, 'quit' to exit): 
```

