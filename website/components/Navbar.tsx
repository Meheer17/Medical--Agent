'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Stethoscope, UserCheck, TestTube, LogOut, LogIn, LayoutDashboard } from 'lucide-react';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();

  const getRoleDashboardLink = () => {
    if (!user) return '/login';
    if (user.role === 'PATIENT') return '/dashboard/patient';
    if (user.role === 'DOCTOR') return '/dashboard/doctor';
    if (user.role === 'LAB') return '/dashboard/lab';
    return '/dashboard';
  };

  const getRoleBadge = () => {
    if (!user) return null;
    if (user.role === 'PATIENT') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 border border-blue-300">
          <UserCheck className="w-3.5 h-3.5" /> Patient
        </span>
      );
    }
    if (user.role === 'DOCTOR') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-700 border border-emerald-300">
          <Stethoscope className="w-3.5 h-3.5" /> Doctor
        </span>
      );
    }
    if (user.role === 'LAB') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-700 border border-purple-300">
          <TestTube className="w-3.5 h-3.5" /> Diagnostic Lab
        </span>
      );
    }
    return null;
  };

  return (
    <header className="sticky top-0 z-50 glass-nav border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform duration-200">
            <Stethoscope className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900 bg-clip-text text-transparent">
                ClinIQ
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-bold tracking-wider uppercase bg-gradient-to-r from-blue-600 to-teal-500 text-white rounded">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-medium -mt-1">Healthcare Agent</p>
          </div>
        </Link>

        {/* Navigation Actions */}
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <>
              <div className="hidden md:flex items-center gap-3 pr-3 border-r border-slate-200">
                <div className="text-right">
                  <div className="text-sm font-semibold text-slate-800">
                    {user?.full_name || user?.username}
                  </div>
                  <div className="text-xs text-slate-500">{user?.email}</div>
                </div>
                {getRoleBadge()}
              </div>

              <Link
                href={getRoleDashboardLink()}
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm shadow-blue-600/20 transition-colors"
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>Dashboard</span>
              </Link>

              <button
                onClick={logout}
                className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                title="Sign out"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-slate-700 hover:text-blue-600 hover:bg-slate-100/80 rounded-lg transition-colors"
              >
                <LogIn className="w-4 h-4" />
                <span>Sign In</span>
              </Link>
              <Link
                href="/signup"
                className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 rounded-lg shadow-md shadow-blue-500/20 transition-all duration-200"
              >
                <span>Get Started</span>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
