from .knowledge import search_knowledge
from .memory import ConversationMemory
from .intent import detect_intent, split_questions
import re


SYSTEM_POLICY = """
သင်သည် မြန်မာဘာသာဖြင့် Customer Service Representative အဖြစ်
တာဝန်ထမ်းဆောင်သော AI Agent ဖြစ်သည်။

အဓိကတာဝန်မှာ Customer ကို လူသား Customer Service Representative
တစ်ယောက်ကဲ့သို့ သဘာဝကျ၊ ယဉ်ကျေးပြီး တိုက်ရိုက်ကူညီပေးရန်ဖြစ်သည်။

RULES:

1. Customer ကို မြန်မာလို သဘာဝကျစွာ ပြောပါ။
2. Customer မေးထားသောအချက်ကိုသာ အဓိကဖြေပါ။
3. Business Knowledge Base ကို business facts အတွက် source of truth
   အဖြစ် အသုံးပြုပါ။
4. Knowledge Base ထဲမရှိသော ဈေးနှုန်း၊ stock၊ promotion၊ delivery fee၊
   delivery time၊ warranty သို့မဟုတ် policy ကို မခန့်မှန်းပါနှင့်။
5. Product မတွေ့ပါက အခြား product ၏ information ကို
   အစားထိုးမဖြေပါနှင့်။
6. Knowledge မရှိပါက ရိုးရိုးသားသားပြောပြီး Human Agent ဆီ
   လွှဲပေးနိုင်ပါသည်။
7. Customer မေးခွန်းများစွာရှိပါက တစ်ခုချင်းစီ စဉ်းစားပြီး ဖြေပါ။
8. ယခင် conversation context ကို အသုံးပြုပါ။
9. Message တစ်ခုထဲတွင် follow-up question ပါလာပါက
   အဲဒီ message ထဲမှာ အရင်ဖော်ပြထားသော product/entity ကို
   နောက်မေးခွန်းများတွင် ဆက်လက်အသုံးပြုပါ။
10. Customer က previous message ကို ဆက်စပ်ပြီး မေးလာပါက
    ယခင် context မှ product/entity ကို ဆက်လက်နားလည်ပါ။
11. Complaint ဖြစ်ပါက ယဉ်ကျေးစွာ တောင်းပန်ပြီး
    လိုအပ်ပါက Human Agent ဆီ လွှဲပါ။
12. မသေချာသောအချက်ကို မဖန်တီးပါနှင့်။
13. စက်ရုပ်ဆန်သော၊ အလွန်ရှည်သော explanation များကို ရှောင်ပါ။
"""


GREETING_WORDS = {
    "မင်္ဂလာပါ",
    "ဟယ်လို",
    "hello",
    "hi",
    "hey",
}


def is_greeting(text: str) -> bool:
    normalized = text.strip().lower()

    if normalized in GREETING_WORDS:
        return True

    greeting_phrases = [
        "မင်္ဂလာပါရှင့်",
        "မင်္ဂလာပါခင်ဗျာ",
        "မင်္ဂလာပါခင်ဗျ",
        "hello",
        "hi",
        "hey",
    ]

    return any(
        phrase in normalized
        for phrase in greeting_phrases
    )


def has_explicit_product_like_reference(text: str) -> bool:
    """
    Detect whether the customer message appears to contain
    a specific product/entity reference.

    Example:
        "iPhone 17 Pro ဘယ်လောက်လဲ" -> True
        "stock ရှိလား" -> False
        "ဘယ်လောက်လဲ" -> False
    """

    text = text.strip().lower()

    # Latin/alphanumeric product names such as:
    # iPhone 17 Pro, Galaxy S25, AirPods Pro
    if re.search(r"[a-z]", text):
        return True

    # Numbers can also identify products.
    # Avoid treating ordinary question numbers as product names.
    if re.search(r"\b\d{2,}\b", text):
        return True

    return False


class CustomerServiceAgent:

    def __init__(self):
        self.memory = ConversationMemory()

    def _last_product(self, customer_id: str):
        history = self.memory.get(customer_id)

        for message in reversed(history):
            if message["role"] != "user":
                continue

            results = search_knowledge(
                message["content"]
            )

            for result in results:
                if result["type"] == "product":
                    return result["name"]

        return None

    def retrieve(
        self,
        customer_id: str,
        question: str,
        current_product: str | None = None,
    ):
        if is_greeting(question):
            return []

        # First priority:
        # Search the customer's current question directly.
        results = search_knowledge(question)

        if results:
            return results

        # If this message already has a verified product from
        # an earlier question in the SAME message, use it.
        if current_product:
            contextual_query = (
                f"{current_product} {question}"
            )

            results = search_knowledge(
                contextual_query
            )

            if results:
                return results

        # Only use previous conversation product context when
        # the current question does NOT explicitly mention another
        # product/entity.
        #
        # This prevents:
        #   previous = Test Product A
        #   current  = iPhone 17 Pro
        #
        # from incorrectly returning Test Product A.
        if not has_explicit_product_like_reference(question):
            last_product = self._last_product(
                customer_id
            )

            if last_product:
                contextual_query = (
                    f"{last_product} {question}"
                )

                results = search_knowledge(
                    contextual_query
                )

                if results:
                    return results

        return []

    def analyze_question(
        self,
        customer_id: str,
        question: str,
        current_product: str | None = None,
    ):
        intent = detect_intent(question)

        knowledge = self.retrieve(
            customer_id,
            question,
            current_product,
        )

        detected_product = current_product

        for result in knowledge:
            if result["type"] == "product":
                detected_product = result["name"]
                break

        return {
            "question": question,
            "intent": intent,
            "knowledge": knowledge,
            "product": detected_product,
            "needs_human": (
                len(knowledge) == 0
                and not is_greeting(question)
            ),
        }

    def build_context(
        self,
        customer_id: str,
        question: str,
    ):
        history = self.memory.get(customer_id)

        questions = split_questions(question)

        analyses = []
        current_product = None

        for item in questions:
            analysis = self.analyze_question(
                customer_id,
                item,
                current_product,
            )

            analyses.append(analysis)

            if analysis["product"]:
                current_product = analysis["product"]

        return {
            "policy": SYSTEM_POLICY.strip(),
            "history": history,
            "question": question,
            "questions": analyses,
            "needs_human": any(
                item["needs_human"]
                for item in analyses
            ),
        }

    def receive(
        self,
        customer_id: str,
        question: str,
    ):
        context = self.build_context(
            customer_id,
            question,
        )

        self.memory.add(
            customer_id,
            "user",
            question,
        )

        return context

    def record_reply(
        self,
        customer_id: str,
        reply: str,
    ):
        self.memory.add(
            customer_id,
            "assistant",
            reply,
        )
