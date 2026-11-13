import { PredictionResponse, PricePrediction, HistoricalPricePoint, MarketInfo, ModelMetrics } from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export async function fetchPredictions(): Promise<PredictionResponse> {
  const res = await fetch(`${API_BASE}/predictions`);
  if (!res.ok) throw new Error('Failed to load predictions');
  return res.json();
}

export async function fetchMarkets(): Promise<MarketInfo[]> {
  const res = await fetch(`${API_BASE}/markets`);
  if (!res.ok) throw new Error('Failed to load markets');
  return res.json();
}

export async function fetchHistoricalPrices(marketId: string, limit: number = 30): Promise<HistoricalPricePoint[]> {
  const res = await fetch(`${API_BASE}/historical/${marketId}?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to load history');
  return res.json();
}

export async function fetchModelMetrics(): Promise<ModelMetrics> {
  const res = await fetch(`${API_BASE}/model-info`);
  if (!res.ok) throw new Error('Failed to load model metrics');
  return res.json();
}

export async function triggerDailyPrediction(): Promise<any> {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error('Failed to run prediction pipeline');
  return res.json();
}

export async function sendEmailNotification(recipientEmail: string): Promise<any> {
  const res = await fetch(`${API_BASE}/notify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ recipient_email: recipientEmail }),
  });
  if (!res.ok) throw new Error('Failed to send notification email');
  return res.json();
}

