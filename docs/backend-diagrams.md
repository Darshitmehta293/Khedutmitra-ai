# KhedutMitra AI — Backend & Database Diagrams

## 1. High-Level Architecture

```mermaid
graph TB
    subgraph Client["Frontend (React + Vite + Tailwind)"]
        LP["Landing Page"]
        DASH["Dashboard"]
        MKT["Market"]
        SOS["Sell/Store"]
        BUY["Buyers"]
        QLT["Quality"]
        INV["Inventory"]
        INC["Income"]
        AI["AI Assistant"]
        FP["Farm Planner"]
        IH["Intelligence Hub"]
        ADM["Admin"]
    end

    subgraph API["FastAPI Backend"]
        AUTH["/api/auth"]
        FARM["/api/farmer"]
        MKT_API["/api/markets"]
        AI_API["/api/ai"]
        BUY_API["/api/buyers"]
        INTEL_API["/api/intelligence"]
        ADMIN_API["/api/admin"]
    end

    subgraph Services["Services & Agents"]
        ORCH["Agent Orchestrator"]
        MANDI["Mandi Price Agent"]
        FCST["Forecasting Agent"]
        STORE["Storage Advisor"]
        MATCH["Buyer Matching"]
        QUAL["Quality Grading"]
        INC_AGT["Income Dashboard"]
        GRANITE["Granite LLM / Templates"]
        MKT_PROV["Market Data Provider<br/>Mock / AGMARKNET"]
    end

    subgraph Data["Data Layer"]
        DB[(SQLite / PostgreSQL)]
        REDIS[(Redis / In-Memory)]
    end

    LP --> API
    DASH --> API
    MKT --> API
    SOS --> API
    BUY --> API
    QLT --> API
    INV --> API
    INC --> API
    AI --> API
    FP --> API
    IH --> API
    ADM --> API

    AUTH --> DB
    FARM --> DB
    MKT_API --> ORCH
    AI_API --> ORCH
    BUY_API --> DB
    INTEL_API --> DB
    ADMIN_API --> DB

    ORCH --> MANDI
    ORCH --> FCST
    ORCH --> STORE
    ORCH --> MATCH
    ORCH --> QUAL
    ORCH --> INC_AGT
    ORCH --> GRANITE

    MANDI --> MKT_PROV
    FCST --> MKT_PROV
    MATCH --> DB

    MKT_PROV --> REDIS
    ORCH --> DB
```

---

## 2. Database ER Diagram

