import React from 'react';
import { RefreshCw, Mail, Sparkles, Cloud } from 'lucide-react';

interface HeaderProps {
  onRefresh: () => void;
  onOpenEmail: () => void;
  isPredicting: boolean;
  predictionDate: string;
}

export const Header: React.FC<HeaderProps> = ({
  onRefresh,
  onOpenEmail,
  isPredicting,
  predictionDate,
}) => {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-rose-600 to-red-500 flex items-center justify-center text-white shadow-md shadow-rose-200">
            <span className="text-2xl">🍅</span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">
                Tomato Price Prediction
              </h1>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-rose-100 text-rose-700">
                Azure ML 2.0
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Karnataka Mandis • Automated Daily Forecasting Pipeline • Forecast Date: <strong className="text-slate-700">{predictionDate || 'Tomorrow'}</strong>
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onRefresh}
            disabled={isPredicting}
            className="inline-flex items-center px-3.5 py-2 border border-slate-300 rounded-lg shadow-sm text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-rose-500 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-4 h-4 mr-2 text-slate-500 ${isPredicting ? 'animate-spin' : ''}`} />
            {isPredicting ? 'Inferring...' : 'Run Daily ETL'}
          </button>

          <button
            onClick={onOpenEmail}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-700 hover:to-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-rose-500 transition-all shadow-rose-200 shadow-md"
          >
            <Mail className="w-4 h-4 mr-2" />
            Send Email Notification
          </button>
        </div>
      </div>
    </header>
  );
};

