import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { AzureServicesBadge } from './components/AzureServicesBadge';
import { KpiCards } from './components/KpiCards';
import { PriceChart } from './components/PriceChart';
import { MarketTable } from './components/MarketTable';
import { EmailModal } from './components/EmailModal';
import {
  fetchPredictions,
  fetchHistoricalPrices,
  fetchModelMetrics,
  triggerDailyPrediction,
} from './services/api';
import { PredictionResponse, PricePrediction, HistoricalPricePoint, ModelMetrics } from './types';
import { Loader2, AlertCircle } from 'lucide-react';

export const App: React.FC = () => {
  const [data, setData] = useState<PredictionResponse | null>(null);
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [selectedMarket, setSelectedMarket] = useState<PricePrediction | null>(null);
  const [history, setHistory] = useState<HistoricalPricePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [isPredicting, setIsPredicting] = useState(false);
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [preds, modelMeta] = await Promise.all([
        fetchPredictions(),
        fetchModelMetrics().catch(() => null),
      ]);
      setData(preds);
      setMetrics(modelMeta);

      // Default select the first market (e.g. Kolar or Bangalore)
      if (preds.predictions && preds.predictions.length > 0) {
        const initialMarket = preds.predictions[0];
        setSelectedMarket(initialMarket);
        loadMarketHistory(initialMarket.market_id);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to connect to backend prediction service.');
    } finally {
      setLoading(false);
    }
  };

  const loadMarketHistory = async (marketId: string) => {
    try {
      const hist = await fetchHistoricalPrices(marketId, 30);
      setHistory(hist);
    } catch (err) {
      console.error('Failed to load market history:', err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectMarket = (m: PricePrediction) => {
    setSelectedMarket(m);
    loadMarketHistory(m.market_id);
  };

  const handleRunEtl = async () => {
    try {
      setIsPredicting(true);
      await triggerDailyPrediction();
      await loadData();
    } catch (err: any) {
      alert('Error triggering prediction pipeline: ' + err.message);
    } finally {
      setIsPredicting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Header
        onRefresh={handleRunEtl}
        onOpenEmail={() => setIsEmailModalOpen(true)}
        isPredicting={isPredicting}
        predictionDate={data?.prediction_date || ''}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Azure Services Orchestration Banner */}
        <AzureServicesBadge />

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-center space-x-3 text-amber-800 text-sm">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
            <div className="flex-1">
              <strong>Connection Notice:</strong> {error}
            </div>
            <button
              onClick={loadData}
              className="px-3 py-1 bg-amber-200 hover:bg-amber-300 rounded text-xs font-semibold text-amber-900"
            >
              Retry
            </button>
          </div>
        )}

        {loading ? (
          <div className="flex flex-col items-center justify-center py-24 text-slate-500">
            <Loader2 className="w-8 h-8 animate-spin text-rose-600 mb-3" />
            <p className="text-sm font-medium">Loading Karnataka Mandi Price Forecasts & Azure Models...</p>
          </div>
        ) : (
          <>
            {/* KPI Cards */}
            <KpiCards data={data} metrics={metrics} />

            {/* Time-Series Chart */}
            <PriceChart
              history={history}
              prediction={selectedMarket}
              marketName={selectedMarket?.market_name || 'Market'}
            />

            {/* Mandi Forecast Table */}
            <MarketTable
              predictions={data?.predictions || []}
              selectedMarketId={selectedMarket?.market_id || null}
              onSelectMarket={handleSelectMarket}
            />
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <div>
            Built with <strong>Azure Machine Learning, Docker, Azure DevOps & Terraform</strong>
          </div>
          <div>
            User: <code className="text-slate-700 bg-slate-100 px-1.5 py-0.5 rounded">priya@iservce.onmicrosoft.com</code> • Karnataka APMC Tomato Price Prediction
          </div>
        </div>
      </footer>

      {/* Email Modal */}
      <EmailModal
        isOpen={isEmailModalOpen}
        onClose={() => setIsEmailModalOpen(false)}
        predictionDate={data?.prediction_date || ''}
        totalMarkets={data?.total_markets || 0}
      />
    </div>
  );
};

export default App;

