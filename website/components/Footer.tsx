import React from 'react';
import { Stethoscope, ShieldCheck, Cpu } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-400 py-12 border-t border-slate-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                <Stethoscope className="w-5 h-5" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">ClinIQ</span>
            </div>
            <p className="text-sm text-slate-400 max-w-sm mb-4">
              AI-Powered Medical Agent & Healthcare Ecosystem. Harnessing Google Gemini Multimodal Vision AI for diagnostic parsing, autonomous follow-up booking, and intelligent care coordination.
            </p>
            <div className="flex items-center gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1"><Cpu className="w-3.5 h-3.5 text-blue-400" /> Powered by Gemini 3.6 Flash</span>
              <span className="flex items-center gap-1"><ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Secure HIPAA Ready</span>
            </div>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">Roles</h4>
            <ul className="space-y-2 text-sm">
              <li><span className="hover:text-white transition-colors cursor-pointer">Patient Portal</span></li>
              <li><span className="hover:text-white transition-colors cursor-pointer">Doctor Portal</span></li>
              <li><span className="hover:text-white transition-colors cursor-pointer">Diagnostic Lab Portal</span></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">AI Capabilities</h4>
            <ul className="space-y-2 text-sm">
              <li><span>PDF Multimodal Vision OCR</span></li>
              <li><span>Abnormal Parameter Extraction</span></li>
              <li><span>Autonomous Agentic Booking</span></li>
              <li><span>Urgency Query Desk</span></li>
            </ul>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
          <p>© {new Date().getFullYear()} ClinIQ Healthcare Ecosystem. All rights reserved.</p>
          <p className="mt-2 sm:mt-0">Built with FastAPI, Google Gemini AI, Next.js & MongoDB.</p>
        </div>
      </div>
    </footer>
  );
}
