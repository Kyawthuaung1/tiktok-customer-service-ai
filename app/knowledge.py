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


def product_name_in_query(query: str, product_name: str) -> bool:
    """
    Product retrieval must be conservative.

    We only consider a product matched when:
    - the complete product name appears in the query, or
    - all meaningful product-name tokens appear in the query.
    """

    q = normalize(query)
    name = normalize(product_name)

    if not q or not name:
        return False

    if name in q:
        return True

    query_words = set(
        re.findall(r"[a-z0-9]+", q)
    )

    name_words = [
        word
        for word in re.findall(
            r"[a-z0-9]+",
            name,
        )
        if len(word) >= 2
    ]

    if not name_words:
        return False

    return all(
        word in query_words
        for word in name_words
    )


def search_product(query: str):
    matches = []

    for item in _product_records(
        load_knowledge()["products"]
    ):
        if product_name_in_query(
            query,
            item["name"],
        ):
            matches.append({
                "type": "product",
                "score": 100,
                "name": item["name"],
                "data": item["data"],
            })

    return matches


def search_knowledge(query: str, limit: int = 5):
    knowledge = load_knowledge()

    q = normalize(query)

    if not q:
        return []

    results = []

    # -------------------------------------------------
    # PRODUCTS
    # -------------------------------------------------
    product_matches = search_product(q)

    if product_matches:
        return product_matches[:limit]

    # -------------------------------------------------
    # FAQ
    # -------------------------------------------------
    query_words = set(
        re.findall(r"[a-z0-9]+|[\u1000-\u109f]+", q)
    )

    for item in _faq_records(knowledge["faq"]):
        question = normalize(item["question"])

        score = 0

        if question == q:
            score = 100

        elif question in q:
            score = 80

        else:
            faq_words = set(
                re.findall(
                    r"[a-z0-9]+|[\u1000-\u109f]+",
                    question,
                )
            )

            common = query_words & faq_words

            if len(common) >= 2:
                score = len(common) * 10

        if score > 0:
            results.append({
                "type": "faq",
                "score": score,
                "question": item["question"],
                "answer": item["answer"],
            })

    # -------------------------------------------------
    # COMPANY
    # -------------------------------------------------
    for item in _company_records(
        knowledge["company"]
    ):
        field = normalize(item["field"])
        value = normalize(item["value"])

        score = 0

        if field and field in q:
            score = 20

        if score > 0:
            results.append({
                "type": "company",
                "score": score,
                "field": item["field"],
                "value": item["value"],
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:limit]
