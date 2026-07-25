'use client';

import React from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import {
  Stethoscope,
  Sparkles,
  Bot,
  UserCheck,
  TestTube,
  FileCheck,
  Calendar,
  MessageSquareText,
  ArrowRight,
  Zap,
  ShieldAlert,
} from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-100/60 via-slate-50 to-indigo-100/40 pointer-events-none" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-bold bg-gradient-to-r from-blue-600/10 via-indigo-600/10 to-teal-500/10 text-blue-700 border border-blue-200/80 mb-6 animate-glow">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span>Next-Gen Gemini 3.6 Multimodal Medical AI Agent</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.15] mb-6">
              AI-Powered Healthcare Ecosystem for{' '}
              <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-teal-600 bg-clip-text text-transparent">
                Patients, Doctors & Labs
              </span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed mb-8">
              ClinIQ automates diagnostic PDF report parsing, extracts abnormal medical parameters with Gemini Vision AI, and autonomously schedules follow-up doctor appointments when critical health parameters are detected.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link
                href="/signup"
                className="px-6 py-3.5 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg shadow-blue-500/25 transition-all duration-200 flex items-center gap-2"
              >
                <span>Get Started Now</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/login"
                className="px-6 py-3.5 rounded-xl font-semibold text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 hover:border-slate-400 shadow-sm transition-all duration-200"
              >
                <span>Sign In to Portal</span>
              </Link>
            </div>
          </div>

          {/* Key Features Grid */}
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Patient Role Card */}
            <div className="glass-card rounded-2xl p-6 border-t-4 border-t-blue-600 hover:shadow-xl transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center mb-4">
                <UserCheck className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Patient Portal</h3>
              <p className="text-sm text-slate-600 mb-4 leading-relaxed">
                Connect with your doctor via shareable Doctor Code (`DOC...`), track appointments, view AI-analyzed lab reports with abnormal value highlights, and send urgent health queries.
              </p>
              <div className="text-xs font-semibold text-blue-600 flex items-center gap-1">
                <span>Explore Patient Role</span> →
              </div>
            </div>

            {/* Doctor Role Card */}
            <div className="glass-card rounded-2xl p-6 border-t-4 border-t-emerald-600 hover:shadow-xl transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-4">
                <Stethoscope className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Doctor Portal</h3>
              <p className="text-sm text-slate-600 mb-4 leading-relaxed">
                Generate shareable Doctor Codes, manage linked patient rosters, inspect complete lab report histories with AI summaries, prescribe tests, and reply to health queries by urgency.
              </p>
              <div className="text-xs font-semibold text-emerald-600 flex items-center gap-1">
                <span>Explore Doctor Role</span> →
              </div>
            </div>

            {/* Diagnostic Lab Role Card */}
            <div className="glass-card rounded-2xl p-6 border-t-4 border-t-purple-600 hover:shadow-xl transition-all duration-300">
              <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center mb-4">
                <TestTube className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Diagnostic Lab Portal</h3>
              <p className="text-sm text-slate-600 mb-4 leading-relaxed">
                Manage diagnostic test schedules, upload official patient PDF reports, and automatically trigger background Gemini Multimodal Vision AI parsing and parameter extraction.
              </p>
              <div className="text-xs font-semibold text-purple-600 flex items-center gap-1">
                <span>Explore Diagnostic Lab</span> →
              </div>
            </div>
          </div>

          {/* AI Workflow Section */}
          <div className="mt-20 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white rounded-3xl p-8 lg:p-12 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />
            
            <div className="max-w-3xl mb-8">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-500/20 text-blue-300 border border-blue-400/30 mb-3">
                <Bot className="w-4 h-4 text-blue-400" /> Autonomous Agentic Workflow
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
                How Gemini AI Automates Healthcare Follow-ups
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
                <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold text-sm mb-3">
                  1
                </div>
                <h4 className="font-semibold text-white text-sm mb-1">PDF Upload</h4>
                <p className="text-xs text-slate-400">Lab uploads PDF test report to appointment record.</p>
              </div>

              <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-sm mb-3">
                  2
                </div>
                <h4 className="font-semibold text-white text-sm mb-1">Vision OCR</h4>
                <p className="text-xs text-slate-400">PyMuPDF converts pages to images for Gemini Vision analysis.</p>
              </div>

              <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
                <div className="w-8 h-8 rounded-lg bg-purple-600 text-white flex items-center justify-center font-bold text-sm mb-3">
                  3
                </div>
                <h4 className="font-semibold text-white text-sm mb-1">Parameter Extract</h4>
                <p className="text-xs text-slate-400">AI flags abnormal values and assesses Criticality Index.</p>
              </div>

              <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
                <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold text-sm mb-3">
                  4
                </div>
                <h4 className="font-semibold text-white text-sm mb-1">Auto Booking</h4>
                <p className="text-xs text-slate-400">If abnormal, AI agent executes function call to book doctor.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
