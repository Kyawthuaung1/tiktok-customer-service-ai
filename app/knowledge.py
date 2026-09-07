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

    # Common punctuation becomes spaces.
    text = re.sub(
        r"[၊၊။,!?？!()\[\]{}:;\"'“”‘’\-_/]+",
        " ",
        text,
    )

    # Collapse whitespace.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


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


def _aliases(product: dict):
    aliases = product.get("aliases", [])

    if isinstance(aliases, str):
        aliases = [aliases]

    if not isinstance(aliases, list):
        return []

    return [
        str(alias).strip()
        for alias in aliases
        if str(alias).strip()
    ]


def _latin_tokens(text: str):
    return [
        token
        for token in re.findall(
            r"[a-z0-9]+",
            normalize(text),
        )
        if len(token) >= 2
    ]


def product_name_in_query(
    query: str,
    product_name: str,
    aliases=None,
) -> bool:
    """
    Conservative product matching.

    Match only when:
    1. Full product name appears, OR
    2. Full alias appears, OR
    3. All meaningful Latin/alphanumeric product-name
       tokens appear.

    Burmese product names are safely handled by
    exact normalized substring matching.
    """

    q = normalize(query)
    name = normalize(product_name)

    if not q or not name:
        return False

    # Exact full product name.
    if name in q:
        return True

    # Optional business-defined aliases.
    for alias in aliases or []:
        alias = normalize(alias)

        if alias and alias in q:
            return True

    # English / alphanumeric product names.
    name_words = _latin_tokens(name)

    if not name_words:
        return False

    query_words = set(_latin_tokens(q))

    return all(
        word in query_words
        for word in name_words
    )


def search_product(query: str):
    matches = []

    products = load_knowledge()["products"]

    for item in _product_records(products):
        product = item["data"]

        if product_name_in_query(
            query,
            item["name"],
            _aliases(product),
        ):
            matches.append({
                "type": "product",
                "score": 100,
                "name": item["name"],
                "data": product,
            })

    return matches


def search_knowledge(
    query: str,
    limit: int = 5,
):
    knowledge = load_knowledge()

    q = normalize(query)

    if not q:
        return []

    # -------------------------------------------------
    # PRODUCTS
    # -------------------------------------------------

    product_matches = search_product(q)

    # Product match has highest priority.
    # Never let FAQ/company matching replace a verified
    # product result.
    if product_matches:
        return product_matches[:limit]

    # -------------------------------------------------
    # FAQ
    # -------------------------------------------------

    results = []

    query_words = set(
        re.findall(
            r"[a-z0-9]+|[\u1000-\u109f]+",
            q,
        )
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

            # Conservative FAQ threshold.
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
