def test_chunker_imports():
    from src.chunking.chunker import load_and_chunk_all, chunk_table
    assert callable(load_and_chunk_all)
    assert callable(chunk_table)

def test_prompt_imports():
    from src.llm.prompts import ERP_RAG_PROMPT, SUMMARY_PROMPT
    assert ERP_RAG_PROMPT is not None
    assert SUMMARY_PROMPT is not None

def test_rag_chain_imports():
    from src.rag.chain import build_context, retrieve
    assert callable(build_context)
    assert callable(retrieve)

def test_mitre_style_mapping():
    from src.chunking.chunker import row_to_text
    import pandas as pd
    row = pd.Series({
        "material_id": "MAT-000001",
        "description": "Test material",
        "current_stock": 50
    })
    text = row_to_text(row, "stock_levels")
    assert "MAT-000001" in text
    assert "stock_levels" in text