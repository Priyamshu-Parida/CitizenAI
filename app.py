import html

import streamlit as st
from src.llm import generate_answer
from src.comparison import compare_schemes


st.set_page_config(
    page_title="CitizenAI",
    page_icon="🇮🇳",
    layout="wide"
)


# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------

SCHEME_NAMES = [
    "PM Vishwakarma",
    "PM-KISAN",
    "PMFBY",
    "PMEGP",
    "PMFME",
    "Agriculture Infrastructure Fund",
    "PMAY-U",
    "PM SVANidhi",
    "NMSA",
    "DAY-NULM"
]

EXAMPLE_QUESTIONS = [
    "What benefits are provided under PM Vishwakarma?",
    "Which scheme supports street vendors?",
    "What financial assistance is available for farmers?",
    "What is the purpose of PMAY-U?"
]

COMPARISON_ROWS = [
    ("Purpose", "purpose"),
    ("Target beneficiaries", "target_beneficiaries"),
    ("Major benefits", "major_benefits"),
    ("Financial or other support", "financial_support"),
    ("Key features", "key_features")
]

HOW_IT_WORKS = [
    ("Official Documents",
     "Government scheme PDFs form the knowledge base."),
    ("Hybrid Search",
     "Semantic search and BM25 keyword search are combined."),
    ("Relevant Passages",
     "The best matching passages are selected."),
    ("Groq AI",
     "The language model reads only those passages."),
    ("Answer + Sources",
     "The answer is shown with document and page references.")
]


# ------------------------------------------------------------------
# Styling (small, controlled CSS block)
# ------------------------------------------------------------------

def compact(markup):
    """Remove line breaks and indentation so Markdown never treats the
    HTML as a code block."""
    return " ".join(line.strip() for line in markup.splitlines() if line.strip())


