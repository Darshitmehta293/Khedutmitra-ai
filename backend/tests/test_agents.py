"""
KhedutMitra AI — Test Suite
Tests: calculations, agents, auth, buyer matching, multilingual intent
"""
import pytest
import asyncio
from typing import Any


# ─────────────────── Storage Advisor Tests ────────────────────

class TestStorageAdvisorCalculations:
    """
    All numerical calculations are deterministic — test them thoroughly.
    """

    @pytest.fixture
    def agent(self):
        from app.agents.storage_advisor_agent import StorageAdvisorAgent
        return StorageAdvisorAgent()

    @pytest.mark.asyncio
    async def test_scenario_a_storage_cost_exceeds_gain(self, agent):
        """
        Scenario A: Future price increases but storage cost > gain → SELL_NOW
        """
        result = await agent.run(
            crop_id="crop_cotton",
            quantity=50,
            current_price=7000,
            forecast_price=7050,   # Only ₹50/q rise
            forecast_confidence=0.80,
            storage_available=True,
            storage_cost_per_quintal_per_day=1.0,  # High storage cost
            transport_cost_total=5000,
            horizon_days=7,
        )
        assert result.success
        # 50 q * 7 days * 1.0 = 350 storage + 5000 transport = 5350 total cost
        # Gain = (7050-7000)*50 = 2500, net = 2500-5350-ql = negative
        assert result.data["action"] == "SELL_NOW", f"Expected SELL_NOW, got {result.data['action']}"
        assert result.data["potential_gain"] < 0

    @pytest.mark.asyncio
    async def test_scenario_b_significant_price_increase(self, agent):
        """
        Scenario B: Future price increase significantly exceeds costs → STORE
        """
        result = await agent.run(
            crop_id="crop_cotton",
            quantity=100,
            current_price=7000,
            forecast_price=7500,   # ₹500/q rise = ₹50,000 total
            forecast_confidence=0.80,
            storage_available=True,
            storage_cost_per_quintal_per_day=0.5,
            transport_cost_total=2000,
            horizon_days=7,
        )
        assert result.success
        # Storage: 100 * 7 * 0.5 = 350. Transport: 2000. QL: small
        # Gain = 50000 - 350 - 2000 - ~525 = ~47125
        assert result.data["action"] == "STORE", f"Expected STORE, got {result.data['action']}"
        assert result.data["potential_gain"] > 0

    @pytest.mark.asyncio
    async def test_scenario_c_uncertain_forecast(self, agent):
        """
        Scenario C: Low forecast confidence → WAIT (not STORE)
        """
        result = await agent.run(
            crop_id="crop_cotton",
            quantity=50,
            current_price=7000,
            forecast_price=7200,
            forecast_confidence=0.55,   # Below 0.70 threshold
            storage_available=True,
            storage_cost_per_quintal_per_day=0.5,
            transport_cost_total=2000,
            horizon_days=7,
        )
        assert result.success
        assert result.data["action"] in ("WAIT", "SELL_NOW")

    @pytest.mark.asyncio
    async def test_revenue_calculation_correctness(self, agent):
        """Revenue calculations must be deterministic and exact."""
        result = await agent.run(
            crop_id="crop_cotton",
            quantity=50,
            current_price=7000,
            forecast_price=7400,
            forecast_confidence=0.82,
            storage_available=True,
            storage_cost_per_quintal_per_day=0.5,
            transport_cost_total=2000,
            horizon_days=7,
        )
        assert result.success
        d = result.data
        assert d["current_revenue"] == pytest.approx(7000 * 50, abs=1)
        assert d["expected_future_gross"] == pytest.approx(7400 * 50, abs=1)
        assert d["storage_cost"] == pytest.approx(0.5 * 50 * 7, abs=1)
        assert d["transport_cost"] == pytest.approx(2000, abs=1)

    @pytest.mark.asyncio
    async def test_price_drop_is_sell_now(self, agent):
        """If forecast shows price drop, always SELL_NOW."""
        result = await agent.run(
            crop_id="crop_cotton",
            quantity=50,
            current_price=7000,
            forecast_price=6800,  # price drop
            forecast_confidence=0.85,
            storage_available=True,
            storage_cost_per_quintal_per_day=0.5,
            transport_cost_total=2000,
            horizon_days=7,
        )
        assert result.success
        assert result.data["action"] == "SELL_NOW"


# ─────────────────── Buyer Matching Tests ─────────────────────

class TestBuyerMatchingAgent:

    @pytest.fixture
    def agent(self):
        from app.agents.buyer_matching_agent import BuyerMatchingAgent
        return BuyerMatchingAgent()

    @pytest.mark.asyncio
    async def test_exact_crop_match_returns_results(self, agent):
        result = await agent.run(
            crop_id="crop_cotton", quantity=50, quality_grade="B", district="Ahmedabad"
        )
        assert result.success
        assert len(result.data["matches"]) > 0
        for m in result.data["matches"]:
            assert m["match_score"] > 0

    @pytest.mark.asyncio
    async def test_no_matches_for_wrong_crop(self, agent):
        """No buyers for an invalid crop_id."""
        result = await agent.run(
            crop_id="crop_invalid", quantity=50, quality_grade="B", district="Ahmedabad"
        )
        assert result.success
        assert len(result.data["matches"]) == 0

    @pytest.mark.asyncio
    async def test_matches_sorted_by_score(self, agent):
        result = await agent.run(
            crop_id="crop_cotton", quantity=50, quality_grade="A", district="Ahmedabad"
        )
        scores = [m["match_score"] for m in result.data["matches"]]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_quantity_mismatch_reduces_score(self, agent):
        """Quantity way below min_quantity reduces score."""
        result_normal = await agent.run(
            crop_id="crop_cotton", quantity=50, quality_grade="A", district="Ahmedabad"
        )
        result_low = await agent.run(
            crop_id="crop_cotton", quantity=1, quality_grade="A", district="Ahmedabad"
        )
        assert result_normal.success and result_low.success
        avg_normal = sum(m["match_score"] for m in result_normal.data["matches"]) / max(1, len(result_normal.data["matches"]))
        avg_low = sum(m["match_score"] for m in result_low.data["matches"]) / max(1, len(result_low.data["matches"]))
        assert avg_normal >= avg_low

    @pytest.mark.asyncio
    async def test_groundnut_buyers_match_groundnut(self, agent):
        result = await agent.run(
            crop_id="crop_groundnut", quantity=100, quality_grade="B", district="Junagadh"
        )
        assert result.success
        for m in result.data["matches"]:
            assert "groundnut" in m["listing_id"].lower() or m["crop_name"].lower() == "groundnut"


