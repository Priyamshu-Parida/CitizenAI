import os
from dotenv import load_dotenv
from groq import Groq

from .hybrid_retriever import hybrid_search

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=api_key)


def generate_answer(question):

    results = hybrid_search(question)

    unique_results = []
    seen = set()

    for result in results:
        key = (result["source"], result["page"])

        if key not in seen:
            unique_results.append(result)
            seen.add(key)

    results = unique_results[:3]

    context_parts = []

    for i, result in enumerate(results, start=1):
        context_parts.append(
            f"""
            Source {i}
            Scheme: {result['scheme']}
            Document: {result['source']}
            Page: {result['page']}

            Content:
            {result['text']}
            """
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are CitizenAI, a government scheme information assistant.

Answer the user's question using ONLY the government document
information provided in the context below.

Important rules:

1. Do not invent facts.
2. Do not use outside knowledge.
3. If the provided context does not contain enough information,
   clearly say that the available documents do not provide enough
   information.
4. Give a clear and concise answer.
5. Mention the relevant scheme name when appropriate.
6. Do not make personalized eligibility decisions.
7. Do not claim that a citizen is definitely eligible or ineligible.
8. At the end, provide the document name and page number used.

User question:
{question}

Government document context:
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

    answer = response.choices[0].message.content

    return answer, results