CSS = compact("""
<style>
.block-container, [data-testid="stMainBlockContainer"] {
    max-width: 1100px;
    padding-top: 4.5rem;
    padding-bottom: 3rem;
}
footer { visibility: hidden; }

button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-primaryFormSubmit"] {
    background-color: #4F46E5;
    border-color: #4F46E5;
    color: #FFFFFF;
}
button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background-color: #4338CA;
    border-color: #4338CA;
    color: #FFFFFF;
}

.ca-hero {
    border: 1px solid #E0E7FF;
    border-radius: 16px;
    background: linear-gradient(135deg, #EEF2FF 0%, #FFFFFF 70%);
    padding: 0 0 1.6rem 0;
    overflow: hidden;
    margin-bottom: 1rem;
}
.ca-flag {
    height: 5px;
    background: linear-gradient(90deg, #FF9933 0 33.33%, #E5E7EB 33.33% 66.66%, #138808 66.66% 100%);
    margin-bottom: 1.4rem;
}
.ca-hero-body { padding: 0 2rem; }
.ca-badge {
    display: inline-block;
    background: #FFFFFF;
    border: 1px solid #C7D2FE;
    color: #4338CA;
    border-radius: 999px;
    padding: 0.2rem 0.85rem;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.ca-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #312E81;
    line-height: 1.15;
    margin: 0.7rem 0 0.2rem 0;
}
.ca-sub {
    font-size: 1.2rem;
    font-weight: 600;
    color: #1F2937;
    margin-bottom: 0.5rem;
}
.ca-desc {
    font-size: 1rem;
    color: #4B5563;
    max-width: 720px;
    margin: 0;
}

.ca-stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}
.ca-stat {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 0.7rem 1rem;
}
.ca-stat b { display: block; color: #4338CA; font-size: 1.05rem; }
.ca-stat span { color: #6B7280; font-size: 0.85rem; }

.ca-h2 {
    font-size: 1.4rem;
    font-weight: 700;
    color: inherit;
    margin: 2rem 0 0.2rem 0;
    padding-bottom: 0.35rem;
    border-bottom: 2px solid rgba(79, 70, 229, 0.25);
}
.ca-h2sub {
    font-size: 0.95rem;
    opacity: 0.7;
    margin: 0.3rem 0 0.8rem 0;
}

.ca-meta { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-bottom: 0.6rem; }
.ca-meta div {
    background: #F5F3FF;
    border: 1px solid #E0E7FF;
    border-radius: 8px;
    padding: 0.3rem 0.7rem;
    font-size: 0.85rem;
    color: #1F2937;
}
.ca-meta span {
    display: block;
    color: #6B7280;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.ca-src {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.4rem 0.9rem;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-left: 4px solid #4F46E5;
    border-radius: 10px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
}
.ca-src .scheme { font-weight: 700; color: #1F2937; }
.ca-src .doc { color: #6B7280; font-size: 0.9rem; word-break: break-all; }
.ca-src .page {
    margin-left: auto;
    background: #EEF2FF;
    color: #4338CA;
    border-radius: 999px;
    padding: 0.15rem 0.7rem;
    font-weight: 700;
    font-size: 0.8rem;
    white-space: nowrap;
}

.ca-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.75rem;
}
.ca-scheme {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-top: 3px solid #4F46E5;
    border-radius: 12px;
    padding: 0.8rem 1rem;
}
.ca-scheme span {
    display: block;
    color: #6366F1;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}
.ca-scheme b { color: #1F2937; font-size: 1rem; }

.ca-table-wrap {
    overflow-x: auto;
    margin-bottom: 1rem;
    border: 1px solid #C7D2FE;
    border-radius: 12px;
    background: #FFFFFF;
}
.ca-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    table-layout: fixed;
    background: #FFFFFF;
    font-size: 0.93rem;
}
.ca-table th:first-child { width: 18%; }
.ca-table th:nth-child(2), .ca-table th:nth-child(3) { width: 41%; }
.ca-table th {
    background: #4F46E5;
    color: #FFFFFF;
    text-align: left;
    padding: 0.7rem 0.9rem;
    font-weight: 700;
}
.ca-table td {
    color: #1F2937;
    padding: 0.7rem 0.9rem;
    vertical-align: top;
    border-top: 1px solid #E5E7EB;
    line-height: 1.5;
}
.ca-table td.aspect { background: #F5F3FF; color: #3730A3; font-weight: 700; }
.ca-table td { word-wrap: break-word; overflow-wrap: anywhere; }
.ca-table tr:nth-child(even) td:not(.aspect) { background: #F9FAFB; }
.ca-table ul { margin: 0; padding-left: 1.1rem; }

.ca-steps { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem; }
.ca-step {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 0.9rem;
}
.ca-step .num {
    display: inline-block;
    width: 1.7rem;
    height: 1.7rem;
    line-height: 1.7rem;
    text-align: center;
    border-radius: 50%;
    background: #4F46E5;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
}
.ca-step b { display: block; color: #1F2937; margin-bottom: 0.25rem; }
.ca-step p { color: #4B5563; font-size: 0.85rem; margin: 0; }

.ca-note {
    background: #FEF9C3;
    border-left: 4px solid #F59E0B;
    color: #78350F;
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    font-size: 0.88rem;
    margin-top: 0.9rem;
}

.ca-footer {
    text-align: center;
    margin-top: 2.5rem;
    padding-top: 1.2rem;
    border-top: 1px solid rgba(128, 128, 128, 0.3);
    font-size: 0.85rem;
    opacity: 0.8;
    line-height: 1.6;
}

@media (max-width: 900px) {
    .ca-grid { grid-template-columns: repeat(2, 1fr); }
    .ca-steps { grid-template-columns: repeat(2, 1fr); }
    .ca-stats { grid-template-columns: 1fr; }
    .ca-title { font-size: 2rem; }
}
</style>
""")

st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------
# Small UI helpers (presentation only)
# ------------------------------------------------------------------

def esc(value):
    return html.escape(str(value))


def section_header(title, subtitle=None):
    markup = f'<div class="ca-h2">{esc(title)}</div>'
    if subtitle:
        markup += f'<div class="ca-h2sub">{esc(subtitle)}</div>'
    st.markdown(compact(markup), unsafe_allow_html=True)


def render_references(sources):
    """Show each unique (document, page) once, same de-duplication as before."""
    seen = set()
    rows = []

    for source in sources:
        reference = (source["source"], source["page"])

        if reference not in seen:
            rows.append(
                '<div class="ca-src">'
                f'<span class="scheme">{esc(source["scheme"])}</span>'
                f'<span class="doc">{esc(source["source"])}</span>'
                f'<span class="page">Page {esc(source["page"])}</span>'
                '</div>'
            )
            seen.add(reference)

    st.markdown("".join(rows), unsafe_allow_html=True)


