import React, { useState, useMemo } from 'react';
import { PricePrediction } from '../types';
import { Search, ArrowUpDown, ChevronUp, ChevronDown, Minus, ArrowRight } from 'lucide-react';

interface MarketTableProps {
  predictions: PricePrediction[];
  selectedMarketId: string | null;
  onSelectMarket: (market: PricePrediction) => void;
}

export const MarketTable: React.FC<MarketTableProps> = ({
  predictions,
  selectedMarketId,
  onSelectMarket,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [trendFilter, setTrendFilter] = useState<'ALL' | 'UP' | 'DOWN' | 'STABLE'>('ALL');
  const [sortField, setSortField] = useState<keyof PricePrediction>('predicted_modal_price');
  const [sortAsc, setSortAsc] = useState(false);

  const filteredPredictions = useMemo(() => {
    return predictions
      .filter((p) => {
        const matchesSearch =
          p.market_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          p.district_name.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesTrend = trendFilter === 'ALL' || p.trend === trendFilter;
        return matchesSearch && matchesTrend;
      })
      .sort((a, b) => {
        const valA = a[sortField];
        const valB = b[sortField];
        if (typeof valA === 'number' && typeof valB === 'number') {
          return sortAsc ? valA - valB : valB - valA;
        }
        return sortAsc
          ? String(valA).localeCompare(String(valB))
          : String(valB).localeCompare(String(valA));
      });
  }, [predictions, searchTerm, trendFilter, sortField, sortAsc]);

  const handleSort = (field: keyof PricePrediction) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 shadow-sm overflow-hidden mb-8">
      {/* Search and Filters toolbar */}
      <div className="p-4 sm:p-5 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search Karnataka mandis or districts (e.g., Kolar, Bangalore, Ramanagara)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500 placeholder-slate-400"
          />
        </div>

        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-500 font-medium">Trend:</span>
          {(['ALL', 'UP', 'DOWN', 'STABLE'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => setTrendFilter(filter)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                trendFilter === filter
                  ? 'bg-rose-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th
                onClick={() => handleSort('market_name')}
                className="px-4 py-3.5 text-left font-semibold cursor-pointer hover:text-slate-900 select-none"
              >
                <div className="flex items-center space-x-1">
                  <span>Mandi (Market)</span>
                  <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('district_name')}
                className="px-4 py-3.5 text-left font-semibold cursor-pointer hover:text-slate-900 select-none"
              >
                <div className="flex items-center space-x-1">
                  <span>District</span>
                  <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('predicted_modal_price')}
                className="px-4 py-3.5 text-right font-semibold cursor-pointer hover:text-slate-900 select-none"
              >
                <div className="flex items-center justify-end space-x-1">
                  <span>Predicted Modal</span>
                  <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
                </div>
              </th>
              <th className="px-4 py-3.5 text-right font-semibold text-slate-500">
                Predicted Range
              </th>
              <th
                onClick={() => handleSort('percentage_change')}
                className="px-4 py-3.5 text-center font-semibold cursor-pointer hover:text-slate-900 select-none"
              >
                <div className="flex items-center justify-center space-x-1">
                  <span>Trend / Chg</span>
                  <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
                </div>
              </th>
              <th className="px-4 py-3.5 text-center font-semibold text-slate-500">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {filteredPredictions.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-10 text-slate-500">
                  No matching markets found.
                </td>
              </tr>
            ) : (
              filteredPredictions.map((p) => {
                const isSelected = selectedMarketId === p.market_id;
                return (
                  <tr
                    key={p.market_id}
                    onClick={() => onSelectMarket(p)}
                    className={`cursor-pointer transition-colors ${
                      isSelected ? 'bg-rose-50/70' : 'hover:bg-slate-50/80'
                    }`}
                  >
                    <td className="px-4 py-3 font-semibold text-slate-900">
                      <div className="flex items-center space-x-2">
                        {isSelected && <span className="w-2 h-2 rounded-full bg-rose-600"></span>}
                        <span>{p.market_name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{p.district_name}</td>
                    <td className="px-4 py-3 text-right">
                      <span className="font-bold text-rose-600 text-base">
                        ₹{p.predicted_modal_price.toFixed(0)}
                      </span>
                      <span className="text-xs text-slate-400 ml-1">/qtl</span>
                    </td>
                    <td className="px-4 py-3 text-right text-xs text-slate-500 font-mono">
                      ₹{p.predicted_min_price.toFixed(0)} - ₹{p.predicted_max_price.toFixed(0)}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {p.trend === 'UP' && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-rose-100 text-rose-700">
                          <ChevronUp className="w-3.5 h-3.5 mr-0.5" />
                          +{p.percentage_change.toFixed(1)}%
                        </span>
                      )}
                      {p.trend === 'DOWN' && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700">
                          <ChevronDown className="w-3.5 h-3.5 mr-0.5" />
                          {p.percentage_change.toFixed(1)}%
                        </span>
                      )}
                      {p.trend === 'STABLE' && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600">
                          <Minus className="w-3 h-3 mr-0.5" />
                          Stable
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectMarket(p);
                        }}
                        className="inline-flex items-center text-xs font-medium text-rose-600 hover:text-rose-800"
                      >
                        Inspect <ArrowRight className="w-3 h-3 ml-1" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <div className="p-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <span>Showing {filteredPredictions.length} of {predictions.length} markets</span>
        <span>Prices normalized per quintal (100 kg)</span>
      </div>
    </div>
  );
};