```mermaid
erDiagram
    USER ||--o| FARMER_PROFILE : "has"
    USER ||--o| BUYER_PROFILE : "has"
    USER ||--o{ FARMER_INVENTORY : "owns"
    USER ||--o{ CONVERSATION : "starts"
    USER ||--o{ QUALITY_ASSESSMENT : "uploads"
    USER ||--o{ RECOMMENDATION : "receives"
    USER ||--o{ PRICE_ALERT : "creates"
    USER ||--o{ EXPENSE : "logs"
    USER ||--o{ RATING : "rates"
    USER ||--o{ COOPERATIVE_MEMBER : "joins"

    CROP ||--o{ FARMER_INVENTORY : "categorizes"
    CROP ||--o{ MARKET_PRICE : "priced as"
    CROP ||--o{ FORECAST : "forecasted"
    CROP ||--o{ BUYER_LISTING : "requires"

    MANDI_MARKET ||--o{ MARKET_PRICE : "records"
    MANDI_MARKET ||--o{ FORECAST : "targets"

    BUYER_PROFILE ||--o{ BUYER_LISTING : "publishes"
    BUYER_LISTING ||--o{ OFFER : "receives"
    BUYER_LISTING ||--o{ BUYER_MATCH : "matches"

    FARMER_INVENTORY ||--o{ OFFER : "offers via"
    FARMER_INVENTORY ||--o{ QUALITY_ASSESSMENT : "assessed"
    FARMER_INVENTORY ||--o{ RECOMMENDATION : "recommended for"

    CONVERSATION ||--o{ MESSAGE : "contains"

    COOPERATIVE ||--o{ COOPERATIVE_MEMBER : "includes"

    OFFER ||--o{ DEAL : "creates"
    OFFER ||--o{ RATING : "rated in"

    USER {
        string id PK
        string name
        string phone UK
        string email UK
        string password_hash
        enum role "farmer|buyer|admin"
        enum language "gu|hi|en"
        string location
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    FARMER_PROFILE {
        string id PK
        string user_id FK
        string village
        string district
        string state
        enum preferred_language
        float farm_size_acres
        string aadhaar_number
        string bank_account_number
        string ifsc_code
        datetime created_at
    }

    BUYER_PROFILE {
        string id PK
        string user_id FK
        string business_name
        enum buyer_type
        text address
        string district
        float latitude
        float longitude
        string gst_number
        string verification_status
        boolean is_active
        datetime created_at
    }

    CROP {
        string id PK
        string name
        string name_gu
        string name_hi
        enum category "cotton|groundnut"
        string unit
        text description
        boolean is_active
    }

    FARMER_INVENTORY {
        string id PK
        string farmer_id FK
        string crop_id FK
        float quantity
        string unit
        enum quality_grade "A|B|C|ungraded"
        datetime harvest_date
        boolean storage_available
        float storage_cost_per_quintal_per_day
        string village
        string district
        float latitude
        float longitude
        text notes
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    MANDI_MARKET {
        string id PK
        string name
        string name_gu
        string district
        string state
        float latitude
        float longitude
        string contact
        boolean is_active
    }

    MARKET_PRICE {
        string id PK
        string market_id FK
        string crop_id FK
        datetime price_date
        numeric min_price
        numeric max_price
        numeric modal_price
        float arrivals_tonnes
        string source
        boolean is_demo
        datetime created_at
    }

    FORECAST {
        string id PK
        string crop_id FK
        string market_id FK
        datetime forecast_date
        datetime target_date
        integer horizon_days
        numeric predicted_price
        numeric lower_bound
        numeric upper_bound
        float confidence
        string model_version
        text factors
        boolean is_demo
    }

    BUYER_LISTING {
        string id PK
        string buyer_profile_id FK
        string crop_id FK
        float min_quantity
        float max_quantity
        enum quality_requirement
        numeric offered_price
        string district
        float latitude
        float longitude
        integer delivery_days
        boolean is_active
        boolean is_demo
        datetime created_at
        datetime expires_at
    }

    BUYER_MATCH {
        string id PK
        string farmer_id FK
        string buyer_listing_id FK
        string inventory_id FK
        float match_score
        text score_breakdown
        text reason
        datetime created_at
    }

    OFFER {
        string id PK
        string farmer_id FK
        string buyer_listing_id FK
        string inventory_id FK
        numeric offered_price
        float quantity
        text message
        enum status "pending|accepted|rejected|withdrawn|completed"
        datetime created_at
        datetime updated_at
    }

    QUALITY_ASSESSMENT {
        string id PK
        string farmer_id FK
        string inventory_id FK
        string image_url
        string crop_type
        text assessment_result
        float confidence
        string suggested_grade
        text disclaimer
        string provider
        datetime created_at
    }

    RECOMMENDATION {
        string id PK
        string farmer_id FK
        string inventory_id FK
        enum action "SELL_NOW|STORE|WAIT"
        integer recommended_days
        numeric current_revenue
        numeric expected_future_revenue
        numeric storage_cost
        numeric transport_cost
        numeric quality_loss_cost
        numeric expected_net_revenue
        numeric potential_gain
        float confidence
        text explanation
        text explanation_gu
        text explanation_hi
        text agent_trace
        datetime created_at
    }

    CONVERSATION {
        string id PK
        string farmer_id FK
        string session_id
        datetime created_at
    }

    MESSAGE {
        string id PK
        string conversation_id FK
        string role "user|assistant|system"
        text message
        string agent_used
        enum language
        datetime created_at
    }

    PRICE_ALERT {
        string id PK
        string farmer_id FK
        string crop_id
        float threshold_price
        string direction "above|below"
        boolean is_active
        datetime last_triggered_at
        datetime created_at
    }

    EXPENSE {
        string id PK
        string farmer_id FK
        string crop_id
        string category
        numeric amount
        datetime incurred_date
        text notes
        datetime created_at
    }

    DEAL {
        string id PK
        string farmer_id FK
        string offer_id FK
        string status
        numeric agreed_price
        float agreed_quantity
        datetime delivery_date
        numeric transport_cost
        numeric storage_cost
        datetime created_at
        datetime updated_at
    }

    RATING {
        string id PK
        string rater_id FK
        string rated_user_id FK
        string offer_id FK
        integer score
        text comment
        datetime created_at
    }

    COOPERATIVE {
        string id PK
        string name
        string district
        string created_by FK
        datetime created_at
    }

    COOPERATIVE_MEMBER {
        string id PK
        string cooperative_id FK
        string farmer_id FK
        datetime joined_at
    }

    WEATHER_SNAPSHOT {
        string id PK
        string farmer_id FK
        string district
        datetime forecast_date
        float rainfall_mm
        float temperature_c
        float humidity_percent
        string alert
        string source
        boolean is_demo
        datetime created_at
    }
```

