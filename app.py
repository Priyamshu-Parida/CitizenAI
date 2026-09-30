import streamlit as st
from src.llm import generate_answer
from src.comparison import compare_schemes


st.set_page_config(
    page_title="CitizenAI",
    page_icon="🇮🇳",
    layout="wide"
)


st.title("🇮🇳 CitizenAI")
st.subheader("Smart Government Scheme Discovery & Comparison Assistant")

st.write(
    "Ask questions about Indian government schemes and get "
    "grounded answers from official government documents."
)

st.divider()


st.subheader("🔎 Ask About Government Schemes")

st.write(
    "Search the available government scheme documents using natural language."
)

with st.form("search_form"):

    question = st.text_input(
        "Your question",
        placeholder="Example: What benefits are provided under PM Vishwakarma?"
    )

    ask_button = st.form_submit_button(
        "Ask CitizenAI",
        type="primary"
    )


if ask_button and question:

    with st.spinner("Searching government documents and generating answer..."):

        try:
            answer, sources = generate_answer(question)

            st.subheader("🤖 CitizenAI Answer")

            st.write(answer)

            st.divider()

            st.subheader("📚 Relevant Government Information")

            for i, source in enumerate(sources, start=1):

                with st.expander(
                    f"Source {i} — {source['scheme']} | Page {source['page']}"
                ):

                    st.write(source["text"])

            st.divider()

            st.subheader("📖 References")

            seen = set()

            for source in sources:

                reference = (
                    source["source"],
                    source["page"]
                )

                if reference not in seen:

                    st.write(
                        f"- {source['scheme']} — "
                        f"{source['source']} — "
                        f"Page {source['page']}"
                    )

                    seen.add(reference)

        except Exception:

            st.error(
                "The AI service is temporarily unavailable. "
                "Please try again in a moment."
            )

st.divider()

st.subheader("📚 Available Government Schemes")

st.write(
    "CitizenAI currently uses official government documents covering "
    "the following schemes:"
)

scheme_names = [
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

st.write(" • ".join(scheme_names))

st.divider()

st.subheader("🔄 Compare Government Schemes")

scheme_names = [
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

col1, col2 = st.columns(2)

with col1:
    scheme1 = st.selectbox(
        "Select Scheme 1",
        scheme_names,
        index=0
    )

with col2:
    scheme2 = st.selectbox(
        "Select Scheme 2",
        scheme_names,
        index=3
    )

if st.button("Compare Schemes", type="primary"):

    if scheme1 == scheme2:
        st.warning("Please select two different schemes.")

    else:

        with st.spinner("Comparing government schemes..."):

            try:
                comparison, comparison_sources = compare_schemes(
                    scheme1,
                    scheme2
                )

                st.subheader("📊 Scheme Comparison")

                comparison_table = {
                    "Aspect": [
                        "Purpose",
                        "Target beneficiaries",
                        "Major benefits",
                        "Financial or other support",
                        "Key features"
                    ],
                    scheme1: [
                        comparison["purpose"]["scheme1"],
                        comparison["target_beneficiaries"]["scheme1"],
                        comparison["major_benefits"]["scheme1"],
                        comparison["financial_support"]["scheme1"],
                        comparison["key_features"]["scheme1"]
                    ],
                    scheme2: [
                        comparison["purpose"]["scheme2"],
                        comparison["target_beneficiaries"]["scheme2"],
                        comparison["major_benefits"]["scheme2"],
                        comparison["financial_support"]["scheme2"],
                        comparison["key_features"]["scheme2"]
                    ]
                }

                st.table(comparison_table)
    
                st.subheader("📚 Comparison Sources")

                seen = set()

                for source in comparison_sources:

                    reference = (
                        source["source"],
                        source["page"]
                    )

                    if reference not in seen:

                        st.write(
                            f"- {source['scheme']} — "
                            f"{source['source']} — "
                            f"Page {source['page']}"
                        )

                        seen.add(reference)

            except Exception:

                st.error(
                    "Unable to compare the selected schemes. "
                    "Please try again."
                )