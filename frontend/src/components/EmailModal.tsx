import React, { useState } from 'react';
import { X, Mail, Send, CheckCircle2, AlertCircle } from 'lucide-react';
import { sendEmailNotification } from '../services/api';

interface EmailModalProps {
  isOpen: boolean;
  onClose: () => void;
  predictionDate: string;
  totalMarkets: number;
}

export const EmailModal: React.FC<EmailModalProps> = ({
  isOpen,
  onClose,
  predictionDate,
  totalMarkets,
}) => {
  const [email, setEmail] = useState('priya@iservce.onmicrosoft.com');
  const [isSending, setIsSending] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [statusMessage, setStatusMessage] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsSending(true);
    setStatus('idle');
    try {
      const res = await sendEmailNotification(email);
      setStatus('success');
      setStatusMessage(res.message || 'Daily tomato price forecast email sent successfully!');
      setTimeout(() => {
        onClose();
        setStatus('idle');
      }, 2500);
    } catch (err: any) {
      setStatus('error');
      setStatusMessage(err.message || 'Failed to dispatch email notification.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100 relative animate-in fade-in zoom-in-95 duration-150">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1 rounded-lg"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center">
            <Mail className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Send Daily Forecast Email</h3>
            <p className="text-xs text-slate-500">Automated Azure Notification Delivery</p>
          </div>
        </div>

        <div className="bg-slate-50 rounded-xl p-3 mb-5 border border-slate-200/60 text-xs text-slate-600 space-y-1">
          <p>• <strong>Target Forecast:</strong> {predictionDate}</p>
          <p>• <strong>Coverage:</strong> {totalMarkets} Karnataka APMC Mandis</p>
          <p>• <strong>Provider:</strong> Azure Communication Services / SendGrid / SMTP</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 mb-1">
              Recipient Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="user@domain.com"
              className="w-full px-3.5 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-rose-500 focus:border-rose-500"
            />
          </div>

          {status === 'success' && (
            <div className="flex items-center space-x-2 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg p-3">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>{statusMessage}</span>
            </div>
          )}

          {status === 'error' && (
            <div className="flex items-center space-x-2 text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-lg p-3">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{statusMessage}</span>
            </div>
          )}

          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-300 rounded-lg text-xs font-medium text-slate-700 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSending}
              className="inline-flex items-center px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-semibold shadow-sm focus:outline-none focus:ring-2 focus:ring-rose-500 disabled:opacity-50"
            >
              <Send className={`w-3.5 h-3.5 mr-1.5 ${isSending ? 'animate-pulse' : ''}`} />
              {isSending ? 'Dispatching...' : 'Dispatch Email Now'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