---

## 3. API Routing & Request Flow

```mermaid
graph LR
    CLIENT["React Frontend"]

    subgraph AUTH_FLOW["Authentication Flow"]
        LOGIN["POST /api/auth/login"]
        REGISTER["POST /api/auth/register"]
        ME["GET /api/auth/me"]
        TOKEN["JWT Bearer Token"]
    end

    subgraph PROTECTED["Protected Routes"]
        FARMER_ROUTES["/api/farmer/*"]
        AI_ROUTES["/api/ai/*"]
        BUYER_ROUTES["/api/buyers/*"]
        INTEL_ROUTES["/api/intelligence/*"]
        ADMIN_ROUTES["/api/admin/*"]
    end

    subgraph DEPS["Dependencies"]
        GET_CURRENT["get_current_user"]
        REQ_FARMER["require_farmer"]
        REQ_BUYER["require_buyer"]
        REQ_ADMIN["require_admin"]
        GET_DB["get_db"]
    end

    CLIENT --> LOGIN
    CLIENT --> REGISTER
    LOGIN --> TOKEN
    REGISTER --> TOKEN
    TOKEN --> ME

    TOKEN --> PROTECTED
    PROTECTED --> DEPS
    DEPS --> DB[(Database)]
```

---

## 4. AI Agent Orchestration Pipeline

```mermaid
graph TB
    REQ["User Request<br/>(Chat / Sell-or-Store / Quality)"]

    subgraph ORCH["Agent Orchestrator"]
        INTENT["Intent Detector"]
        ROUTE["Route to Agents"]
    end

    subgraph AGENTS["Specialized Agents"]
        MANDI["MandiPriceAgent"]
        FCST["ForecastingAgent"]
        STORE["StorageAdvisorAgent"]
        MATCH["BuyerMatchingAgent"]
        QUAL["QualityGradingAgent"]
        INC["IncomeDashboardAgent"]
    end

    subgraph LLM["LLM Layer"]
        GRANITE["IBM Granite 13B<br/>(or template fallback)"]
    end

    subgraph DATA["Data Providers"]
        MOCK["MockMarketDataProvider"]
        LIVE["AGMARKNETProvider<br/>(optional)"]
        BASE["BaselineForecastModel"]
        MOCK_QUAL["MockQualityProvider"]
    end

    REQ --> ORCH
    INTENT --> ROUTE

    ROUTE --> MANDI
    ROUTE --> FCST
    ROUTE --> STORE
    ROUTE --> MATCH
    ROUTE --> QUAL
    ROUTE --> INC

    MANDI --> MOCK
    MANDI --> LIVE
    FCST --> BASE
    FCST --> MOCK
    QUAL --> MOCK_QUAL

    MANDI --> GRANITE
    FCST --> GRANITE
    STORE --> GRANITE
    MATCH --> GRANITE
    INC --> GRANITE

    GRANITE --> RESPONSE["Structured Response<br/>+ Agent Trace"]
```

