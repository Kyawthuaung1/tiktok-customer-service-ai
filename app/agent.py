from .knowledge import search_knowledge
from .memory import ConversationMemory


SYSTEM_POLICY = """
သင်သည် Customer Service Representative AI Agent တစ်ယောက်ဖြစ်သည်။

အဓိကတာဝန်များ:
1. Customer ကို မြန်မာဘာသာဖြင့် သဘာဝကျကျ၊ ယဉ်ကျေးစွာ ဖြေကြားပါ။
2. Business Knowledge Base ထဲရှိ အချက်အလက်ကိုသာ အဓိကအရင်းအမြစ်အဖြစ် အသုံးပြုပါ။
3. Knowledge Base ထဲတွင် မရှိသော ဈေးနှုန်း၊ stock၊ promotion၊ delivery၊ policy
   စသည့်အချက်များကို မခန့်မှန်းပါနှင့်။
4. မသေချာပါက မသေချာကြောင်း ရိုးရိုးသားသားပြောပြီး Human Agent ဆီလွှဲရန် အကြံပြုပါ။
5. Customer မေးခွန်းကို တိုက်ရိုက်ဖြေပါ။ မလိုအပ်ဘဲ ရှည်လျားစွာမဖြေပါနှင့်။
6. Customer နှင့် ယခင်ပြောဆိုထားသော context ကို ထည့်သွင်းစဉ်းစားပါ။
7. စက်ရုပ်ဆန်သော စာသားမဟုတ်ဘဲ Customer Service Representative တစ်ယောက်
   ပြောသလို သဘာဝကျစွာ ပြောပါ။
"""


class CustomerServiceAgent:
    def __init__(self):
        self.memory = ConversationMemory()

    def build_context(self, customer_id: str, question: str):
        history = self.memory.get(customer_id)
        knowledge = search_knowledge(question)

        return {
            "policy": SYSTEM_POLICY.strip(),
            "history": history,
            "knowledge": knowledge,
            "question": question,
        }

    def receive(self, customer_id: str, question: str):
        context = self.build_context(customer_id, question)

        self.memory.add(customer_id, "user", question)

        return context
