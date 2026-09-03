// KhedutMitra AI — TypeScript Types

export type Language = 'en' | 'gu' | 'hi'
export type UserRole = 'farmer' | 'buyer' | 'admin'
export type CropCategory = 'cotton' | 'groundnut'
export type QualityGrade = 'A' | 'B' | 'C' | 'ungraded'
export type RecommendationAction = 'SELL_NOW' | 'STORE' | 'WAIT'
export type OfferStatus = 'pending' | 'accepted' | 'rejected' | 'withdrawn' | 'completed'

export interface User {
  id: string
  name: string
  phone: string
  email?: string
  role: UserRole
  language: Language
  location?: string
  is_active: boolean
  created_at: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

export interface Crop {
  id: string
  name: string
  name_gu?: string
  name_hi?: string
  category: CropCategory
  unit: string
}

export interface InventoryItem {
  id: string
  farmer_id: string
  crop: Crop
  quantity: number
  unit: string
  quality_grade: QualityGrade
  harvest_date?: string
  storage_available: boolean
  storage_cost_per_quintal_per_day: number
  village?: string
  district?: string
  is_active: boolean
  created_at: string
}

export interface PriceData {
  crop_id: string
  crop_name: string
  primary_market_id: string
  primary_market_name: string
  current_price: number
  min_price: number
  max_price: number
  avg_price_across_mandis: number
  best_market_name: string
  best_market_price: number
  trend: 'upward' | 'downward' | 'stable'
  trend_percentage: number
  data_timestamp: string
  source: string
  confidence: number
  current_revenue: number
  nearby_mandis: NearbyMandi[]
  price_history_14d: PricePoint[]
  is_demo: boolean
  anomaly_detected: boolean
}

export interface NearbyMandi {
  market_id: string
  market_name: string
  modal_price: number
  min_price: number
  max_price: number
  arrivals_tonnes: number
}

export interface PricePoint {
  date: string
  price: number
}

export interface ForecastData {
  crop_id: string
  market_id: string
  horizon_days: number
  predicted_price: number
  lower_bound: number
  upper_bound: number
  confidence: number
  model_version: string
  factors?: string
  target_date: string
  forecast_series: ForecastPoint[]
  is_demo: boolean
  disclaimer: string
}

export interface ForecastPoint {
  horizon_days: number
  target_date: string
  predicted_price: number
  lower_bound: number
  upper_bound: number
  confidence: number
}

export interface AgentTrace {
  agent: string
  status: string
  latency_ms?: number
  label?: string
  error?: string | null
}

export interface RecommendationResult {
  action: RecommendationAction
  recommended_days?: number
  current_price: number
  current_revenue: number
  forecast_price: number
  forecast_confidence: number
  forecast_lower: number
  forecast_upper: number
  expected_future_revenue: number
  storage_cost: number
  transport_cost: number
  quality_loss_cost: number
  expected_net_revenue: number
  potential_gain: number
  confidence: number
  reasoning: string
  granite_explanation: string
  best_buyer?: BuyerMatch
  buyer_matches: BuyerMatch[]
  agent_trace: AgentTrace[]
  forecast_series: ForecastPoint[]
  income_data: IncomeSummary
  crop_name: string
  is_demo: boolean
  disclaimer: string
}

export interface BuyerMatch {
  listing_id: string
  buyer_name: string
  buyer_type: string
  crop_name: string
  offered_price: number
  min_quantity: number
  max_quantity: number
  quality_requirement: string
  district?: string
  distance_km: number
  delivery_days: number
  match_score: number
  score_breakdown: Record<string, number>
  reason: string
  contact_phone?: string
  is_demo: boolean
}

export interface IncomeSummary {
  farmer_name: string
  district?: string
  total_inventory_quintals: number
  cotton_quintals: number
  groundnut_quintals: number
  current_estimated_value: number
  expected_value_7d: number
  potential_gain: number
  active_buyer_opportunities: number
  revenue_scenarios: RevenueScenario[]
  recommendation_action: RecommendationAction
  top_buyers: BuyerMatch[]
}

export interface RevenueScenario {
  label: string
  gross_revenue: number
  net_revenue: number
  horizon_days: number
}

export interface DashboardData {
  farmer_name: string
  district?: string
  total_inventory_quintals: number
  cotton_quintals: number
  groundnut_quintals: number
  current_estimated_value: number
  expected_value_7d: number
  potential_gain: number
  active_buyer_opportunities: number
  current_price: number
  forecast_price_7d: number
  recommendation_action: RecommendationAction
  revenue_scenarios: RevenueScenario[]
  top_buyers: BuyerMatch[]
  is_demo: boolean
}

export interface QualityAssessmentResult {
  suggested_grade: string
  confidence: number
  crop_type: string
  assessment_details: Record<string, string>
  disclaimer: string
  provider: string
  is_demo: boolean
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  language: Language
  agent_trace?: AgentTrace[]
}

export interface ChatResponse {
  reply: string
  language: Language
  intent?: string
  agent_trace: AgentTrace[]
  structured_data?: Record<string, unknown>
  session_id: string
  is_demo: boolean
}
