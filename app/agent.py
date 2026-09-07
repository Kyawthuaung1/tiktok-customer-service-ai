from .knowledge import search_knowledge
from .memory import ConversationMemory


SYSTEM_POLICY = """
သင်သည် မြန်မာဘာသာဖြင့် Customer Service Representative အဖြစ်
တာဝန်ထမ်းဆောင်သော AI Agent ဖြစ်သည်။

RULES:

1. Customer ကို မြန်မာလို သဘာဝကျပြီး ယဉ်ကျေးစွာ ပြောပါ။
2. Customer ၏ မေးခွန်းကို တိုက်ရိုက်နားလည်ပြီး လိုအပ်သလောက်သာ ဖြေပါ။
3. Business Knowledge Base ထဲတွင်ရှိသော အချက်အလက်ကိုသာ
   business fact အဖြစ် အသုံးပြုပါ။
4. ဈေးနှုန်း၊ stock၊ promotion၊ delivery fee၊ delivery time၊
   warranty၊ policy စသည့်အချက်များကို မခန့်မှန်းပါနှင့်။
5. Knowledge Base တွင် မရှိသောအချက်ကို မဖန်တီးပါနှင့်။
6. Product တစ်ခုကို မေးလာပါက သက်ဆိုင်ရာ product record ကို
   ဦးစားပေးအသုံးပြုပါ။
7. Product မတွေ့ပါက အခြား product ၏ information ကို
   အစားထိုးမဖြေပါနှင့်။
8. Greeting ဖြစ်ပါက သဘာဝကျစွာ ပြန်နှုတ်ဆက်ပါ။
9. Customer မေးခွန်းများစွာ မေးပါက တစ်ခုချင်းစီ ဖြေပါ။
10. ယခင် conversation context ကို ထည့်သွင်းစဉ်းစားပါ။
11. မသေချာသောအချက်ကို မခန့်မှန်းဘဲ ရိုးရိုးသားသား ပြောပါ။
12. Customer complaint ဖြစ်ပါက ယဉ်ကျေးစွာ တောင်းပန်ပြီး
    လိုအပ်ပါက Human Agent ဆီ လွှဲပေးပါ။
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


class CustomerServiceAgent:
    def __init__(self):
        self.memory = ConversationMemory()

    def retrieve(self, question: str):
        if is_greeting(question):
            return []

        return search_knowledge(question)

    def build_context(self, customer_id: str, question: str):
        history = self.memory.get(customer_id)
        knowledge = self.retrieve(question)

        return {
            "policy": SYSTEM_POLICY.strip(),
            "history": history,
            "knowledge": knowledge,
            "question": question,
            "needs_human": (
                len(knowledge) == 0
                and not is_greeting(question)
            ),
        }

    def receive(self, customer_id: str, question: str):
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

    def record_reply(self, customer_id: str, reply: str):
        self.memory.add(
            customer_id,
            "assistant",
            reply,
        )
