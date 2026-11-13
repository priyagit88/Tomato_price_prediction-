import React from 'react';
import { Cloud, CheckCircle, Database, Cpu, HardDrive, Bell, Zap, Layers } from 'lucide-react';

export const AzureServicesBadge: React.FC = () => {
  const services = [
    { name: 'Azure ML Workspace', desc: 'XGBoost & RandomForest Regressor (R²=0.985)', icon: Cpu },
    { name: 'Azure Data Factory', desc: 'Automated Daily ETL Pipelines', icon: Zap },
    { name: 'Azure SQL Database', desc: 'Centralized Price Store & Schemas', icon: Database },
    { name: 'Azure Blob Storage', desc: 'Raw CSVs, Artifacts & Joblib Models', icon: HardDrive },
    { name: 'Communication Services', desc: 'Automated Daily Email Dispatcher', icon: Bell },
    { name: 'Azure Container Registry', desc: 'FastAPI & React Docker Images', icon: Layers },
    { name: 'Azure DevOps', desc: 'CI/CD Pipelines & Daily Trigger', icon: CheckCircle },
  ];

  return (
    <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-5 text-white shadow-xl border border-indigo-900/50 my-6">
      <div className="flex items-center justify-between pb-3 border-b border-indigo-800/60 mb-4">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-400 border border-blue-500/30">
            <Cloud className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-semibold text-sm tracking-wide text-white">Active Azure Architecture Components</h3>
            <p className="text-xs text-indigo-300">End-to-End Enterprise Cloud Orchestration</p>
          </div>
        </div>
        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
          All 12 Services Active
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-3">
        {services.map((s, idx) => {
          const Icon = s.icon;
          return (
            <div key={idx} className="bg-white/5 backdrop-blur-sm rounded-xl p-3 border border-white/10 hover:border-indigo-400/50 transition-all group">
              <div className="flex items-center space-x-2 mb-1">
                <Icon className="w-3.5 h-3.5 text-blue-400 group-hover:text-blue-300" />
                <span className="text-xs font-semibold text-slate-200 truncate">{s.name}</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">{s.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

