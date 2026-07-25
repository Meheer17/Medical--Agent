'use client';

import { useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

export default function DashboardGateway() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login');
      } else if (user.role === 'PATIENT') {
        router.push('/dashboard/patient');
      } else if (user.role === 'DOCTOR') {
        router.push('/dashboard/doctor');
      } else if (user.role === 'LAB') {
        router.push('/dashboard/lab');
      }
    }
  }, [user, isLoading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-600 text-sm font-semibold">
      Loading ClinIQ Portal...
    </div>
  );
}
