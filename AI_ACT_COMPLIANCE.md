# EU AI Act & DSGVO Compliance Notes

## Risk classification
This system provides AI-generated responses based on retrieved ERP data.
It is intended as a decision-support tool, not an autonomous decision-maker.
Under the EU AI Act, this system is classified as limited risk.

## Transparency measures
- Users are informed they are interacting with an AI system
- Every answer includes retrieved source records so users can verify responses
- The system does not store personal data — synthetic data only

## Data handling
- No real employee, customer, or financial data is used
- All data is synthetically generated for demonstration purposes
- ChromaDB stores only document embeddings and metadata

## Model governance
- Retrieval quality metrics (MRR, Recall@5) are tracked via MLflow
- Prompt templates are versioned in src/llm/prompts.py