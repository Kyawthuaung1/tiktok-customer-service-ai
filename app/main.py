from .agent import CustomerServiceAgent


def main():
    agent = CustomerServiceAgent()

    customer_id = "test_customer"

    print("===================================")
    print(" Burmese Customer Service Agent")
    print(" Type 'exit' to quit")
    print("===================================")

    while True:
        question = input("\nCustomer: ").strip()

        if question.lower() == "exit":
            break

        if not question:
            continue

        context = agent.receive(customer_id, question)

        print("\n[Agent Context]")
        print("Question:", context["question"])

        if context["knowledge"]:
            print("\nKnowledge found:")
            for item in context["knowledge"]:
                print("-", item["text"])
        else:
            print("\nKnowledge found: None")


if __name__ == "__main__":
    main()
