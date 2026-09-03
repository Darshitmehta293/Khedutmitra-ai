"""
KhedutMitra AI — IBM Granite LLM Service

Wraps ibm-watsonx-ai SDK. Falls back to deterministic templates when
Granite is not configured (development/demo mode).
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import logger


INTENT_EXAMPLES = {
    "MARKET_PRICE": ["price", "bhav", "ભાવ", "भाव", "mandi", "rate", "today", "aaj"],
    "PRICE_FORECAST": ["forecast", "predict", "future", "wait", "7 days", "rate change", "aaage"],
    "SELL_OR_STORE": ["sell", "store", "vech", "vechan", "rakhvu", "रखना", "बेचना", "વેચ", "રાખ", "storu"],
    "FIND_BUYER": ["buyer", "kharidu", "khareedaar", "ખરીદ", "खरीदार", "who will buy"],
    "QUALITY_CHECK": ["quality", "grade", "guni", "ગુણ", "गुणवत्ता", "check my"],
    "INCOME": ["income", "earn", "aavak", "આવક", "आमदनी", "how much"],
}


def detect_intent(message: str) -> str:
    msg_lower = message.lower()
    for intent, keywords in INTENT_EXAMPLES.items():
        if any(kw in msg_lower for kw in keywords):
            return intent
    return "GENERAL_CROP_QUERY"


class GraniteLLMService:
    """
    IBM Granite integration via watsonx.ai.
    When IBM credentials are absent, uses deterministic fallback templates.
    """

    def __init__(self):
        self._client = None
        self._token = None
        self._configured = settings.is_granite_configured

    def _get_client(self):
        if self._client is None and self._configured:
            try:
                from ibm_watsonx_ai import Credentials
                from ibm_watsonx_ai.foundation_models import ModelInference
                creds = Credentials(
                    url=settings.IBM_GRANITE_ENDPOINT,
                    api_key=settings.IBM_API_KEY,
                )
                self._client = ModelInference(
                    model_id=settings.IBM_GRANITE_MODEL_ID,
                    credentials=creds,
                    project_id=settings.IBM_PROJECT_ID,
                    params={
                        "max_new_tokens": 512,
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "repetition_penalty": 1.1,
                    },
                )
            except Exception as e:
                logger.error("Failed to initialize Granite client", error=str(e))
                self._configured = False
        return self._client

    async def generate(self, prompt: str, max_tokens: int = 512) -> str:
        client = self._get_client()
        if client is None:
            return self._fallback_response(prompt)
        try:
            response = client.generate_text(prompt=prompt)
            return response.strip()
        except Exception as e:
            logger.error("Granite generate error", error=str(e))
            return self._fallback_response(prompt)

    async def explain_recommendation(self, rec: Dict[str, Any], language: str = "en") -> str:
        if not self._configured:
            return self._template_recommendation(rec, language)

        prompt = self._build_recommendation_prompt(rec, language)
        return await self.generate(prompt)

    async def chat(self, user_message: str, context: Dict[str, Any], language: str = "en",
                   history: Optional[List[Dict]] = None) -> str:
        if not self._configured:
            return self._template_chat(user_message, context, language)

        prompt = self._build_chat_prompt(user_message, context, language, history or [])
        return await self.generate(prompt)

    def _build_recommendation_prompt(self, rec: Dict[str, Any], language: str) -> str:
        lang_instruction = {
            "gu": "Respond ONLY in Gujarati (ગુજરાતી). Use simple farmer-friendly language.",
            "hi": "Respond ONLY in Hindi (हिन्दी). Use simple farmer-friendly language.",
            "en": "Respond in clear, simple English. Avoid technical jargon.",
        }.get(language, "Respond in English.")

        return f"""You are KhedutMitra AI, an agricultural market advisor for Gujarat farmers.
{lang_instruction}

Based on the following market analysis, explain the recommendation in 3-4 short sentences:
- Crop: {rec.get('crop_name', 'Cotton')}
- Quantity: {rec.get('quantity', 'N/A')} quintals
- Current Price: ₹{rec.get('current_price', 0):,.0f}/quintal
- 7-Day Forecast: ₹{rec.get('forecast_price', 0):,.0f}/quintal
- Current Revenue: ₹{rec.get('current_revenue', 0):,.0f}
- Expected Net Revenue (if stored): ₹{rec.get('expected_net_revenue', 0):,.0f}
- Storage Cost: ₹{rec.get('storage_cost', 0):,.0f}
- Quality Loss Cost: ₹{rec.get('quality_loss_cost', 0):,.0f}
- Recommendation: {rec.get('action', 'SELL_NOW')}
- Potential Gain: ₹{rec.get('potential_gain', 0):,.0f}

