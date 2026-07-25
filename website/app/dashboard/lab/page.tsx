'use client';

import React, { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import StatusBadge from '@/components/StatusBadge';
import ReportModal from '@/components/ReportModal';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';
import { LabAppointment, LabReport, AppointmentStatus } from '@/types';
import {
  TestTube,
  Upload,
  FileText,
  Calendar,
  Sparkles,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileUp,
  RotateCw,
  Check,
  CheckCheck,
  XCircle,
} from 'lucide-react';

export default function LabDashboard() {
  const { user } = useAuth();
  const [labAppointments, setLabAppointments] = useState<LabAppointment[]>([]);
  const [reports, setReports] = useState<LabReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<LabReport | null>(null);

  // Upload Modal State
  const [uploadApptId, setUploadApptId] = useState<number | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [testResultsNotes, setTestResultsNotes] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const [actionMessage, setActionMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(
    null
  );

  const fetchData = async () => {
    try {
      const [apptsRes, rptsRes] = await Promise.all([
        api.appointments.getMyLabAppointments().catch(() => []),
        api.reports.getMyReports().catch(() => []),
      ]);
      setLabAppointments(apptsRes);
      setReports(rptsRes);
    } catch (e) {
      console.error('Failed to load lab dashboard data', e);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleUpdateApptStatus = async (apptId: number, newStatus: AppointmentStatus) => {
    try {
      await api.appointments.updateLabAppointment(apptId, { status: newStatus });
      setActionMessage({ type: 'success', text: `Lab test appointment status updated to ${newStatus}` });
      fetchData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message || 'Failed to update status' });
    }
  };

  const handleUploadReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadApptId || !uploadFile) return;
    setIsUploading(true);
    setActionMessage(null);
    try {
      await api.reports.uploadReport(uploadApptId, uploadFile, testResultsNotes);
      setActionMessage({
        type: 'success',
        text: 'Lab report uploaded successfully! Gemini Vision AI is processing the PDF in the background.',
      });
      setUploadApptId(null);
      setUploadFile(null);
      setTestResultsNotes('');
      fetchData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message || 'Failed to upload report' });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Banner */}
        <div className="bg-gradient-to-r from-purple-900 via-indigo-900 to-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl relative overflow-hidden">
          <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1 text-purple-300 text-xs font-semibold uppercase tracking-wider">
                <TestTube className="w-4 h-4" /> Diagnostic Lab Portal
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold">
                {user?.full_name || user?.username} Pathology Center
              </h1>
              <p className="text-sm text-slate-300 mt-1">
                Accept lab bookings, update appointment statuses, upload PDF reports, and trigger Gemini AI vision parsing.
              </p>
            </div>
          </div>
        </div>

        {/* Global Toast */}
        {actionMessage && (
          <div
            className={`p-4 rounded-xl text-xs font-semibold flex items-center justify-between shadow-sm border ${
              actionMessage.type === 'success'
                ? 'bg-purple-50 text-purple-800 border-purple-200'
                : 'bg-red-50 text-red-800 border-red-200'
            }`}
          >
            <span>{actionMessage.text}</span>
            <button onClick={() => setActionMessage(null)} className="text-slate-500 font-bold hover:text-slate-800">
              ✕
            </button>
          </div>
        )}

        {/* Quick Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-purple-600 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">Lab Appointments</span>
              <div className="text-3xl font-extrabold text-slate-900 mt-1">{labAppointments.length}</div>
              <p className="text-xs text-slate-500 mt-1">Test slots requested by patients/doctors</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center font-bold">
              <Calendar className="w-6 h-6" />
            </div>
          </div>

          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-indigo-600 flex items-center justify-between">
            <div>
              <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">Uploaded Reports</span>
              <div className="text-3xl font-extrabold text-slate-900 mt-1">{reports.length}</div>
              <p className="text-xs text-slate-500 mt-1">Processed with Gemini Multimodal AI</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center font-bold">
              <Sparkles className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Lab Schedule, Status Updater & PDF Upload Section */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-purple-600" /> Lab Test Requests & Status Management
            </h2>
          </div>

          {labAppointments.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-xl">
              No lab test appointments found.
            </div>
          ) : (
            <div className="space-y-4">
              {labAppointments.map((appt) => {
                const hasReport = reports.some((r) => r.appointment_id === appt.id);

                return (
                  <div
                    key={appt.id}
                    className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex flex-col lg:flex-row lg:items-center justify-between gap-4"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-slate-900">{appt.test_type}</span>
                        <StatusBadge status={appt.status} />
                      </div>
                      <div className="text-xs text-slate-500">
                        Patient ID: <span className="font-semibold text-slate-700">{appt.patient_id}</span> • Date:{' '}
                        <span className="font-semibold text-slate-700">{new Date(appt.appointment_date).toLocaleString()}</span>
                      </div>
                      {appt.reason && <div className="text-xs text-slate-600">Notes: {appt.reason}</div>}
                    </div>

                    <div className="flex flex-wrap items-center gap-2 pt-2 lg:pt-0 border-t lg:border-t-0 border-slate-200">
                      {/* Status Update Buttons */}
                      {appt.status !== 'CONFIRMED' && (
                        <button
                          onClick={() => handleUpdateApptStatus(appt.id, 'CONFIRMED')}
                          className="px-3 py-1.5 bg-emerald-100 hover:bg-emerald-200 text-emerald-800 text-xs font-bold rounded-lg transition-colors flex items-center gap-1"
                        >
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Accept</span>
                        </button>
                      )}

                      {appt.status !== 'COMPLETED' && (
                        <button
                          onClick={() => handleUpdateApptStatus(appt.id, 'COMPLETED')}
                          className="px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 text-xs font-bold rounded-lg transition-colors flex items-center gap-1"
                        >
                          <CheckCheck className="w-3.5 h-3.5" />
                          <span>Mark Completed</span>
                        </button>
                      )}

                      {appt.status !== 'CANCELLED' && (
                        <button
                          onClick={() => handleUpdateApptStatus(appt.id, 'CANCELLED')}
                          className="px-3 py-1.5 bg-red-100 hover:bg-red-200 text-red-800 text-xs font-bold rounded-lg transition-colors flex items-center gap-1"
                        >
                          <XCircle className="w-3.5 h-3.5" />
                          <span>Cancel</span>
                        </button>
                      )}

                      {/* PDF Upload Button */}
                      {hasReport ? (
                        <span className="px-3 py-1.5 bg-purple-100 text-purple-800 text-xs font-bold rounded-lg border border-purple-300 flex items-center gap-1">
                          <Check className="w-3.5 h-3.5" /> PDF Uploaded
                        </span>
                      ) : (
                        <button
                          onClick={() => {
                            setUploadApptId(appt.id);
                            setUploadFile(null);
                            setTestResultsNotes('');
                          }}
                          className="px-4 py-1.5 bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold rounded-xl shadow-sm flex items-center gap-1.5"
                        >
                          <Upload className="w-3.5 h-3.5" /> Upload PDF
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>

        {/* Uploaded Reports Management */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-600" /> Lab Reports & AI Status Manager
          </h2>

          {reports.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-xl">
              No reports uploaded yet.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {reports.map((rpt) => (
                <div
                  key={rpt.id}
                  onClick={() => setSelectedReport(rpt)}
                  className="p-4 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl cursor-pointer transition-all space-y-3"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 bg-white rounded-lg border border-slate-200 text-purple-600">
                        <FileUp className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800 line-clamp-1">{rpt.file_name}</div>
                        <div className="text-[11px] text-slate-400">
                          {new Date(rpt.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>

                    <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-800 border border-indigo-200">
                      {rpt.ai_analysis_status}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 line-clamp-2 italic">
                    "{rpt.ai_summary || 'Gemini processing in background...'}"
                  </p>

                  <div className="text-[11px] text-purple-600 font-semibold flex items-center justify-between pt-2 border-t border-slate-200">
                    <span>Inspect AI Output</span>
                    <span>→</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Upload Modal */}
        {uploadApptId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
              <h3 className="text-lg font-bold text-slate-900">Upload PDF Diagnostic Report</h3>
              <p className="text-xs text-slate-500">
                Uploading a PDF file automatically triggers background Gemini Multimodal Vision AI analysis.
              </p>

              <form onSubmit={handleUploadReport} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Select PDF File</label>
                  <input
                    type="file"
                    required
                    accept="application/pdf"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setUploadFile(e.target.files[0]);
                      }
                    }}
                    className="w-full text-xs text-slate-600 file:mr-3 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Lab Notes / Results Text (Optional)
                  </label>
                  <textarea
                    rows={3}
                    value={testResultsNotes}
                    onChange={(e) => setTestResultsNotes(e.target.value)}
                    placeholder="Additional technician notes..."
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-purple-600"
                  />
                </div>

                <div className="flex gap-2 justify-end pt-2">
                  <button
                    type="button"
                    onClick={() => setUploadApptId(null)}
                    className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isUploading || !uploadFile}
                    className="px-4 py-2 text-xs font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-sm disabled:opacity-50 flex items-center gap-1.5"
                  >
                    {isUploading ? (
                      <span>Uploading & Triggering AI...</span>
                    ) : (
                      <>
                        <Upload className="w-3.5 h-3.5" />
                        <span>Upload & Analyze</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Report Details & Gemini AI Analysis */}
        <ReportModal
          report={selectedReport}
          onClose={() => setSelectedReport(null)}
          onRefresh={fetchData}
        />
      </main>

      <Footer />
    </div>
  );
}
