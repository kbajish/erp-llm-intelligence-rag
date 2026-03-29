import pandas as pd
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
log = logging.getLogger(__name__)

SD_DIR = Path("data/sd")
MM_DIR = Path("data/mm")


def row_to_text(row: pd.Series, table_name: str) -> str:
    """Convert a single DataFrame row to a human-readable text chunk."""
    fields = " | ".join([f"{col}: {val}" for col, val in row.items()])
    return f"[{table_name}] {fields}"


def chunk_table(df: pd.DataFrame, table_name: str) -> List[Dict]:
    """
    Table-aware chunking — each row becomes one chunk.
    Column names are preserved in every chunk so the retriever
    always knows what each value means.
    """
    chunks = []
    for _, row in df.iterrows():
        text = row_to_text(row, table_name)
        metadata = {
            "table":  table_name,
            "source": f"{table_name} record"
        }
        # Add key identifier to metadata for source citation
        if "order_id" in row:
            metadata["record_id"] = row["order_id"]
        elif "material_id" in row:
            metadata["record_id"] = row["material_id"]
        elif "customer_id" in row:
            metadata["record_id"] = row["customer_id"]
        elif "po_id" in row:
            metadata["record_id"] = row["po_id"]

        chunks.append({"text": text, "metadata": metadata})
    return chunks


def load_and_chunk_all() -> List[Dict]:
    log.info("Loading and chunking all ERP tables...")
    all_chunks = []

    tables = {
        "sales_orders":    SD_DIR / "sales_orders.csv",
        "customer_master": SD_DIR / "customer_master.csv",
        "material_master": MM_DIR / "material_master.csv",
        "stock_levels":    MM_DIR / "stock_levels.csv",
        "purchase_orders": MM_DIR / "purchase_orders.csv",
    }

    for table_name, path in tables.items():
        if not path.exists():
            log.warning(f"File not found: {path}")
            continue
        df     = pd.read_csv(path)
        chunks = chunk_table(df, table_name)
        all_chunks.extend(chunks)
        log.info(f"  {table_name}: {len(chunks)} chunks")

    log.info(f"Total chunks: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    chunks = load_and_chunk_all()
    print("\nSample chunk:")
    print(chunks[0]["text"])
    print("\nMetadata:", chunks[0]["metadata"])