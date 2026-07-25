import React from 'react';
import { AppointmentStatus } from '@/types';
import { Clock, CheckCircle2, XCircle, CheckCheck } from 'lucide-react';

export default function StatusBadge({ status }: { status: AppointmentStatus | string }) {
  const normalized = status.toUpperCase();

  if (normalized === 'SCHEDULED') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
        <Clock className="w-3.5 h-3.5" /> Scheduled
      </span>
    );
  }

  if (normalized === 'CONFIRMED') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
        <CheckCircle2 className="w-3.5 h-3.5" /> Confirmed
      </span>
    );
  }

  if (normalized === 'COMPLETED') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-300">
        <CheckCheck className="w-3.5 h-3.5" /> Completed
      </span>
    );
  }

  if (normalized === 'CANCELLED') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700 border border-red-200">
        <XCircle className="w-3.5 h-3.5" /> Cancelled
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-600">
      {status}
    </span>
  );
}
