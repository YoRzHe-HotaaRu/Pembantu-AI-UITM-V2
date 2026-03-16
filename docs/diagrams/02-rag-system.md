# RAG System Architecture

## Overview

The Retrieval-Augmented Generation (RAG) system enhances AI responses by retrieving relevant information from the UiTM knowledge base before generating answers.

## RAG Component Architecture

```mermaid
graph TB
    subgraph "RAG Manager"
        RM[RAG Manager]
        INIT[Initialize]
        QUERY[Query Handler]
    end

    subgraph "Document Processing"
        DL[Document Loader]
        CHUNK[Text Chunker]
    end

    subgraph "Storage"
        VS[Vector Store]
        CACHE[Embedding Cache]
    end

    subgraph "Retrieval"
        SIMP[Simple Retriever]
        HYB[Hybrid Retriever]
    end

    RM --> INIT
    RM --> QUERY
    INIT --> DL
    DL --> CHUNK
    CHUNK --> VS
    VS --> CACHE
    QUERY --> SIMP
    QUERY --> HYB
```

## Document Loading Process

```mermaid
flowchart TD
    A[Start: Initialize RAG] --> B{KB Path Exists?}
    B -->|No| C[Log Error]
    B -->|Yes| D[Scan Category Directories]

    D --> E{Found Category?}
    E -->|No| F[End: No Documents]
    E -->|Yes| G[Read Files in Category]

    G --> H{File Found?}
    H -->|No| I[Next Category]
    H -->|Yes| J{File Type?}

    J -->|Markdown| K[Parse Markdown]
    J -->|JSON| L[Parse JSON]
    J -->|TXT| M[Parse Text]
    J -->|PDF| N[Parse PDF]

    K --> O[Extract Title]
    L --> O
    M --> O
    N --> O

    O --> P[Clean Content]
    P --> Q[Create Document Object]
    Q --> R[Add to Collection]

    R --> S{More Files?}
    S -->|Yes| H
    S -->|No| I

    I --> T{More Categories?}
    T -->|Yes| D
    T -->|No| U[End: Documents Loaded]
```

## Query Processing Flow

```mermaid
sequenceDiagram
    participant A as App.py
    participant M as RAG Manager
    participant S as Retriever
    participant V as Vector Store
    participant D as Document Loader

    A->>M: query(text, top_k, category)

    alt Advanced Mode Enabled
        M->>S: Hybrid Retriever
        S->>V: Semantic Search
        V-->>S: Vector Results
        S->>S: Rerank Results
    else Lightweight Mode
        M->>S: Simple Retriever
        S->>D: Keyword Search
        D-->>S: Matched Chunks
    end

    S-->>M: Retrieved Chunks
    M->>M: Format Context
    M->>M: Extract Sources
    M-->>A: {context, sources, chunks}
```

## Two-Mode Retrieval System

```mermaid
graph LR
    subgraph "Lightweight Mode"
        KW[Keyword Matching]
        TF[TF-IDF Scoring]
        CAT[Category Filter]
    end

    subgraph "Advanced Mode"
        EMB[Embedding Generation]
        VEC[Vector Similarity]
        HYB[Hybrid Scoring]
    end

    Q[User Query] --> KW
    Q --> EMB

    KW --> TF
    TF --> CAT

    EMB --> VEC
    VEC --> HYB
```

## RAG Initialization Sequence

```mermaid
sequenceDiagram
    autonumber
    participant APP as app.py
    participant RM as RAGManager
    participant DL as DocumentLoader
    participant SR as SimpleRetriever
    participant AR as AdvancedRetriever

    APP->>RM: initialize()

    Note over RM,Dl: Step 1: Load Documents
    RM->>DL: load_all()
    DL-->>RM: List<Document>
    RM->>RM: Count Documents

    Note over RM,SR: Step 2: Build Keyword Index
    RM->>SR: build_index()
    SR->>SR: Create Chunk Index
    SR-->>RM: Index Ready

    alt Advanced Mode Enabled
        Note over RM,AR: Step 3: Advanced Features
        RM->>RM: Check Cache
        alt Cache Miss
            RM->>SR: chunk_documents()
            RM->>RM: Generate Embeddings
            RM->>RM: Store Vectors
        end
        RM->>AR: Initialize Hybrid Retriever
    else Lightweight Mode
        RM->>RM: Skip Advanced Features
    end

    RM-->>APP: RAG System Ready
```

## Document Chunking (Advanced Mode)

```mermaid
flowchart LR
    A[Full Document] --> B[Split by Sections]
    B --> C{Chunk Size < Max?}

    C -->|Yes| D[Keep Section]
    C -->|No| E[Split Further]

    E --> F[Split by Paragraphs]
    F --> G{Still Too Large?}
    G -->|Yes| H[Split by Sentences]
    G -->|No| I[Add Overlap]

    H --> I
    D --> I
    F --> I

    I --> J[Store Chunk]
    J --> K{More Sections?}
    K -->|Yes| B
    K -->|No| L[All Chunks Ready]
```

## Source: `rag/rag_manager.py`

```python
class RAGManager:
    """
    Main manager for the RAG system
    Coordinates document loading, chunking, and retrieval
    """

    def initialize(self, force_reindex: bool = False):
        # Step 1: Load documents
        documents = self.document_loader.load_all()

        # Step 2: Build simple retriever (lightweight)
        self.simple_retriever = SimpleRetriever(self.document_loader)
        self.simple_retriever.build_index()

        # Step 3: Advanced features (optional)
        if self.use_advanced:
            self._init_advanced_features(force_reindex)

    def query(self, query_text: str, top_k: int = 5, category_filter: Optional[str] = None):
        if self.use_advanced and self.hybrid_retriever:
            return self._query_advanced(...)
        else:
            return self._query_simple(...)
```

## Source: `rag/simple_retriever.py`

```python
class SimpleRetriever:
    """Keyword-based retrieval without embeddings"""

    def build_index(self):
        """Build inverted index for keyword search"""
        for doc in self.document_loader.documents:
            chunks = self._chunk_document(doc.content)
            for chunk in chunks:
                self.chunk_index.append({
                    'content': chunk,
                    'doc_id': doc.id,
                    'category': doc.category
                })

    def retrieve(self, query: str, top_k: int, category_filter: str = None):
        """Retrieve chunks by keyword matching"""
        scores = []
        for chunk in self.chunk_index:
            score = self._keyword_score(query, chunk['content'])
            if category_filter:
                if chunk['category'] == category_filter:
                    scores.append((score, chunk))
            else:
                scores.append((score, chunk))

        scores.sort(reverse=True)
        return [chunk for score, chunk in scores[:top_k]]
```

---

*Generated for UiTM AI Receptionist - RAG System Documentation*
