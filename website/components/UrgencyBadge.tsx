import React from 'react';
import { QueryUrgency } from '@/types';
import { AlertTriangle, AlertCircle, Info } from 'lucide-react';

export default function UrgencyBadge({ urgency }: { urgency: QueryUrgency | string }) {
  const norm = urgency.toUpperCase();

  if (norm === 'HIGH') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-red-100 text-red-700 border border-red-300">
        <AlertTriangle className="w-3.5 h-3.5 text-red-600" /> HIGH
      </span>
    );
  }

  if (norm === 'MEDIUM') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-bold bg-amber-100 text-amber-700 border border-amber-300">
        <AlertCircle className="w-3.5 h-3.5 text-amber-600" /> MEDIUM
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-medium bg-emerald-100 text-emerald-700 border border-emerald-300">
      <Info className="w-3.5 h-3.5 text-emerald-600" /> LOW
    </span>
  );
}