def format_cell(value):
    if value is None:
        return "&mdash;"
    if isinstance(value, (list, tuple)):
        items = "".join(f"<li>{esc(item)}</li>" for item in value)
        return f"<ul>{items}</ul>"
    return esc(value).replace("\n", "<br>")


def render_comparison_table(scheme_a, scheme_b, comparison):
    body = ""

    for label, key in COMPARISON_ROWS:
        body += (
            "<tr>"
            f'<td class="aspect">{esc(label)}</td>'
            f'<td>{format_cell(comparison[key]["scheme1"])}</td>'
            f'<td>{format_cell(comparison[key]["scheme2"])}</td>'
            "</tr>"
        )

    table = (
        '<div class="ca-table-wrap"><table class="ca-table">'
        f"<thead><tr><th>Aspect</th><th>{esc(scheme_a)}</th>"
        f"<th>{esc(scheme_b)}</th></tr></thead>"
        f"<tbody>{body}</tbody></table></div>"
    )
    st.markdown(table, unsafe_allow_html=True)


def use_example(example):
    """Button callback: fill the search box and ask for a search on next run."""
    st.session_state["question_input"] = example
    st.session_state["run_example"] = True


# ------------------------------------------------------------------
# Hero
# ------------------------------------------------------------------

st.markdown(
    compact(f"""
    <div class="ca-hero">
        <div class="ca-flag"></div>
        <div class="ca-hero-body">
            <span class="ca-badge">Hybrid RAG &bull; Official Documents &bull; Source-Grounded Answers</span>
            <div class="ca-title">CitizenAI</div>
            <div class="ca-sub">Smart Government Scheme Discovery &amp; Comparison Assistant</div>
            <p class="ca-desc">Explore and compare Indian government schemes using
            AI-powered search grounded in official government documents.</p>
        </div>
    </div>
    <div class="ca-stats">
        <div class="ca-stat"><b>{len(SCHEME_NAMES)} schemes</b><span>Supported government schemes</span></div>
        <div class="ca-stat"><b>Hybrid search</b><span>Semantic search + BM25 keyword search</span></div>
        <div class="ca-stat"><b>Traceable</b><span>Answers shown with document and page references</span></div>
    </div>
    """),
    unsafe_allow_html=True
)


# ------------------------------------------------------------------
# Search
# ------------------------------------------------------------------

section_header(
    "Ask CitizenAI",
    "Search the available government scheme documents using natural language."
)

st.caption("Try an example question:")

example_cols = st.columns(2)

for i, example in enumerate(EXAMPLE_QUESTIONS):
    with example_cols[i % 2]:
        st.button(
            example,
            key=f"example_{i}",
            on_click=use_example,
            args=(example,),
            use_container_width=True
        )

with st.form("search_form"):

    question = st.text_input(
        "Your question",
        key="question_input",
        placeholder="Example: What benefits are provided under PM Vishwakarma?",
        label_visibility="collapsed"
    )

    ask_button = st.form_submit_button(
        "Ask CitizenAI",
        type="primary"
    )

run_example = st.session_state.pop("run_example", False)

if ask_button or run_example:

    if not question.strip():
        st.warning("Please type a question about a government scheme.")

    else:

        with st.spinner("Searching government documents and generating answer..."):

            try:
                answer, sources = generate_answer(question)

                st.session_state["qa_result"] = {
                    "question": question,
                    "answer": answer,
                    "sources": sources
                }

            except Exception:

                st.session_state.pop("qa_result", None)

                st.error(
                    "The AI service is temporarily unavailable. "
                    "Please try again in a moment."
                )


# ------------------------------------------------------------------
# Results
# ------------------------------------------------------------------

qa_result = st.session_state.get("qa_result")

