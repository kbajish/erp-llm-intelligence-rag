import pandas as pd
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(message)s")
log = logging.getLogger(__name__)

SD_DIR = Path("data/sd")
MM_DIR = Path("data/mm")


def row_to_text(row: pd.Series, table_name: str) -> str:
    fields = " | ".join([f"{col}: {val}" for col, val in row.items()])
    return f"[{table_name}] {fields}"


def chunk_table(df: pd.DataFrame, table_name: str,
                id_col: str = None) -> List[Dict]:
    chunks = []
    for _, row in df.iterrows():
        text     = row_to_text(row, table_name)
        metadata = {"table": table_name, "source": f"{table_name} record"}
        if id_col and id_col in row:
            metadata["record_id"] = str(row[id_col])
        chunks.append({"text": text, "metadata": metadata})
    return chunks


def load_and_chunk_all() -> List[Dict]:
    log.info("Loading and chunking AdventureWorks tables...")
    all_chunks = []

    tables = {
        "sales_orders":    (SD_DIR / "sales_orders_clean.csv",    "SalesOrderID"),
        "customer_master": (SD_DIR / "customer_master_clean.csv", "CustomerID"),
        "product_master":  (MM_DIR / "product_master_clean.csv",  "ProductID"),
        "stock_levels":    (MM_DIR / "stock_levels_clean.csv",    "ProductID"),
        "purchase_orders": (MM_DIR / "purchase_orders_clean.csv", "PurchaseOrderID"),
    }

    for table_name, (path, id_col) in tables.items():
        if not path.exists():
            log.warning(f"File not found: {path}")
            continue

        df = pd.read_csv(path)

        # Sample large tables to keep embedding manageable
        if len(df) > 2000:
            log.info(f"  Sampling {table_name} from {len(df)} to 2000 rows")
            df = df.sample(2000, random_state=42).reset_index(drop=True)

        chunks = chunk_table(df, table_name, id_col)
        all_chunks.extend(chunks)
        log.info(f"  {table_name}: {len(chunks)} chunks")

    log.info(f"Total chunks: {len(all_chunks)}")
    return all_chunks


if __name__ == "__main__":
    chunks = load_and_chunk_all()
    print("\nSample chunk:")
    print(chunks[0]["text"])
    print("\nMetadata:", chunks[0]["metadata"])