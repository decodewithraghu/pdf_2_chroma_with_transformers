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

### Step 1: Ingest a PDF into the Database

Use the `ingest_pdf.py` script to process a PDF and add its contents to the database.

**Command:**
```bash
python ingest_pdf.py path/to/your/document.pdf