if qa_result:

    try:
        section_header(
            "AI Answer",
            "Generated from the retrieved government-document passages shown below."
        )

        with st.container(border=True):
            st.caption(f"Question: {qa_result['question']}")
            st.markdown(qa_result["answer"])

        section_header(
            "Retrieved Government Information",
            "Open a passage to read the original text used for the answer."
        )

        for i, source in enumerate(qa_result["sources"], start=1):

            with st.expander(
                f"Source {i} — {source['scheme']} | Page {source['page']}",
                expanded=(i == 1)
            ):
                st.markdown(
                    compact(f"""
                    <div class="ca-meta">
                        <div><span>Scheme</span>{esc(source['scheme'])}</div>
                        <div><span>Document</span>{esc(source['source'])}</div>
                        <div><span>Page</span>{esc(source['page'])}</div>
                    </div>
                    """),
                    unsafe_allow_html=True
                )

                st.write(source["text"])

        section_header(
            "Sources",
            "Documents and pages of the passages used for this answer."
        )

        render_references(qa_result["sources"])

    except Exception:

        st.error(
            "The AI service is temporarily unavailable. "
            "Please try again in a moment."
        )


# ------------------------------------------------------------------
# Scheme explorer
# ------------------------------------------------------------------

section_header(
    "Explore Supported Schemes",
    "CitizenAI currently uses official government documents covering these schemes."
)

cards = "".join(
    f'<div class="ca-scheme"><span>{i:02d}</span><b>{esc(name)}</b></div>'
    for i, name in enumerate(SCHEME_NAMES, start=1)
)

st.markdown(f'<div class="ca-grid">{cards}</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------
# Comparison
# ------------------------------------------------------------------

section_header(
    "Compare Government Schemes",
    "Compare two supported schemes using information retrieved from "
    "official government documents."
)

with st.container(border=True):

    col1, col2 = st.columns(2)

    with col1:
        scheme1 = st.selectbox(
            "Scheme 1",
            SCHEME_NAMES,
            index=0
        )

    with col2:
        scheme2 = st.selectbox(
            "Scheme 2",
            SCHEME_NAMES,
            index=3
        )

    compare_button = st.button("Compare Schemes", type="primary")

if compare_button:

    if scheme1 == scheme2:
        st.session_state.pop("cmp_result", None)
        st.warning("Please select two different schemes.")

    else:

        with st.spinner("Comparing government schemes..."):

            try:
                comparison, comparison_sources = compare_schemes(
                    scheme1,
                    scheme2
                )

                st.session_state["cmp_result"] = {
                    "scheme1": scheme1,
                    "scheme2": scheme2,
                    "comparison": comparison,
                    "sources": comparison_sources
                }

            except Exception:

                st.session_state.pop("cmp_result", None)

                st.error(
                    "Unable to compare the selected schemes. "
                    "Please try again."
                )

cmp_result = st.session_state.get("cmp_result")

if cmp_result:

    try:
        section_header(
            "Scheme Comparison",
            f"{cmp_result['scheme1']} vs {cmp_result['scheme2']}"
        )

        render_comparison_table(
            cmp_result["scheme1"],
            cmp_result["scheme2"],
            cmp_result["comparison"]
        )

        section_header(
            "Comparison Sources",
            "Documents and pages used to build this comparison."
        )

        render_references(cmp_result["sources"])

    except Exception:

        st.error(
            "Unable to compare the selected schemes. "
            "Please try again."
        )


# ------------------------------------------------------------------
# How CitizenAI works
# ------------------------------------------------------------------

section_header(
    "How CitizenAI Works",
    "From official documents to a source-grounded answer."
)

steps = "".join(
    f'<div class="ca-step"><span class="num">{i}</span>'
    f"<b>{esc(title)}</b><p>{esc(text)}</p></div>"
    for i, (title, text) in enumerate(HOW_IT_WORKS, start=1)
)

st.markdown(
    compact(f"""
    <div class="ca-steps">{steps}</div>
    <div class="ca-note">CitizenAI is an information aid. Answers depend on the
    passages retrieved and may be incomplete, so please verify details in the
    official documents. It does not make personal eligibility decisions.</div>
    """),
    unsafe_allow_html=True
)


# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------

st.markdown(
    compact("""
    <div class="ca-footer">
        <b>CitizenAI</b> &middot; Hybrid RAG Government Scheme Assistant<br>
        Built as a Generative AI / RAG academic project. It is not an official government service.<br>
        Information is based on the government documents included in the knowledge base.
    </div>
    """),
    unsafe_allow_html=True
)