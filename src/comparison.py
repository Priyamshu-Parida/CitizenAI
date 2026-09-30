from groq import Groq
import os
import json

from dotenv import load_dotenv
from .hybrid_retriever import hybrid_search

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)


SCHEMES = {
    "PM Vishwakarma": "PM Vishwakarma",
    "PM-KISAN": "PM Kisan",
    "PMFBY": "PMFBY",
    "PMEGP": "PMEGP",
    "PMFME": "PMFME",
    "Agriculture Infrastructure Fund": "Agriculture Infrastructure Fund",
    "PMAY-U": "PMAY U",
    "PM SVANidhi": "PM SVANIDHI",
    "NMSA": "NMSA",
    "DAY-NULM": "DAY NULM"
}


def get_scheme_context(scheme):

    query = (
        f"{SCHEMES[scheme]} purpose benefits "
        "financial support components target beneficiaries"
    )

    results = hybrid_search(query, top_k=10)

    scheme_results = []
    seen = set()

    search_name = SCHEMES[scheme].lower()

    for result in results:
        result_scheme = result["scheme"].lower()

        if search_name in result_scheme or result_scheme in search_name:
            key = (result["source"], result["page"])

            if key not in seen:
                scheme_results.append(result)
                seen.add(key)

    return scheme_results[:4]


def compare_schemes(scheme1, scheme2):

    results1 = get_scheme_context(scheme1)
    results2 = get_scheme_context(scheme2)

    context_parts = []

    context_parts.append(f"INFORMATION FOR {scheme1}:\n")

    for result in results1:
        context_parts.append(
            f"""
Document: {result['source']}
Page: {result['page']}

{result['text']}
"""
        )

    context_parts.append(f"\nINFORMATION FOR {scheme2}:\n")

    for result in results2:
        context_parts.append(
            f"""
Document: {result['source']}
Page: {result['page']}

{result['text']}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are CitizenAI, a government scheme comparison assistant.

Compare these two Indian government schemes:

Scheme 1: {scheme1}
Scheme 2: {scheme2}

Use ONLY the government document information provided below.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
  "purpose": {{
    "scheme1": "...",
    "scheme2": "..."
  }},
  "target_beneficiaries": {{
    "scheme1": "...",
    "scheme2": "..."
  }},
  "major_benefits": {{
    "scheme1": "...",
    "scheme2": "..."
  }},
  "financial_support": {{
    "scheme1": "...",
    "scheme2": "..."
  }},
  "key_features": {{
    "scheme1": "...",
    "scheme2": "..."
  }}
}}

Rules:
- Keep every value short and concise.
- Each value must be ONE paragraph.
- Do not use bullet points.
- Do not use Markdown.
- Do not use HTML.
- Do not use newline characters inside values.
- Do not use the | character.
- Mention relevant document page numbers.
- Do not invent facts.
- Do not use outside knowledge.
- If information is unavailable, write:
  "Not specified in the provided documents."
- Do not make personalized eligibility decisions.
- Do not state which scheme is better.

Government document information:

{context}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    answer = response.choices[0].message.content.strip()

    if answer.startswith("```"):
        answer = answer.replace("```json", "").replace("```", "").strip()

    comparison_data = json.loads(answer)

    sources = results1 + results2

    return comparison_data, sources