# ─────────────────── Intent Detection Tests ───────────────────

class TestIntentDetection:

    def test_english_market_price(self):
        from app.services.granite_service import detect_intent
        assert detect_intent("What is the cotton price today?") == "MARKET_PRICE"

    def test_gujarati_sell_or_store(self):
        from app.services.granite_service import detect_intent
        assert detect_intent("મારી પાસે 30 ક્વિન્ટલ કપાસ છે. અત્યારે વેચવું?") == "SELL_OR_STORE"

    def test_hindi_sell_or_store(self):
        from app.services.granite_service import detect_intent
        assert detect_intent("मेरे पास 30 क्विंटल कपास है। अभी बेचना चाहिए?") == "SELL_OR_STORE"

    def test_buyer_search_english(self):
        from app.services.granite_service import detect_intent
        assert detect_intent("Find buyers for my groundnut") == "FIND_BUYER"

    def test_income_query(self):
        from app.services.granite_service import detect_intent
        assert detect_intent("How much income can I earn from 50 quintals?") == "INCOME"

    def test_quality_check(self):
        from app.services.granite_service import detect_intent
        assert detect_intent("Check quality of my cotton") == "QUALITY_CHECK"


# ─────────────────── Market Data Provider Tests ───────────────

class TestMockMarketDataProvider:

    @pytest.fixture
    def provider(self):
        from app.services.market_data_provider import MockMarketDataProvider
        return MockMarketDataProvider()

    @pytest.mark.asyncio
    async def test_current_prices_returns_all_markets(self, provider):
        prices = await provider.get_current_prices("crop_cotton")
        assert len(prices) == 8  # All 8 demo markets

    @pytest.mark.asyncio
    async def test_current_prices_all_marked_demo(self, provider):
        prices = await provider.get_current_prices("crop_cotton")
        assert all(p.is_demo for p in prices)

    @pytest.mark.asyncio
    async def test_historical_prices_correct_count(self, provider):
        history = await provider.get_historical_prices("crop_cotton", "mkt_ahmedabad", 30)
        assert len(history) == 30

    @pytest.mark.asyncio
    async def test_prices_in_reasonable_range(self, provider):
        prices = await provider.get_current_prices("crop_cotton")
        for p in prices:
            assert 4000 <= float(p.modal_price) <= 12000, f"Price {p.modal_price} out of range"

    @pytest.mark.asyncio
    async def test_min_less_than_max(self, provider):
        prices = await provider.get_current_prices("crop_groundnut")
        for p in prices:
            assert float(p.min_price) <= float(p.modal_price) <= float(p.max_price)

    @pytest.mark.asyncio
    async def test_market_filter(self, provider):
        prices = await provider.get_current_prices("crop_cotton", "mkt_ahmedabad")
        assert len(prices) == 1
        assert prices[0].market_id == "mkt_ahmedabad"


# ─────────────────── Forecast Service Tests ───────────────────

class TestForecastService:

    @pytest.fixture
    def service(self):
        from app.services.market_data_provider import MockMarketDataProvider
        from app.services.forecast_service import ForecastService
        return ForecastService(MockMarketDataProvider())

    @pytest.mark.asyncio
    async def test_confidence_decreases_with_horizon(self, service):
        fc3 = await service.forecast_single("crop_cotton", "mkt_ahmedabad", 3)
        fc30 = await service.forecast_single("crop_cotton", "mkt_ahmedabad", 30)
        assert fc3.confidence > fc30.confidence

    @pytest.mark.asyncio
    async def test_bounds_widen_with_horizon(self, service):
        fc7 = await service.forecast_single("crop_cotton", "mkt_ahmedabad", 7)
        fc30 = await service.forecast_single("crop_cotton", "mkt_ahmedabad", 30)
        band_7 = fc7.upper_bound - fc7.lower_bound
        band_30 = fc30.upper_bound - fc30.lower_bound
        assert band_30 > band_7

    @pytest.mark.asyncio
    async def test_forecast_series_has_all_horizons(self, service):
        results = await service.forecast_series("crop_cotton", "mkt_rajkot")
        horizons = [r.horizon_days for r in results]
        assert set(horizons) == {3, 7, 15, 30}

    @pytest.mark.asyncio
    async def test_forecast_price_near_historical(self, service):
        """Forecast should not be wildly off from historical prices."""
        fc7 = await service.forecast_single("crop_cotton", "mkt_ahmedabad", 7)
        assert 4000 < fc7.predicted_price < 12000
        assert fc7.lower_bound <= fc7.predicted_price <= fc7.upper_bound
