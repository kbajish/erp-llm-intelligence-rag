import streamlit as st
import requests
import pandas as pd
from pathlib import Path

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title = "ERP LLM Intelligence",
    page_icon  = "🤖",
    layout     = "wide"
)

st.title("🤖 ERP LLM Intelligence — RAG Dashboard")
st.caption("Natural language querying of SAP SD and MM data")

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("Quick Queries")
    st.caption("Click to run a sample query:")

    sample_queries = [
        "Which materials are below safety stock?",
        "What is the total revenue from sales orders?",
        "Show me the top customers by order value.",
        "Which purchase orders are still open?",
        "What materials need reordering?",
        "Show revenue by region.",
    ]

    for q in sample_queries:
        if st.button(q, use_container_width=True):
            st.session_state["query_input"] = q

    st.markdown("---")
    if st.button("Check API health"):
        try:
            r = requests.get(f"{API_URL}/health", timeout=3)
            st.success(f"API online — {r.json()}")
        except Exception:
            st.error("API not reachable")

# ── Key metrics ───────────────────────────────────────────────────
try:
    sd_orders   = pd.read_csv("data/sd/sales_orders.csv")
    mm_stock    = pd.read_csv("data/mm/stock_levels.csv")
    mm_po       = pd.read_csv("data/mm/purchase_orders.csv")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total sales orders",   len(sd_orders))
    col2.metric("Total revenue (EUR)",  f"{sd_orders['total_value'].sum():,.0f}")
    col3.metric("Materials below safety stock", int(mm_stock["below_safety"].sum()))
    col4.metric("Open purchase orders", len(mm_po[mm_po["status"] == "Open"]))
except Exception:
    st.warning("Could not load ERP data for metrics — run the data generator first.")

st.markdown("---")

# ── Chat interface ─────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display conversation history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Query input
query = st.chat_input(
    "Ask a question about your ERP data...",
)

# Handle sidebar quick query
if "query_input" in st.session_state and st.session_state["query_input"]:
    query = st.session_state.pop("query_input")

if query:
    # Show user message
    with st.chat_message("user"):
        st.write(query)
    st.session_state["messages"].append({"role": "user", "content": query})

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Retrieving from ERP data..."):
            try:
                resp   = requests.post(
                    f"{API_URL}/query",
                    json    = {"question": query},
                    timeout = 60
                )
                result = resp.json()
                answer  = result.get("answer", "No answer returned.")
                sources = result.get("sources", [])

                st.write(answer)
                st.session_state["messages"].append({
                    "role":    "assistant",
                    "content": answer
                })

                # Show sources
                if sources:
                    with st.expander(f"Retrieved sources ({len(sources)} records)"):
                        for s in sources:
                            st.markdown(
                                f"**{s['record_id']}** — `{s['table']}` "
                                f"(relevance: {s['relevance']:.3f})"
                            )
                            st.caption(s["text"])
                            st.divider()

                # Auto chart for revenue/stock queries
                if "revenue" in query.lower() or "region" in query.lower():
                    try:
                        chart_data = sd_orders.groupby("region")["total_value"].sum().reset_index()
                        chart_data.columns = ["Region", "Revenue (EUR)"]
                        st.bar_chart(chart_data.set_index("Region"))
                    except Exception:
                        pass

                if "stock" in query.lower() or "safety" in query.lower():
                    try:
                        below = mm_stock[mm_stock["below_safety"] == True][
                            ["material_id", "current_stock", "safety_stock"]
                        ].head(10)
                        if not below.empty:
                            st.bar_chart(below.set_index("material_id"))
                    except Exception:
                        pass

            except Exception as e:
                st.error(f"API error: {str(e)}")

# ── Clear conversation ─────────────────────────────────────────────
if st.session_state["messages"]:
    if st.button("Clear conversation"):
        st.session_state["messages"] = []
        st.rerun()