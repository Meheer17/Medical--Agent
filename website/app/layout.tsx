import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';

export const metadata: Metadata = {
  title: 'ClinIQ — AI-Powered Medical Agent & Healthcare Ecosystem',
  description:
    'Intelligent healthcare management connecting Patients, Doctors, and Labs with Google Gemini Multimodal Vision AI for automated medical report parsing, critical diagnostic extraction, and autonomous follow-up booking.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-full flex flex-col bg-slate-50 text-slate-900 font-sans antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