**Intent → Agent Mapping:**

| Intent | Agents Invoked |
|--------|---------------|
| `MARKET_PRICE` | MandiPriceAgent |
| `PRICE_FORECAST` | MandiPriceAgent, ForecastingAgent |
| `SELL_OR_STORE` | MandiPriceAgent, ForecastingAgent, StorageAdvisorAgent, BuyerMatchingAgent, IncomeDashboardAgent |
| `FIND_BUYER` | MandiPriceAgent, BuyerMatchingAgent |
| `QUALITY_CHECK` | QualityGradingAgent |
| `INCOME` | MandiPriceAgent, ForecastingAgent, BuyerMatchingAgent, IncomeDashboardAgent |

---

## 5. Sell-or-Store Request Flow (Deep Dive)

```mermaid
sequenceDiagram
    participant U as User
    participant F as FastAPI
    participant O as Orchestrator
    participant M as MandiPriceAgent
    participant F2 as ForecastingAgent
    participant S as StorageAdvisorAgent
    participant B as BuyerMatchingAgent
    participant I as IncomeDashboardAgent
    participant G as Granite LLM
    participant D as Database

    U->>F: POST /api/ai/recommendation
    F->>F: Validate JWT + require_farmer
    F->>O: get_full_recommendation()

    O->>M: _timed_run(crop_id, district, quantity)
    M->>D: get_current_prices()
    D-->>M: MarketPrice rows
    M-->>O: current_price, primary_market_id

    O->>F2: _timed_run(crop_id, market_id, horizon_days)
    F2->>D: get_historical_prices()
    D-->>F2: Price history
    F2-->>O: predicted_price, confidence

    O->>S: _timed_run(storage economics)
    S-->>O: action, recommended_days, net_revenue

    O->>B: _timed_run(crop_id, quantity, grade, district)
    B->>D: load BuyerListing + BuyerProfile
    D-->>B: listings
    B-->>O: matches, best_buyer

    O->>I: _timed_run(farmer, inventory, prices, forecast, buyers)
    I-->>O: revenue_scenarios, total_inventory

    O->>G: explain_recommendation(rec_data, language)
    G-->>O: granite_explanation

    O->>D: persist Recommendation row
    O-->>F: { action, revenue, buyers, trace, ... }
    F-->>U: JSON Response
```

---

## 6. Authentication & Role Guard Flow

```mermaid
graph TB
    LOGIN["POST /api/auth/login<br/>phone + password"]
    REGISTER["POST /api/auth/register<br/>name, phone, password, role"]
    TOKEN["create_access_token()<br/>JWT with sub, role, exp, iat"]

    subgraph GUARDS["Route Guards"]
        GET_CURRENT["get_current_user<br/>Extract JWT from Authorization header"]
        REQ_FARMER["require_farmer<br/>403 if role != farmer"]
        REQ_BUYER["require_buyer<br/>403 if role != buyer"]
        REQ_ADMIN["require_admin<br/>403 if role != admin"]
    end

    subgraph ROLES["User Roles"]
        FARMER_ROLE["FARMER"]
        BUYER_ROLE["BUYER"]
        ADMIN_ROLE["ADMIN"]
    end

    LOGIN --> TOKEN
    REGISTER --> TOKEN
    TOKEN --> GET_CURRENT
    GET_CURRENT --> GUARDS
    GUARDS --> ROLES

    FARMER_ROLE --> REQ_FARMER
    BUYER_ROLE --> REQ_BUYER
    ADMIN_ROLE --> REQ_ADMIN
```

---

## 7. Frontend Module → API Mapping

