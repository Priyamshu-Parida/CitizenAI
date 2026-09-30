import chromadb
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

SCHEME_ALIASES = {
    "pm vishwakarma": ["pm vishwakarma", "vishwakarma"],
    "pm kisan": ["pm kisan", "pm-kisan", "pmkisan"],
    "pmfby": ["pmfby", "pm fasal bima yojana", "fasal bima"],
    "pmegp": ["pmegp", "prime minister employment generation programme"],
    "pmfme": ["pmfme", "pm formalisation of micro food processing enterprises"],
    "agriculture infrastructure fund": [
        "agriculture infrastructure fund",
        "agri infrastructure fund",
        "aif"
    ],
    "pmay u": ["pmay-u", "pmay u", "pmay urban", "pmay-u 2.0"],
    "pm svanidhi": ["pm svanidhi", "pmsvanidhi"],
    "nmsa": ["nmsa", "national mission for sustainable agriculture"],
    "day nulm": ["day-nulm", "day nulm", "national urban livelihoods mission"]
}

def detect_scheme(query):
    query_lower = query.lower()

    for scheme, aliases in SCHEME_ALIASES.items():
        for alias in aliases:
            if alias in query_lower:
                return scheme

    return None


VECTOR_DB = "vector_db"
COLLECTION_NAME = "citizenai"

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=VECTOR_DB)
collection = client.get_collection(COLLECTION_NAME)

data = collection.get(
    include=["documents", "metadatas"]
)

texts = data["documents"]
metadatas = data["metadatas"]

tokenized_texts = [
    text.lower().split()
    for text in texts
]

bm25 = BM25Okapi(tokenized_texts)


def hybrid_search(query, top_k=3):

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )[0].tolist()

    semantic_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 5
    )

    semantic_ids = semantic_results["ids"][0]

    id_to_index = {
        doc_id: index
        for index, doc_id in enumerate(data["ids"])
    }

    semantic_ranks = {}

    for rank, doc_id in enumerate(semantic_ids):
        semantic_ranks[doc_id] = rank + 1

    tokenized_query = query.lower().split()

    bm25_scores = bm25.get_scores(tokenized_query)

    keyword_indices = sorted(
        range(len(bm25_scores)),
        key=lambda i: bm25_scores[i],
        reverse=True
    )[:top_k * 5]

    keyword_ranks = {}

    for rank, index in enumerate(keyword_indices):
        doc_id = data["ids"][index]
        keyword_ranks[doc_id] = rank + 1

    all_ids = set(semantic_ranks) | set(keyword_ranks)

    rrf_scores = {}

    query_lower = query.lower()
    detected_scheme = detect_scheme(query)

    for doc_id in all_ids:
        score = 0

        if doc_id in semantic_ranks:
            score += 1 / (60 + semantic_ranks[doc_id])

        if doc_id in keyword_ranks:
            score += 1 / (60 + keyword_ranks[doc_id])

        index = id_to_index[doc_id]

        scheme = metadatas[index]["scheme"].lower()
        source = metadatas[index]["source"].lower()

        if detected_scheme:

            normalized_scheme = scheme.replace("_", " ").replace("-", " ")

            if detected_scheme in normalized_scheme:
                score += 0.15

        if source.replace(".pdf", "").replace("_", " ") in query_lower:
            score += 0.03

        query_words = [
            word for word in query_lower.split()
            if len(word) > 3
        ]

        text_lower = texts[index].lower()

        important_matches = sum(
            1 for word in query_words
            if word in text_lower
        )

        score += min(important_matches * 0.005, 0.02)

        rrf_scores[doc_id] = score

    ranked_ids = sorted(
        rrf_scores,
        key=rrf_scores.get,
        reverse=True
    )[:top_k]

    results = []

    for doc_id in ranked_ids:

        index = id_to_index[doc_id]

        results.append({
            "text": texts[index],
            "page": metadatas[index]["page"],
            "source": metadatas[index]["source"],
            "scheme": metadatas[index]["scheme"]
        })

    return results


if __name__ == "__main__":

    query = input("Enter your query: ")

    results = hybrid_search(query)

    print("\nHybrid Search Results:\n")

    for i, result in enumerate(results, start=1):

        print(f"Result {i}")
        print(f"Scheme: {result['scheme']}")
        print(f"Source: {result['source']}")
        print(f"Page: {result['page']}")
        print(f"Text: {result['text'][:500]}")
        print("-" * 80)
