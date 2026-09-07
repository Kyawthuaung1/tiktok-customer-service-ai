import json
import re
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

    except (json.JSONDecodeError, OSError):
        print(f"[WARNING] Could not load JSON: {filename}")
        return {}


def load_knowledge():
    return {
        "company": load_json("company.json"),
        "products": load_json("products.json"),
        "faq": load_json("faq.json"),
    }


def normalize(text: str) -> str:
    text = str(text).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _product_records(products_data):
    products = products_data.get("products", [])

    if not isinstance(products, list):
        return []

    results = []

    for product in products:
        if not isinstance(product, dict):
            continue

        name = str(product.get("name", "")).strip()

        if not name:
            continue

        results.append({
            "type": "product",
            "name": name,
            "data": product,
        })

    return results


def _faq_records(faq_data):
    faq = faq_data.get("faq", [])

    if not isinstance(faq, list):
        return []

    results = []

    for item in faq:
        if not isinstance(item, dict):
            continue

        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()

        if not question:
            continue

        results.append({
            "type": "faq",
            "question": question,
            "answer": answer,
        })

    return results


def _company_records(company_data):
    if not isinstance(company_data, dict):
        return []

    results = []

    for key, value in company_data.items():
        if isinstance(value, (str, int, float)):
            results.append({
                "type": "company",
                "field": str(key),
                "value": str(value),
            })

    return results


def search_knowledge(query: str, limit: int = 5):
    knowledge = load_knowledge()

    q = normalize(query)

    if not q:
        return []

    scored = []

    # -----------------------------
    # Products
    # -----------------------------
    for item in _product_records(knowledge["products"]):
        name = normalize(item["name"])
        score = 0

        if q == name:
            score += 100

        if name in q:
            score += 80

        query_words = q.split()
        name_words = name.split()

        for word in name_words:
            if len(word) >= 2 and word in query_words:
                score += 20

        if score > 0:
            scored.append({
                "type": "product",
                "score": score,
                "name": item["name"],
                "data": item["data"],
            })

    # -----------------------------
    # FAQ
    # -----------------------------
    for item in _faq_records(knowledge["faq"]):
        question = normalize(item["question"])

        score = 0

        if q == question:
            score += 90

        if question in q:
            score += 60

        query_words = set(q.split())

        for word in question.split():
            if len(word) >= 2 and word in query_words:
                score += 10

        if score > 0:
            scored.append({
                "type": "faq",
                "score": score,
                "question": item["question"],
                "answer": item["answer"],
            })

    # -----------------------------
    # Company
    # -----------------------------
    for item in _company_records(knowledge["company"]):
        field = normalize(item["field"])
        value = normalize(item["value"])

        score = 0

        if field in q:
            score += 20

        if value and value in q:
            score += 30

        if score > 0:
            scored.append({
                "type": "company",
                "score": score,
                "field": item["field"],
                "value": item["value"],
            })

    scored.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored[:limit]


def find_product(product_name: str):
    query = normalize(product_name)

    for item in _product_records(
        load_knowledge()["products"]
    ):
        if normalize(item["name"]) == query:
            return item["data"]

    for item in _product_records(
        load_knowledge()["products"]
    ):
        name = normalize(item["name"])

        if name in query or query in name:
            return item["data"]

    return None
