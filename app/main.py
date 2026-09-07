from .agent import CustomerServiceAgent, is_greeting


def print_context(context):
    print("\n-----------------------------------")
    print("[Agent Context]")
    print("Question:", context["question"])

    if context["knowledge"]:
        print("\nKnowledge found:")

        for item in context["knowledge"]:
            print(
                f"- [{item['type']}] "
                f"score={item['score']} "
                f"{item}"
            )
    else:
        print("\nKnowledge found: None")

    print("Needs human:", context["needs_human"])
    print("-----------------------------------")


def local_reply(context):
    question = context["question"]

    if is_greeting(question):
        return (
            "မင်္ဂလာပါရှင့် 😊 "
            "ဘာအကြောင်းအရာလေး သိချင်လို့လဲရှင့်။ "
            "ကူညီပေးပါမယ်နော်။"
        )

    knowledge = context["knowledge"]

    if not knowledge:
        return (
            "ဟုတ်ကဲ့ရှင့်။ ဒီအချက်အလက်လေးကိုတော့ "
            "အခုလက်ရှိ အတည်ပြုထားတဲ့ information မရှိသေးလို့ပါရှင့်။ "
            "တာဝန်ရှိသူကို မေးမြန်းပြီး ပြန်လည်အကြောင်းကြားပေးပါမယ်နော်။"
        )

    top = knowledge[0]

    if top["type"] == "product":
        data = top["data"]

        name = data.get("name", "ဒီပစ္စည်း")
        price = data.get("price")
        stock = data.get("stock")

        parts = [f"{name}"]

        if price:
            parts.append(f"ဈေးနှုန်း {price}")

        if stock:
            parts.append(f"Stock {stock}")

        return "ဟုတ်ကဲ့ရှင့် 😊 " + "၊ ".join(parts) + " ပါရှင့်။"

    if top["type"] == "faq":
        return f"ဟုတ်ကဲ့ရှင့် 😊 {top['answer']}"

    if top["type"] == "company":
        return f"ဟုတ်ကဲ့ရှင့် 😊 {top['value']}"

    return (
        "ဟုတ်ကဲ့ရှင့်။ "
        "သက်ဆိုင်ရာအချက်အလက်ကို ရှာတွေ့ထားပါတယ်ရှင့်။"
    )


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
