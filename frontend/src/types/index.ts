export interface PricePrediction {
  market_id: string;
  market_name: string;
  district_name: string;
  prediction_date: string;
  predicted_modal_price: number;
  predicted_min_price: number;
  predicted_max_price: number;
  confidence_lower: number;
  confidence_upper: number;
  percentage_change: number;
  trend: 'UP' | 'DOWN' | 'STABLE';
}

export interface PredictionResponse {
  generated_at: string;
  prediction_date: string;
  total_markets: number;
  average_predicted_price: number;
  predictions: PricePrediction[];
}

export interface HistoricalPricePoint {
  date: string;
  market_id: string;
  market_name: string;
  district_name: string;
  p_min: number;
  p_max: number;
  p_modal: number;
}

export interface MarketInfo {
  market_id: string;
  market_name: string;
  district_name: string;
  state_name: string;
  commodity: string;
  variety: string;
}

export interface ModelMetrics {
  model_name: string;
  algorithm: string;
  trained_at?: string;
  mae?: number;
  rmse?: number;
  r2_score?: number;
  status?: string;
  features_count?: number;
}

