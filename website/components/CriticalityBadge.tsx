import React from 'react';
import { AlertOctagon, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function CriticalityBadge({ criticality }: { criticality?: string }) {
  const norm = (criticality || 'low').toLowerCase();

  if (norm === 'critical') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-red-600 text-white shadow-sm shadow-red-600/30 animate-pulse">
        <AlertOctagon className="w-4 h-4" /> CRITICAL ABNORMALITY
      </span>
    );
  }

  if (norm === 'medium') {
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500 text-white shadow-sm shadow-amber-500/30">
        <AlertTriangle className="w-4 h-4" /> MODERATE ATTENTION
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-600 text-white shadow-sm">
      <ShieldCheck className="w-4 h-4" /> NORMAL / LOW RISK
    </span>
  );
}