Explain WHY this is the best decision. State the potential gain clearly.
Note that this is an AI estimate, not a guarantee.
Keep the explanation under 80 words."""

    def _build_chat_prompt(self, message: str, context: Dict[str, Any], language: str,
                           history: List[Dict]) -> str:
        lang_instruction = {
            "gu": "Respond ONLY in Gujarati.",
            "hi": "Respond ONLY in Hindi.",
            "en": "Respond in English.",
        }.get(language, "Respond in English.")

        context_str = json.dumps(context, ensure_ascii=False, indent=2)[:800]
        history_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history[-4:]])

        return f"""You are KhedutMitra AI, a helpful agricultural market assistant for Gujarat cotton and groundnut farmers.
{lang_instruction}
You help farmers understand market prices, decide when to sell, find buyers, and maximize income.
Never invent prices — only use the context provided.

Market Context: {context_str}

Recent conversation:
{history_str}

Farmer question: {message}

Answer concisely in 2-3 sentences. If you don't have enough data to answer, say so honestly."""

    def _template_recommendation(self, rec: Dict[str, Any], language: str) -> str:
        action = rec.get("action", "SELL_NOW")
        gain = rec.get("potential_gain", 0)
        days = rec.get("recommended_days", 7)
        cur = rec.get("current_price", 0)
        fut = rec.get("forecast_price", 0)

        templates = {
            "en": {
                "STORE": f"Based on market analysis, storing your crop for {days} days could earn you an additional ₹{gain:,.0f}. The forecast shows prices may rise from ₹{cur:,.0f} to ₹{fut:,.0f}/quintal. After storage and transport costs, you gain ₹{gain:,.0f} more. Note: This is an AI estimate, not a guarantee.",
                "SELL_NOW": f"Current market conditions suggest selling now is the best option. Storing would cost more than the expected price increase. Current price of ₹{cur:,.0f}/quintal is favorable. Act quickly to secure this price.",
                "WAIT": f"Market prices are uncertain right now. Waiting 2-3 days and monitoring prices before deciding is advisable. Current price is ₹{cur:,.0f}/quintal.",
            },
            "gu": {
                "STORE": f"બજારના વિશ્લેષણ મુજબ, {days} દિવસ સ્ટોર કરવાથી ₹{gain:,.0f} વધુ મળી શકે છે. ભાવ ₹{cur:,.0f} થી ₹{fut:,.0f}/ક્વિન્ટલ થઈ શકે છે. આ AI અંદાજ છે, ખાતરી નથી.",
                "SELL_NOW": f"અત્યારે વેચવું સૌથી સારો વિકલ્પ છે. સ્ટોર કરવાનો ખર્ચ ભાવ વધારા કરતા વધુ છે. ₹{cur:,.0f}/ક્વિન્ટલ ભાવ સારો છે.",
                "WAIT": f"બજારના ભાવ અનિશ્ચિત છે. 2-3 દિવસ રાહ જોઈ ભાવ જોયા પછી નિર્ણય લો. અત્યારે ₹{cur:,.0f}/ક્વિન્ટલ.",
            },
            "hi": {
                "STORE": f"बाजार विश्लेषण के अनुसार, {days} दिन भंडारण से ₹{gain:,.0f} अधिक मिल सकते हैं। कीमत ₹{cur:,.0f} से ₹{fut:,.0f}/क्विंटल हो सकती है। यह AI अनुमान है, गारंटी नहीं।",
                "SELL_NOW": f"अभी बेचना सबसे अच्छा विकल्प है। भंडारण लागत अपेक्षित मूल्य वृद्धि से अधिक है। ₹{cur:,.0f}/क्विंटल की कीमत अनुकूल है।",
                "WAIT": f"बाजार की कीमतें अभी अनिश्चित हैं। 2-3 दिन इंतजार करके कीमत देखें। अभी ₹{cur:,.0f}/क्विंटल।",
            },
        }
        lang_templates = templates.get(language, templates["en"])
        return lang_templates.get(action, lang_templates["SELL_NOW"])

    def _template_chat(self, message: str, context: Dict[str, Any], language: str) -> str:
        intent = detect_intent(message)
        price = context.get("current_price", 0)
        crop = context.get("crop_name", "crop")

        responses = {
            "en": {
                "MARKET_PRICE": f"Today's {crop} price is approximately ₹{price:,.0f}/quintal (demo data). Prices vary by mandi and quality grade.",
                "SELL_OR_STORE": f"Based on current analysis, check the Sell or Store page for a detailed recommendation comparing today's price of ₹{price:,.0f} against the 7-day forecast.",
                "FIND_BUYER": f"I found several active buyers for {crop} in your area. Check the Buyer Marketplace for matched buyers with prices and contact details.",
                "PRICE_FORECAST": f"The 7-day forecast for {crop} suggests a slight price change from current ₹{price:,.0f}/quintal. Please check the Market Intelligence page for the full forecast chart.",
                "INCOME": f"Your estimated income depends on quantity, quality, and timing. Use the Income Dashboard for a detailed breakdown.",
                "QUALITY_CHECK": "Upload a photo of your crop on the Quality Assessment page for an AI-assisted preliminary grade estimate.",
                "GENERAL_CROP_QUERY": f"I can help with {crop} prices, forecasts, buyers, and sell/store decisions. What would you like to know?",
            },
            "gu": {
                "MARKET_PRICE": f"આજે {crop}નો ભાવ લગભગ ₹{price:,.0f}/ક્વિન્ટલ છે (ડેમો ડેટા). મંડી અને ગ્રેડ પ્રમાણે ભાવ બદલાય.",
                "SELL_OR_STORE": f"'વેચો અથવા સ્ટોર કરો' પૃષ્ઠ પર જઈ વિગતવાર ભલામણ જુઓ.",
                "FIND_BUYER": f"તમારા વિસ્તારમાં {crop} માટે ઘણા ખરીદદારો છે. ખરીદ બજાર પૃષ્ઠ ચેક કરો.",
                "PRICE_FORECAST": f"{crop}ના ભાવ 7 દિવસ પછી બદલાઈ શકે છે. ₹{price:,.0f}/ક્વિન્ટલ હાલ ભાવ. વિગત માટે બજાર ભાવ પૃષ્ઠ જુઓ.",
                "INCOME": "તમારી આવક ક્વૉન્ટિટી, ગ્રેડ અને સમય પ્રમાણે બદલાય. આવક ડૅશબૉર્ડ ઉઘાડો.",
                "QUALITY_CHECK": "ગ્રેડ જાણવા માટે ગ્રેડ ચેક પૃષ્ઠ પર ફોટો અપલોડ કરો.",
                "GENERAL_CROP_QUERY": f"હું {crop}ના ભાવ, ભવિષ્ય, ખરીદ, વેચ/સ્ટોરમાં મદદ કરી શકું. શું જાણવું છે?",
            },
            "hi": {
                "MARKET_PRICE": f"आज {crop} का भाव लगभग ₹{price:,.0f}/क्विंटल है (डेमो डेटा)।",
                "SELL_OR_STORE": f"'बेचें या रखें' पेज पर जाकर विस्तृत सलाह देखें।",
                "FIND_BUYER": f"आपके क्षेत्र में {crop} के कई खरीदार हैं। खरीदार बाजार पेज देखें।",
                "PRICE_FORECAST": f"{crop} की कीमत 7 दिनों में बदल सकती है। अभी ₹{price:,.0f}/क्विंटल।",
                "INCOME": "आपकी आमदनी मात्रा, गुणवत्ता और समय पर निर्भर है। आय डैशबोर्ड खोलें।",
                "QUALITY_CHECK": "ग्रेड जानने के लिए गुणवत्ता जांच पेज पर फोटो अपलोड करें।",
                "GENERAL_CROP_QUERY": f"मैं {crop} की कीमत, पूर्वानुमान, खरीदार और बेचने/रखने में मदद कर सकता हूं।",
            },
        }
        lang_resp = responses.get(language, responses["en"])
        return lang_resp.get(intent, lang_resp["GENERAL_CROP_QUERY"])

    @property
    def is_configured(self) -> bool:
        return self._configured


_granite_service: Optional[GraniteLLMService] = None


def get_granite_service() -> GraniteLLMService:
    global _granite_service
    if _granite_service is None:
        _granite_service = GraniteLLMService()
    return _granite_service
