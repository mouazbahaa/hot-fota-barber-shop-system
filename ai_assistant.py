# -*- coding: utf-8 -*-
"""
ai_assistant.py
"المساعد الذكي" بتاع السيستم:
- بيقترح خدمات إضافية / عروض على حسب اللي العميل مختاره في السلة.
- بيقترح أنسب معاد فاضي.
هو دلوقتي شغال بقواعد بسيطة محليًا (من غير إنترنت)، لكن مبني بشكل
سهل إنك تستبدله بموديل ذكاء اصطناعي حقيقي (مثلاً عن طريق Anthropic API)
لو حبيت تطوّره بعدين - شوف method: get_ai_suggestion
"""

from typing import List


class SmartAssistant:

    COMBO_HINTS = {
        frozenset({"قصة شعر", "حلاقة دقن"}): "لو ضفت (فوطة سخنة) هتاخد إحساس استرخاء أحلى بسعر رمزي!",
        frozenset({"قصة شعر"}): "عندنا عرض: قصة شعر + دقن أوفر من الاتنين لوحدهم.",
    }

    def suggest_for_cart(self, service_names: List[str]) -> str:
        if not service_names:
            return "السلة فاضية دلوقتي، اختار أول خدمة عشان أقدر أساعدك."

        names = frozenset(service_names)
        for combo, hint in self.COMBO_HINTS.items():
            if combo.issubset(names):
                return hint

        if "فوطة سخنة" not in names:
            return "جرب تضيف (فوطة سخنة) بعد الحلاقة، إحساس مختلف تمامًا."

        return "اختيارك تمام كده! جاهز تكمل الحجز."

    def recommend_time(self, available_slots: List[str]) -> str:
        if not available_slots:
            return "معلش، مفيش مواعيد فاضية في اليوم ده، جرب يوم تاني."
        best = available_slots[len(available_slots) // 2]
        return f"موعد مقترح ليك: {best} (وقت مناسب غالبًا)"

    def get_ai_suggestion(self, prompt: str) -> str:
        """
        Placeholder لو حبيت تربط موديل ذكاء اصطناعي حقيقي بدل القواعد البسيطة.
        مثال (خارج نطاق تشغيل السيستم ده، محتاج مكتبة anthropic ومفتاح API):

            import anthropic
            client = anthropic.Anthropic(api_key="YOUR_KEY")
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        دلوقتي بيرجع اقتراح محلي بسيط بدل ده:
        """
        return self.suggest_for_cart(prompt.split(","))
