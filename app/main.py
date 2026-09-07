from .agent import CustomerServiceAgent, is_greeting


def print_context(context):
    print("\n-----------------------------------")
    print("[Agent Context]")
    print("Question:", context["question"])

    if not context["questions"]:
        print("\nNo questions detected.")

    for index, item in enumerate(
        context["questions"],
        start=1,
    ):
        print(f"\nQuestion {index}: {item['question']}")
        print("Intent:", item["intent"])

        if item["knowledge"]:
            print("Knowledge:")

            for knowledge in item["knowledge"]:
                if knowledge["type"] == "product":
                    data = knowledge["data"]

                    print(
                        f"  - Product: "
                        f"{data.get('name', '')}"
                    )
                    print(
                        f"    Price: "
                        f"{data.get('price', 'မရှိ')}"
                    )
                    print(
                        f"    Stock: "
                        f"{data.get('stock', 'မရှိ')}"
                    )

                elif knowledge["type"] == "faq":
                    print(
                        f"  - FAQ: "
                        f"{knowledge['question']}"
                    )
                    print(
                        f"    Answer: "
                        f"{knowledge['answer']}"
                    )

                elif knowledge["type"] == "company":
                    print(
                        f"  - "
                        f"{knowledge['field']}: "
                        f"{knowledge['value']}"
                    )

        else:
            print("Knowledge: None")

        print(
            "Needs human:",
            item["needs_human"],
        )

    print(
        "\nOverall needs human:",
        context["needs_human"],
    )

    print("-----------------------------------")


def product_reply(item):
    knowledge = item["knowledge"]

    if not knowledge:
        return (
            "ဒီ product အတွက် အတည်ပြုထားတဲ့ "
            "အချက်အလက် မရှိသေးပါရှင့်။"
        )

    product = None

    for result in knowledge:
        if result["type"] == "product":
            product = result["data"]
            break

    if not product:
        return (
            "ဒီ product အတွက် အတည်ပြုထားတဲ့ "
            "အချက်အလက် မရှိသေးပါရှင့်။"
        )

    name = product.get(
        "name",
        "ဒီပစ္စည်း",
    )

    if item["intent"] == "product_price":
        price = product.get("price")

        if not price:
            return (
                f"{name} ရဲ့ ဈေးနှုန်းကို "
                "အတည်ပြုထားတဲ့ information မရှိသေးပါရှင့်။"
            )

        return (
            f"{name} ရဲ့ ဈေးနှုန်းက "
            f"{price} ပါရှင့်။"
        )

    if item["intent"] == "product_stock":
        stock = product.get("stock")

        if not stock:
            return (
                f"{name} ရဲ့ stock အခြေအနေကို "
                "အတည်ပြုထားတဲ့ information မရှိသေးပါရှင့်။"
            )

        return (
            f"{name} stock က "
            f"{stock} ပါရှင့်။"
        )

    return (
        f"{name} အကြောင်း အတည်ပြုထားတဲ့ "
        "အချက်အလက်တွေ ရှိပါတယ်ရှင့်။"
    )


def reply_for_question(item):
    intent = item["intent"]

    if intent == "product_price":
        return product_reply(item)

    if intent == "product_stock":
        return product_reply(item)

    if intent == "delivery":
        if item["knowledge"]:
            result = item["knowledge"][0]

            if result["type"] == "faq":
                return result["answer"]

        return (
            "Delivery အကြောင်းကိုတော့ "
            "အတည်ပြုထားတဲ့ information မရှိသေးလို့ပါရှင့်။ "
            "တာဝန်ရှိသူကို မေးမြန်းပေးပါမယ်နော်။"
        )

    if intent == "order":
        if item["knowledge"]:
            result = item["knowledge"][0]

            if result["type"] == "faq":
                return result["answer"]

        return (
            "မှာယူပုံအကြောင်း အတည်ပြုထားတဲ့ "
            "information မရှိသေးလို့ပါရှင့်။ "
            "တာဝန်ရှိသူကို မေးမြန်းပေးပါမယ်နော်။"
        )

    if intent == "complaint":
        return (
            "အဆင်မပြေဖြစ်သွားတာအတွက် တောင်းပန်ပါတယ်ရှင့်။ "
            "တာဝန်ရှိသူဆီ လွှဲပေးပြီး စစ်ဆေးပေးပါမယ်နော်။"
        )

    if item["knowledge"]:
        result = item["knowledge"][0]

        if result["type"] == "faq":
            return result["answer"]

        if result["type"] == "company":
            return result["value"]

    return (
        "ဒီအကြောင်းအရာအတွက် အတည်ပြုထားတဲ့ "
        "information မရှိသေးလို့ပါရှင့်။ "
        "တာဝန်ရှိသူကို မေးမြန်းပေးပါမယ်နော်။"
    )


def local_reply(context):
    question = context["question"]

    if is_greeting(question):
        return (
            "မင်္ဂလာပါရှင့် 😊 "
            "ဘာအကြောင်းအရာလေး သိချင်လို့လဲရှင့်။ "
            "ကူညီပေးပါမယ်နော်။"
        )

    replies = []

    for item in context["questions"]:
        replies.append(
            reply_for_question(item)
        )

    if not replies:
        return (
            "ဟုတ်ကဲ့ရှင့်။ "
            "ဘာအကြောင်းအရာလေး သိချင်တာလဲ ပြောပေးပါနော်။"
        )

    return "\n".join(replies)


def main():
    agent = CustomerServiceAgent()

    customer_id = "test_customer"

    print("===================================")
    print(" Burmese Customer Service Agent")
    print(" Type 'exit' to quit")
    print("===================================")

    while True:
        try:
            question = input("\nCustomer: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if question.lower() == "exit":
            break

        if not question:
            continue

        context = agent.receive(
            customer_id,
            question,
        )

        print_context(context)

        reply = local_reply(context)

        agent.record_reply(
            customer_id,
            reply,
        )

        print("\nAgent:", reply)


if __name__ == "__main__":
    main()
