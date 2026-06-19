from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.extend([str(PROJECT_ROOT / "src"), str(REPO_ROOT)])

import streamlit as st

from aec_code_compliance_rag import build_assistant_from_paths

st.set_page_config(page_title="AEC Code Compliance RAG", page_icon="AI", layout="wide")

st.title("AEC Code Compliance RAG Assistant")
st.caption("Synthetic demo data. Not legal, code, or professional compliance advice.")

docs = sorted(
    [
        *(PROJECT_ROOT / "sample_data").glob("*.md"),
        *(PROJECT_ROOT / "sample_data").glob("*.pdf"),
    ]
)
assistant = build_assistant_from_paths(docs)
source_catalog = assistant.source_catalog()

question = st.text_input(
    "Ask a design-standard question",
    value="What clear width should be checked for high traffic accessible routes?",
)
k = st.slider("Retrieved sources", min_value=1, max_value=6, value=4)
filter_cols = st.columns(3)
jurisdictions = sorted({source["jurisdiction"] for source in source_catalog})
source_types = sorted({source["source_type"] for source in source_catalog})
selected_jurisdiction = filter_cols[0].selectbox("Jurisdiction", ["All", *jurisdictions])
selected_source_type = filter_cols[1].selectbox("Source type", ["All", *source_types])
include_superseded = filter_cols[2].checkbox("Include superseded", value=False)

source_filters: dict[str, str | bool] = {}
if selected_jurisdiction != "All":
    source_filters["jurisdiction"] = selected_jurisdiction
if selected_source_type != "All":
    source_filters["source_type"] = selected_source_type
if not include_superseded:
    source_filters["superseded"] = False

if st.button("Answer", type="primary") or question:
    result = assistant.answer(question, k=k, source_filters=source_filters or None)
    st.subheader("Grounded answer")
    st.write(result["answer"])
    source_status = result.get("source_status", {})
    if source_status.get("requires_review"):
        st.warning(source_status.get("note", "Retrieved sources require review."))
        with st.expander("Source status details"):
            st.json(source_status)
    st.caption(
        f"Retrieved {result['retrieval']['result_count']} chunks "
        f"from {result['retrieval'].get('filtered_corpus_size', len(assistant.chunks))} "
        f"eligible chunks (top score {result['retrieval'].get('top_score', 0)})."
    )
    st.subheader("Sources")
    for source in result["sources"]:
        title = (
            f"{source['citation_id']} | {source['heading']} | "
            f"{source['clause_id']} | score {source['score']}"
        )
        with st.expander(title):
            st.write(source["reference"])
            st.write(
                "Source: "
                f"`{source.get('title') or source['source']}` "
                f"({source.get('source_type', '')})"
            )
            st.write(f"Chunk: `{source['chunk_id']}`")
            st.write(f"Allowed use: `{source.get('allowed_use', '')}`")
            st.write(
                "Source status: "
                f"version `{source.get('document_version', '')}`, "
                f"jurisdiction `{source.get('jurisdiction', '')}`, "
                f"code year `{source.get('code_year', '')}`, "
                f"superseded `{source.get('superseded', False)}`"
            )
            if source["page"]:
                st.write(f"Page: {source['page']}")
            st.write(source["excerpt"])
