'use client';

import React, { useState } from 'react';
import { LabReport } from '@/types';
import CriticalityBadge from './CriticalityBadge';
import { api } from '@/lib/api';
import {
  X,
  FileText,
  Sparkles,
  Download,
  AlertTriangle,
  RotateCw,
  Stethoscope,
  Info,
  CheckCircle,
} from 'lucide-react';

interface ReportModalProps {
  report: LabReport | null;
  onClose: () => void;
  onRefresh?: () => void;
}

export default function ReportModal({ report, onClose, onRefresh }: ReportModalProps) {
  const [isReanalyzing, setIsReanalyzing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  if (!report) return null;

  // Safe parsing for JSON stored fields
  let parsedAbnormal: string[] = [];
  try {
    if (report.ai_abnormal_values) {
      if (typeof report.ai_abnormal_values === 'string') {
        parsedAbnormal = JSON.parse(report.ai_abnormal_values);
      } else {
        parsedAbnormal = report.ai_abnormal_values;
      }
    }
  } catch {
    parsedAbnormal = [report.ai_abnormal_values || ''];
  }

  let parsedFindings: string[] = [];
  try {
    if (report.ai_key_findings) {
      if (typeof report.ai_key_findings === 'string') {
        parsedFindings = JSON.parse(report.ai_key_findings);
      } else {
        parsedFindings = report.ai_key_findings;
      }
    }
  } catch {
    parsedFindings = [report.ai_key_findings || ''];
  }

  const handleReanalyze = async () => {
    setIsReanalyzing(true);
    setMessage(null);
    try {
      await api.reports.reanalyzeReport(report.appointment_id);
      setMessage('AI analysis re-triggered in background. Refreshing in a few seconds...');
      setTimeout(() => {
        if (onRefresh) onRefresh();
        setIsReanalyzing(false);
      }, 3000);
    } catch (e: any) {
      setMessage(e.message || 'Failed to re-trigger analysis');
      setIsReanalyzing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm overflow-y-auto">
      <div className="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden my-8 border border-slate-200">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white p-6 relative">
          <button
            onClick={onClose}
            className="absolute top-5 right-5 w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          
          <div className="flex items-center gap-2.5 mb-2">
            <span className="p-2 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-400/30">
              <FileText className="w-5 h-5" />
            </span>
            <h2 className="text-xl font-bold">{report.file_name}</h2>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-300 mt-2">
            <span>Uploaded: {new Date(report.created_at).toLocaleDateString()}</span>
            <span>•</span>
            <span>Size: {(report.file_size / 1024).toFixed(1)} KB</span>
            <span>•</span>
            <CriticalityBadge criticality={report.ai_criticality} />
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
          {message && (
            <div className="p-3 bg-blue-50 border border-blue-200 text-blue-800 text-xs font-medium rounded-lg flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-600 flex-shrink-0" />
              <span>{message}</span>
            </div>
          )}

          {/* AI Banner */}
          <div className="bg-gradient-to-r from-indigo-50 via-purple-50 to-blue-50 p-4 rounded-xl border border-indigo-100 flex items-start gap-3">
            <div className="p-2 bg-indigo-600 text-white rounded-lg flex-shrink-0 mt-0.5">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-indigo-950 flex items-center gap-2">
                Gemini Vision Multimodal Analysis
                <span className="text-[10px] bg-indigo-200 text-indigo-800 font-semibold px-2 py-0.5 rounded-full uppercase">
                  {report.ai_analysis_status}
                </span>
              </h3>
              <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                {report.ai_summary || 'Analysis is currently processing in the background...'}
              </p>
            </div>
          </div>

          {/* Abnormal Values Highlight */}
          {parsedAbnormal.length > 0 && (
            <div className="bg-red-50/80 border border-red-200 rounded-xl p-4">
              <h4 className="text-xs font-bold text-red-800 uppercase tracking-wider flex items-center gap-1.5 mb-2.5">
                <AlertTriangle className="w-4 h-4 text-red-600" />
                Detected Abnormalities ({parsedAbnormal.length})
              </h4>
              <div className="flex flex-wrap gap-2">
                {parsedAbnormal.map((item, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-white text-red-700 font-semibold text-xs rounded-lg border border-red-200 shadow-sm"
                  >
                    ⚠️ {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Key Medical Findings */}
          {parsedFindings.length > 0 && (
            <div>
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <CheckCircle className="w-4 h-4 text-emerald-600" /> Key Diagnostic Parameters
              </h4>
              <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-700">
                {parsedFindings.map((finding, i) => (
                  <li key={i} className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-600 flex-shrink-0" />
                    <span>{finding}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Clinical Significance */}
          {report.ai_clinical_significance && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
              <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-1">
                Clinical Context & Guidance
              </h4>
              <p className="text-xs text-slate-700 leading-relaxed">
                {report.ai_clinical_significance}
              </p>
            </div>
          )}

          {/* Official Doctor Recommendation */}
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
            <Stethoscope className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold text-amber-900 uppercase tracking-wider">
                Physician Advisory
              </h4>
              <p className="text-xs text-amber-800 mt-0.5">
                {report.ai_doctor_recommendation ||
                  'Patient should consult their physician for clinical correlation of these findings.'}
              </p>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="bg-slate-50 px-6 py-4 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
          <button
            onClick={handleReanalyze}
            disabled={isReanalyzing}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-100 disabled:opacity-50 transition-colors"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isReanalyzing ? 'animate-spin' : ''}`} />
            <span>Re-analyze with Gemini</span>
          </button>

          <a
            href={api.reports.getDownloadUrl(report.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm shadow-blue-600/20 transition-colors ml-auto"
          >
            <Download className="w-4 h-4" />
            <span>Download Original PDF</span>
          </a>
        </div>
      </div>
    </div>
  );
}
