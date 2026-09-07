import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"


def load_json(filename: str):
    path = KNOWLEDGE_DIR / filename

    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            return {}

        return json.loads(content)

    except json.JSONDecodeError:
        print(f"[WARNING] Invalid JSON: {filename}")
        return {}


def load_knowledge():
    return {
        "company": load_json("company.json"),
        "products": load_json("products.json"),
        "faq": load_json("faq.json"),
    }


def search_knowledge(query: str):
    knowledge = load_knowledge()
    query_words = set(query.lower().split())

    results = []

    def walk(data, path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                walk(value, f"{path}.{key}" if path else key)

        elif isinstance(data, list):
            for index, value in enumerate(data):
                walk(value, f"{path}[{index}]")

        elif isinstance(data, str):
            text = data.lower()
            score = sum(
                1 for word in query_words
                if word and word in text
            )

            if score > 0:
                results.append({
                    "path": path,
                    "text": data,
                    "score": score,
                })

    walk(knowledge)

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:8]