```mermaid
graph LR
    subgraph PAGES["Frontend Pages"]
        LANDING["LandingPage"]
        LOGIN["LoginPage"]
        REGISTER["RegisterPage"]
        DASH["DashboardPage"]
        MKT["MarketPage"]
        SOS["SellOrStorePage"]
        BUY["BuyersPage"]
        QLT["QualityPage"]
        INV["InventoryPage"]
        INC["IncomePage"]
        AI["AIAssistantPage"]
        FP["FarmPlannerPage"]
        IH["IntelligenceHubPage"]
        ADM["AdminDashboardPage"]
    end

    subgraph API_ENDPOINTS["Backend API Endpoints"]
        AUTH_EP["/api/auth/*"]
        FARMER_EP["/api/farmer/*"]
        MARKET_EP["/api/markets/*"]
        AI_EP["/api/ai/*"]
        BUYER_EP["/api/buyers/*"]
        INTEL_EP["/api/intelligence/*"]
        ADMIN_EP["/api/admin/*"]
    end

    LANDING --> AUTH_EP
    LOGIN --> AUTH_EP
    REGISTER --> AUTH_EP

    DASH --> FARMER_EP
    INV --> FARMER_EP

    MKT --> MARKET_EP

    SOS --> AI_EP

    BUY --> BUYER_EP

    QLT --> AI_EP

    INC --> INTEL_EP

    AI --> AI_EP

    FP --> FARMER_EP

    IH --> INTEL_EP

    ADM --> ADMIN_EP
```

---

## 8. Database Table Relationships Summary

```
users
  ├── farmer_profiles (1:1)
  ├── buyer_profiles (1:1)
  ├── farmer_inventory (1:N)
  ├── conversations (1:N)
  ├── quality_assessments (1:N)
  ├── recommendations (1:N)
  ├── price_alerts (1:N)
  ├── expenses (1:N)
  ├── ratings (1:N)
  └── cooperative_members (1:N)

crops
  ├── farmer_inventory (1:N)
  ├── market_prices (1:N)
  ├── forecasts (1:N)
  └── buyer_listings (1:N)

mandi_markets
  ├── market_prices (1:N)
  └── forecasts (1:N)

buyer_profiles
  └── buyer_listings (1:N)

buyer_listings
  ├── offers (1:N)
  └── buyer_matches (1:N)

farmer_inventory
  ├── offers (1:N)
  ├── quality_assessments (1:N)
  └── recommendations (1:N)

conversations
  └── messages (1:N)

cooperatives
  └── cooperative_members (1:N)

offers
  ├── deals (1:N)
  └── ratings (1:N)
```

---

## 9. Data Flow: Market Price to Dashboard

```mermaid
graph LR
    REQ["GET /api/farmer/dashboard"]
    ORCH["Orchestrator"]
    MANDI["MandiPriceAgent"]
    FCST["ForecastingAgent"]
    BUYER["BuyerMatchingAgent"]
    INCOME["IncomeDashboardAgent"]
    GRANITE["Granite LLM"]
    DB[(Database)]

    REQ --> ORCH
    ORCH --> MANDI
    MANDI --> DB
    DB --> MANDI
    MANDI --> ORCH

    ORCH --> FCST
    FCST --> DB
    DB --> FCST
    FCST --> ORCH

    ORCH --> BUYER
    BUYER --> DB
    DB --> BUYER
    BUYER --> ORCH

    ORCH --> INCOME
    INCOME --> ORCH

    ORCH --> GRANITE
    GRANITE --> ORCH

    ORCH --> RESPONSE["Dashboard JSON"]
    RESPONSE --> REQ
```

---

## 10. Key Backend Design Patterns

| Pattern | Implementation |
|---------|---------------|
| **API Gateway** | Single FastAPI app with CORS middleware |
| **Repository** | SQLAlchemy ORM models + async sessions |
| **Service Layer** | `app/services/*` for market data, forecasts, quality, Granite |
| **Agent Pattern** | `app/agents/*` with `AgentResult` base class and `_timed_run` |
| **Orchestrator** | `AgentOrchestrator` routes intents to agent pipelines |
| **Dependency Injection** | FastAPI `Depends(get_db)`, `Depends(require_farmer)` |
| **JWT Auth** | Bearer tokens with role claims + refresh guards |
| **Demo Fallback** | `is_demo` flags, mock providers, template-mode Granite |
| **Async I/O** | Async SQLAlchemy + asyncpg / SQLite |
| **Structured Logging** | `structlog` with request timing middleware |

---

*Generated from backend code in `D:\test\khedutmitra-ai\backend`*
