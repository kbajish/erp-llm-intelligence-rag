# 🤖 ERP LLM Intelligence (RAG System)

![CI](https://github.com/kbajish/erp-llm-intelligence-rag/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/docker-compose-blue)

ERP LLM Intelligence is a Retrieval-Augmented Generation (RAG) system that enables natural language querying of ERP data across Sales & Distribution (SD) and Materials Management (MM) modules. Business users can ask questions like "What are the top customers by order value?" or "Which products are below safety stock level?" and receive accurate, context-aware answers grounded in actual data rather than LLM hallucinations.

Built on the AdventureWorks dataset — a standard enterprise business database covering real sales orders, customers, products, inventory, and purchase orders. The system reduces dependency on manual reporting tools by allowing non-technical users to query ERP data using natural language.

This project demonstrates the architecture and retrieval patterns of an ERP-integrated RAG system. It is intended as a reference implementation and learning resource, not a deployment-ready system.

---

## 🚀 Key Features

- 📊 AdventureWorks dataset — real SD and MM ERP data (121K sales orders, 504 products, 19K customers)
- 🧩 Table-aware chunking preserving column context for accurate retrieval
- 🔍 Semantic search using embeddings (nomic-embed-text via Ollama)
- 🗄 Persistent vector store using ChromaDB (no re-indexing on restart)
- 🤖 LangChain RAG pipeline with source-grounded responses
- 📚 Source citation — every answer includes retrieved records
- 📈 Retrieval evaluation using MRR and Recall@5 tracked via MLflow
- 💬 Streamlit chatbot UI with conversation memory and dynamic visualisations
- ⚡ FastAPI backend (`/query`, `/health`)
- 🐳 Docker Compose for reproducible full-stack deployment
- 🔄 GitHub Actions CI for testing and validation

---

## 🧠 Why RAG instead of SQL?

Traditional ERP reporting relies on structured queries or predefined dashboards, which require technical knowledge and limit flexibility. This system enables semantic search and natural language interaction, allowing users to ask complex, context-aware business questions without knowing database schemas or writing queries.

---

## 🧠 System Architecture

```
AdventureWorks Dataset (SD + MM modules)
        ↓
src/data/loader.py             — loads and cleans AdventureWorks CSVs
        ↓
src/chunking/chunker.py        — table-aware chunking strategy
        ↓
src/embeddings/ingest.py       — nomic-embed-text via Ollama
        ↓
chroma_db/                     — persistent ChromaDB vector store
        ↓
src/rag/chain.py               — LangChain RAG pipeline
        ↓
src/llm/prompts.py             — structured prompt templates
        ↓
api/main.py                    — FastAPI (/query, /health)
        ↓
dashboard/app.py               — Streamlit chatbot + charts
        ↓
src/evaluation/metrics.py      — MRR, Recall@5 → MLflow
```

---

## ⚙️ How It Works

AdventureWorks ERP data covering SD and MM modules is loaded, cleaned, and structured into five business tables — sales orders, customer master, product master, stock levels, and purchase orders. The loader normalises dates, maps status codes to readable labels, joins related tables (e.g. sales orders enriched with product names), and saves clean CSVs ready for chunking.

The data is processed using a table-aware chunking strategy that preserves column relationships, ensuring semantic meaning is retained during retrieval. Chunks are embedded using a local embedding model (nomic-embed-text via Ollama) and stored in a persistent ChromaDB vector database. When a user submits a query, the system retrieves the most relevant records and passes them to llama3.2 via a LangChain RAG chain. The LLM generates a response grounded in the retrieved context, along with source references showing exactly which records were used.

Retrieval quality metrics (MRR and Recall@5) are logged to MLflow after each query, enabling ongoing evaluation of the RAG pipeline.

---

## 📊 Dataset Overview

| Table | Source | Rows | Description |
|---|---|---|---|
| Sales orders | SalesOrderHeader + SalesOrderDetail + Product | 121,317 | Orders with product names, quantities, values |
| Customer master | Customer | 19,820 | Customer accounts and territories |
| Product master | Product | 504 | Products with safety stock and reorder points |
| Stock levels | ProductInventory + Product | 432 | Current stock vs safety stock per product |
| Purchase orders | PurchaseOrderHeader + PurchaseOrderDetail | 8,845 | Vendor orders with status and quantities |

---

## 📊 Dashboard Overview

The Streamlit dashboard provides:

- 💬 Chat interface for natural language ERP queries
- 📊 Dynamic bar and line charts for numeric responses
- 📚 Retrieved source records panel for answer transparency
- 🔢 Key business metrics — total revenue, open orders, stock alerts
- 🔁 Conversation history within the session

---

## 🛠 Tech Stack

| Layer | Tool |
|---|---|
| Dataset | AdventureWorks (Microsoft open dataset) |
| Embeddings | nomic-embed-text (Ollama) |
| Vector store | ChromaDB (persistent, local) |
| RAG orchestration | LangChain |
| LLM | llama3.2 (Ollama, local) |
| Backend | FastAPI, Uvicorn |
| Dashboard | Streamlit |
| Experiment tracking | MLflow |
| Containerisation | Docker Compose |
| CI/CD | GitHub Actions |
| Testing | pytest |

---

## 📂 Project Structure

```
erp-llm-intelligence-rag/
│
├── data/                          # ERP CSV files (not committed)
│   ├── sd/                        # Sales & Distribution tables
│   │   ├── SalesOrderHeader.csv   # Raw AdventureWorks files
│   │   ├── SalesOrderDetail.csv
│   │   ├── Customer.csv
│   │   ├── sales_orders_clean.csv # Cleaned output from loader
│   │   └── customer_master_clean.csv
│   └── mm/                        # Materials Management tables
│       ├── Product.csv            # Raw AdventureWorks files
│       ├── ProductInventory.csv
│       ├── PurchaseOrderHeader.csv
│       ├── PurchaseOrderDetail.csv
│       ├── product_master_clean.csv  # Cleaned output from loader
│       ├── stock_levels_clean.csv
│       └── purchase_orders_clean.csv
│
├── chroma_db/                     # ChromaDB persistent store (not committed)
│
├── src/
│   ├── data/
│   │   └── loader.py              # AdventureWorks data loader + cleaner
│   ├── chunking/
│   │   └── chunker.py             # Table-aware chunking logic
│   ├── embeddings/
│   │   └── ingest.py              # Embedding + ChromaDB ingestion
│   ├── rag/
│   │   └── chain.py               # LangChain RAG chain
│   ├── llm/
│   │   └── prompts.py             # Prompt templates
│   └── evaluation/
│       └── metrics.py             # MRR, Recall@5, MLflow logging
│
├── api/
│   └── main.py                    # FastAPI app
│
├── dashboard/
│   └── app.py                     # Streamlit chatbot UI
│
├── tests/
│   ├── test_imports.py            # CI-safe import tests
│   └── test_loader.py             # Data loader smoke tests
│
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions pipeline
│
├── mlruns/                        # MLflow tracking (not committed)
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.dashboard
├── .env.example
├── requirements.api.txt
├── requirements.dashboard.txt
├── requirements.dev.txt
├── AI_ACT_COMPLIANCE.md
└── README.md
```

---

## ▶️ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/kbajish/erp-llm-intelligence-rag.git
cd erp-llm-intelligence-rag
```

### 2. Create and activate virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
```

### 3. Download AdventureWorks CSV files
Download the following files from the [AdventureWorks repository](https://github.com/Microsoft/sql-server-samples/tree/master/samples/databases/adventure-works/oltp-install-script) and place them in `data/sd/` and `data/mm/`:

```
data/sd/  → SalesOrderHeader.csv, SalesOrderDetail.csv, Customer.csv
data/mm/  → Product.csv, ProductInventory.csv, PurchaseOrderHeader.csv, PurchaseOrderDetail.csv
```

### 4. Load and clean the data
```bash
python -m src.data.loader
```

### 5. Ingest data into ChromaDB
```bash
python -m src.embeddings.ingest
```

### 6. Start all services
```bash
docker compose up --build
```

### 7. Access services

| Service   | URL                        |
|-----------|----------------------------|
| API       | http://localhost:8000      |
| API docs  | http://localhost:8000/docs |
| Dashboard | http://localhost:8501      |
| MLflow    | http://localhost:5000      |

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/query` | Natural language query — returns answer, sources, retrieval scores |
| `GET`  | `/health` | Health check |

---

## 📈 Possible Extensions

- Hybrid retrieval (BM25 + dense embeddings) for better recall
- Fine-tuned embedding model on ERP-specific terminology
- Role-based access control (RBAC) on the API
- Integration with real SAP systems via OData APIs
- Cloud deployment (AWS/GCP) with managed ChromaDB

---

## 👤 Author

Experienced IT professional with a background in development, cybersecurity, and ERP systems, with expertise in Industrial AI. Focused on building well-engineered AI systems with explainability, LLM integration, and MLOps practices.
