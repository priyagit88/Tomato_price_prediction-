import React, { useState } from 'react';
import { HistoricalPricePoint, PricePrediction } from '../types';
import { Calendar, DollarSign, Activity } from 'lucide-react';

interface PriceChartProps {
  history: HistoricalPricePoint[];
  prediction: PricePrediction | null;
  marketName: string;
}

export const PriceChart: React.FC<PriceChartProps> = ({ history, prediction, marketName }) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  if (!history || history.length === 0) {
    return (
      <div className="bg-white p-6 rounded-xl border border-slate-200 text-center text-slate-500 py-12">
        <Activity className="w-8 h-8 mx-auto mb-2 text-slate-400 animate-pulse" />
        <p className="text-sm">Select a market from the table below to inspect historical trend & prediction curve.</p>
      </div>
    );
  }

  // Combine history + predicted point
  const points = [...history];
  const allPrices = points.map(p => p.p_modal);
  if (prediction) {
    allPrices.push(prediction.predicted_modal_price);
  }

  const minPrice = Math.min(...allPrices) * 0.9;
  const maxPrice = Math.max(...allPrices) * 1.1;
  const priceRange = maxPrice - minPrice || 1;

  const width = 800;
  const height = 260;
  const paddingX = 40;
  const paddingY = 30;

  const getX = (index: number) => {
    const total = prediction ? points.length : points.length - 1;
    return paddingX + (index / (total || 1)) * (width - paddingX * 2);
  };

  const getY = (val: number) => {
    return height - paddingY - ((val - minPrice) / priceRange) * (height - paddingY * 2);
  };

  // Generate SVG path for historical line
  const histPathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${getX(i)} ${getY(p.p_modal)}`).join(' ');

  // Predicted point coordinates
  const predX = prediction ? getX(points.length) : null;
  const predY = prediction ? getY(prediction.predicted_modal_price) : null;
  const lastHistX = getX(points.length - 1);
  const lastHistY = getY(points[points.length - 1].p_modal);

  return (
    <div className="bg-white rounded-xl border border-slate-200/80 p-5 shadow-sm mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold text-slate-900">
              {marketName} Mandi Price Trend & Tomorrow Forecast
            </h3>
            <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700">
              ₹/Quintal
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Historical Modal Prices vs Next-Day Machine Learning Prediction Band
          </p>
        </div>

        {prediction && (
          <div className="flex items-center space-x-3 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
            <div className="text-right">
              <span className="text-[11px] uppercase tracking-wider text-slate-500 block">Predicted Modal</span>
              <span className="text-lg font-bold text-rose-600">₹{prediction.predicted_modal_price.toFixed(0)}</span>
            </div>
            <div className="h-6 w-px bg-slate-200"></div>
            <div className="text-right">
              <span className="text-[11px] uppercase tracking-wider text-slate-500 block">Band (Min - Max)</span>
              <span className="text-xs font-semibold text-slate-700">
                ₹{prediction.predicted_min_price.toFixed(0)} - ₹{prediction.predicted_max_price.toFixed(0)}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* SVG Chart */}
      <div className="relative mt-4 overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-64 overflow-visible">
          {/* Horizontal grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => {
            const y = paddingY + pct * (height - paddingY * 2);
            const val = maxPrice - pct * priceRange;
            return (
              <g key={i}>
                <line x1={paddingX} y1={y} x2={width - paddingX} y2={y} stroke="#f1f5f9" strokeWidth="1" strokeDasharray="3 3" />
                <text x={paddingX - 8} y={y + 4} textAnchor="end" fontSize="10" fill="#94a3b8">
                  ₹{val.toFixed(0)}
                </text>
              </g>
            );
          })}

          {/* Historical line */}
          <path
            d={histPathD}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Connect last historical to prediction line with dashed red */}
          {prediction && predX && predY && (
            <line
              x1={lastHistX}
              y1={lastHistY}
              x2={predX}
              y2={predY}
              stroke="#e11d48"
              strokeWidth="2"
              strokeDasharray="4 4"
            />
          )}

          {/* Historical points */}
          {points.map((p, i) => {
            const cx = getX(i);
            const cy = getY(p.p_modal);
            return (
              <circle
                key={i}
                cx={cx}
                cy={cy}
                r="3.5"
                fill="#ffffff"
                stroke="#3b82f6"
                strokeWidth="2"
                className="hover:r-5 cursor-pointer transition-all"
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
              />
            );
          })}

          {/* Prediction point */}
          {prediction && predX && predY && (
            <g>
              {/* Confidence interval vertical line */}
              <line
                x1={predX}
                y1={getY(prediction.confidence_upper)}
                x2={predX}
                y2={getY(prediction.confidence_lower)}
                stroke="#fda4af"
                strokeWidth="4"
                strokeLinecap="round"
              />
              <circle
                cx={predX}
                cy={predY}
                r="6"
                fill="#e11d48"
                stroke="#ffffff"
                strokeWidth="2"
                className="animate-pulse"
              />
            </g>
          )}
        </svg>

        {/* Legend */}
        <div className="flex items-center justify-center space-x-6 mt-3 text-xs text-slate-600">
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-0.5 bg-blue-500 rounded"></span>
            <span>Historical Modal Price</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-0.5 bg-rose-500 border-dashed border-b border-rose-500"></span>
            <span className="font-semibold text-rose-600">ML Predicted Forecast</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-2 bg-rose-200 rounded"></span>
            <span className="text-slate-500">95% Confidence Band</span>
          </div>
        </div>
      </div>
    </div>
  );
};

