'use client';

import React, { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import StatusBadge from '@/components/StatusBadge';
import UrgencyBadge from '@/components/UrgencyBadge';
import ReportModal from '@/components/ReportModal';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';
import {
  PatientProfile,
  DoctorAppointment,
  LabAppointment,
  LabReport,
  HealthQuery,
  User,
  QueryUrgency,
} from '@/types';
import {
  Stethoscope,
  Link2,
  Unlink,
  Calendar,
  TestTube,
  FileText,
  MessageSquare,
  Plus,
  Sparkles,
  AlertTriangle,
  Clock,
  Send,
  UserCheck,
  CheckCircle,
} from 'lucide-react';

const COMMON_LAB_TESTS = [
  'Complete Blood Count (CBC)',
  'Lipid Profile (Cholesterol & Triglycerides)',
  'Thyroid Function Panel (T3, T4, TSH)',
  'Fasting Blood Glucose & HbA1c',
  'Liver Function Test (LFT)',
  'Kidney / Renal Function Test (KFT)',
  'Comprehensive Metabolic Panel (CMP)',
  'Vitamin D3 & Vitamin B12 Panel',
  'Urinalysis & Urine Routine',
  'Custom / Other Diagnostic Test',
];

export default function PatientDashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<PatientProfile | null>(null);
  const [doctors, setDoctors] = useState<User[]>([]);
  const [labs, setLabs] = useState<User[]>([]);
  const [doctorAppointments, setDoctorAppointments] = useState<DoctorAppointment[]>([]);
  const [labAppointments, setLabAppointments] = useState<LabAppointment[]>([]);
  const [reports, setReports] = useState<LabReport[]>([]);
  const [queries, setQueries] = useState<HealthQuery[]>([]);

  const [doctorCodeInput, setDoctorCodeInput] = useState('');
  const [selectedReport, setSelectedReport] = useState<LabReport | null>(null);

  // Doctor Consultation Modal
  const [showDoctorApptModal, setShowDoctorApptModal] = useState(false);
  const [selectedDoctorId, setSelectedDoctorId] = useState<number | null>(null);
  const [doctorApptDate, setDoctorApptDate] = useState('');
  const [doctorApptReason, setDoctorApptReason] = useState('');

  // Lab Appointment Modal
  const [showLabApptModal, setShowLabApptModal] = useState(false);
  const [selectedLabId, setSelectedLabId] = useState<number | null>(null);
  const [labTestPreset, setLabTestPreset] = useState<string>(COMMON_LAB_TESTS[0]);
  const [labCustomTest, setLabCustomTest] = useState('');
  const [labApptDate, setLabApptDate] = useState('');
  const [labApptReason, setLabApptReason] = useState('');

  // Query Modal
  const [showQueryModal, setShowQueryModal] = useState(false);
  const [queryText, setQueryText] = useState('');
  const [queryUrgency, setQueryUrgency] = useState<QueryUrgency>('MEDIUM');

  const [actionMessage, setActionMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(
    null
  );

  const fetchData = async () => {
    try {
      const [profData, docsData, labsData, docAppts, labAppts, rpts, qrs] = await Promise.all([
        api.profiles.getMe().catch(() => null),
        api.profiles.getDoctors().catch(() => []),
        api.profiles.getLabs().catch(() => []),
        api.appointments.getMyDoctorAppointments().catch(() => []),
        api.appointments.getMyLabAppointments().catch(() => []),
        api.reports.getMyReports().catch(() => []),
        api.queries.getQueries().catch(() => []),
      ]);

      if (profData) setProfile(profData);
      setDoctors(docsData);
      setLabs(labsData);
      setDoctorAppointments(docAppts);
      setLabAppointments(labAppts);
      setReports(rpts);
      setQueries(qrs);
    } catch (e) {
      console.error('Failed to load patient dashboard data', e);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleLinkDoctor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!doctorCodeInput.trim()) return;
    setActionMessage(null);
    try {
      const res = await api.profiles.linkDoctor(doctorCodeInput.trim());
      setActionMessage({ type: 'success', text: res.message || 'Successfully linked to doctor!' });
      setDoctorCodeInput('');
      fetchData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message || 'Failed to link doctor' });
    }
  };

  const handleUnlinkDoctor = async () => {
    setActionMessage(null);
    try {
      const res = await api.profiles.unlinkDoctor();
      setActionMessage({ type: 'success', text: res.message || 'Unlinked doctor' });
      fetchData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message || 'Failed to unlink doctor' });
    }
  };

  const handleBookDoctorAppt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDoctorId || !doctorApptDate) return;
    setActionMessage(null);
    try {
      await api.appointments.createDoctorAppointment({
        doctor_id: selectedDoctorId,
        appointment_date: new Date(doctorApptDate).toISOString(),
        reason: doctorApptReason,
      });
      setActionMessage({ type: 'success', text: 'Doctor consultation scheduled!' });
      setShowDoctorApptModal(false);
      setDoctorApptReason('');
      setDoctorApptDate('');
      fetchData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message || 'Failed to book appointment' });
    }
  };

  const handleBookLabAppt = async (e: React.FormEvent) => {
    e.preventDefault();
    const finalTestType =
      labTestPreset === 'Custom / Other Diagnostic Test'
        ? labCustomTest.trim()
        : labTestPreset;

    if (!selectedLabId || !labApptDate || !finalTestType) return;
    setActionMessage(null);
    try {
      await api.appointments.createLabAppointment({
        lab_id: selectedLabId,
        appointment_date: new Date(labApptDate).toISOString(),
        test_type: finalTestType,
        reason: labApptReason,
      });
      setActionMessage({ type: 'success', text: `Scheduled lab test "${finalTestType}"!` });
      setShowLabApptModal(false);
      setLabApptReason('');
      setLabApptDate('');
      setLabCustomTest('');
      fetchData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message || 'Failed to book lab appointment' });
    }
  };

  const handleSendQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryText.trim()) return;
    setActionMessage(null);
    try {
      await api.queries.createQuery({
        query_text: queryText,
        urgency: queryUrgency,
      });
      setActionMessage({ type: 'success', text: 'Query submitted to your doctor!' });
      setShowQueryModal(false);
      setQueryText('');
      fetchData();
    } catch (err: any) {
      setActionMessage({ type: 'error', text: err.message || 'Failed to send query' });
    }
  };

  const linkedDoctor = doctors.find((d) => d.id === profile?.linked_doctor_id);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Banner & Greeting */}
        <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl relative overflow-hidden">
          <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1 text-blue-300 text-xs font-semibold uppercase tracking-wider">
                <UserCheck className="w-4 h-4" /> Patient Portal
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold">
                Welcome back, {profile?.full_name || user?.username}!
              </h1>
              <p className="text-sm text-slate-300 mt-1">
                Track your health parameters, consult doctors, and view AI-analyzed lab diagnostics.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={() => setShowDoctorApptModal(true)}
                className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-md shadow-blue-500/30 flex items-center gap-1.5 transition-all"
              >
                <Plus className="w-4 h-4" />
                <span>Book Doctor</span>
              </button>
              <button
                onClick={() => setShowLabApptModal(true)}
                className="px-4 py-2.5 bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold rounded-xl shadow-md shadow-purple-500/30 flex items-center gap-1.5 transition-all"
              >
                <Plus className="w-4 h-4" />
                <span>Book Lab Test</span>
              </button>
            </div>
          </div>
        </div>

        {/* Global Toast */}
        {actionMessage && (
          <div
            className={`p-4 rounded-xl text-xs font-semibold flex items-center justify-between shadow-sm border ${
              actionMessage.type === 'success'
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : 'bg-red-50 text-red-800 border-red-200'
            }`}
          >
            <span>{actionMessage.text}</span>
            <button onClick={() => setActionMessage(null)} className="text-slate-500 font-bold hover:text-slate-800">
              ✕
            </button>
          </div>
        )}

        {/* Top Grid: Doctor Link Widget & Quick Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Linked Doctor Card */}
          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-blue-600 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="w-9 h-9 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                    <Stethoscope className="w-5 h-5" />
                  </div>
                  <h2 className="text-base font-bold text-slate-900">Your Physician</h2>
                </div>
                {profile?.linked_doctor_id && (
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700 border border-emerald-300">
                    Linked
                  </span>
                )}
              </div>

              {profile?.linked_doctor_id ? (
                <div className="space-y-3">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
                    <div className="text-sm font-bold text-slate-800">
                      {linkedDoctor?.full_name || `Doctor ID: ${profile.linked_doctor_id}`}
                    </div>
                    <div className="text-xs text-slate-500">{linkedDoctor?.email}</div>
                  </div>
                  <button
                    onClick={handleUnlinkDoctor}
                    className="w-full py-2 text-xs font-semibold text-red-600 bg-red-50 hover:bg-red-100 border border-red-200 rounded-lg flex items-center justify-center gap-1.5 transition-colors"
                  >
                    <Unlink className="w-3.5 h-3.5" />
                    <span>Unlink Doctor</span>
                  </button>
                </div>
              ) : (
                <form onSubmit={handleLinkDoctor} className="space-y-3">
                  <p className="text-xs text-slate-500">
                    Enter your doctor's shareable Doctor Code (e.g., <code className="bg-slate-100 px-1 py-0.5 rounded">DOC1A2B3C4D</code>)
                  </p>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      required
                      placeholder="Doctor Code"
                      value={doctorCodeInput}
                      onChange={(e) => setDoctorCodeInput(e.target.value)}
                      className="flex-1 px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs uppercase tracking-wider font-mono focus:outline-none focus:ring-2 focus:ring-blue-600"
                    />
                    <button
                      type="submit"
                      className="px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl flex items-center gap-1 shadow-sm"
                    >
                      <Link2 className="w-3.5 h-3.5" />
                      <span>Link</span>
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="glass-card rounded-2xl p-6 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">Scheduled Consultations</span>
              <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center">
                <Calendar className="w-4 h-4" />
              </div>
            </div>
            <div className="text-3xl font-extrabold text-slate-900">{doctorAppointments.length}</div>
            <p className="text-xs text-slate-500 mt-2">Active appointments with doctors</p>
          </div>

          <div className="glass-card rounded-2xl p-6 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">Diagnostic Reports</span>
              <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center">
                <FileText className="w-4 h-4" />
              </div>
            </div>
            <div className="text-3xl font-extrabold text-slate-900">{reports.length}</div>
            <p className="text-xs text-slate-500 mt-2">AI-analyzed lab reports on file</p>
          </div>
        </div>

        {/* AI Lab Reports Section */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-indigo-100 text-indigo-700">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-900">AI Diagnostic Lab Reports</h2>
                <p className="text-xs text-slate-500">Multimodal Gemini Vision OCR & Criticality Analysis</p>
              </div>
            </div>
          </div>

          {reports.length === 0 ? (
            <div className="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-300">
              <FileText className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-600">No lab reports available yet</p>
              <p className="text-xs text-slate-400 mt-1">Book a lab appointment to get diagnostic PDF reports analyzed by AI.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {reports.map((rpt) => (
                <div
                  key={rpt.id}
                  onClick={() => setSelectedReport(rpt)}
                  className="p-4 bg-slate-50 hover:bg-slate-100/80 border border-slate-200 rounded-xl cursor-pointer transition-all duration-200 space-y-3 group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 bg-white rounded-lg border border-slate-200 text-blue-600 group-hover:scale-105 transition-transform">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-800 line-clamp-1">{rpt.file_name}</div>
                        <div className="text-[11px] text-slate-400">
                          {new Date(rpt.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>

                    <span
                      className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                        rpt.ai_criticality === 'critical'
                          ? 'bg-red-100 text-red-700 border border-red-300'
                          : rpt.ai_criticality === 'medium'
                          ? 'bg-amber-100 text-amber-700 border border-amber-300'
                          : 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                      }`}
                    >
                      {rpt.ai_criticality || 'Normal'}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 line-clamp-2 italic">
                    "{rpt.ai_summary || 'Analysis in progress...'}"
                  </p>

                  <div className="text-[11px] text-blue-600 font-semibold flex items-center justify-between pt-2 border-t border-slate-200">
                    <span>View AI Analysis & PDF</span>
                    <span>→</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Doctor Appointments & Lab Appointments */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Doctor Appointments */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Stethoscope className="w-5 h-5 text-blue-600" /> Doctor Consultations
              </h2>
              <button
                onClick={() => setShowDoctorApptModal(true)}
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Book New
              </button>
            </div>

            {doctorAppointments.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-xl">
                No doctor appointments scheduled.
              </div>
            ) : (
              <div className="space-y-3">
                {doctorAppointments.map((appt) => (
                  <div key={appt.id} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between">
                    <div>
                      <div className="text-xs font-bold text-slate-800">
                        Date: {new Date(appt.appointment_date).toLocaleString()}
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">Reason: {appt.reason || 'Consultation'}</div>
                      {appt.notes && <div className="text-[11px] text-blue-700 font-medium mt-1">{appt.notes}</div>}
                    </div>
                    <StatusBadge status={appt.status} />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Lab Appointments */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <TestTube className="w-5 h-5 text-purple-600" /> Lab Test Appointments
              </h2>
              <button
                onClick={() => setShowLabApptModal(true)}
                className="text-xs font-semibold text-purple-600 hover:text-purple-700 flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" /> Schedule Test
              </button>
            </div>

            {labAppointments.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-xl">
                No lab test appointments scheduled.
              </div>
            ) : (
              <div className="space-y-3">
                {labAppointments.map((appt) => (
                  <div key={appt.id} className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between">
                    <div>
                      <div className="text-xs font-bold text-slate-800">
                        {appt.test_type} — {new Date(appt.appointment_date).toLocaleString()}
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">Reason: {appt.reason || 'Routine Diagnostic'}</div>
                    </div>
                    <StatusBadge status={appt.status} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Health Desk Queries Section */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-teal-100 text-teal-700">
                <MessageSquare className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-900">Physician Health Desk</h2>
                <p className="text-xs text-slate-500">Send direct health inquiries to your linked doctor</p>
              </div>
            </div>
            {profile?.linked_doctor_id && (
              <button
                onClick={() => setShowQueryModal(true)}
                className="px-3.5 py-2 bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold rounded-xl shadow-sm flex items-center gap-1.5 transition-colors"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Send Query</span>
              </button>
            )}
          </div>

          {!profile?.linked_doctor_id ? (
            <div className="p-6 bg-slate-50 border border-amber-200 text-amber-800 text-xs rounded-xl flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
              <span>Please link to a doctor using their Doctor Code to send medical inquiries.</span>
            </div>
          ) : queries.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-xl">
              No health inquiries sent yet.
            </div>
          ) : (
            <div className="space-y-3">
              {queries.map((q) => (
                <div key={q.id} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <UrgencyBadge urgency={q.urgency} />
                      <span className="text-xs text-slate-400">
                        {new Date(q.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    {q.is_responded ? (
                      <span className="text-[10px] font-bold bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full border border-emerald-300 flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" /> Answered
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full border border-amber-300 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> Pending Reply
                      </span>
                    )}
                  </div>
                  <p className="text-xs font-semibold text-slate-800">Q: {q.query_text}</p>
                  {q.response_text && (
                    <div className="mt-2 p-3 bg-white border border-teal-200 rounded-lg text-xs text-teal-900">
                      <span className="font-bold text-teal-700">Doctor's Response: </span>
                      {q.response_text}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Modal: Book Doctor Consultation */}
      {showDoctorApptModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Schedule Doctor Consultation</h3>
            <form onSubmit={handleBookDoctorAppt} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Select Doctor</label>
                <select
                  required
                  value={selectedDoctorId || ''}
                  onChange={(e) => setSelectedDoctorId(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  <option value="">-- Choose Doctor --</option>
                  {doctors.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.full_name || d.username} ({d.email})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Date & Time</label>
                <input
                  type="datetime-local"
                  required
                  value={doctorApptDate}
                  onChange={(e) => setDoctorApptDate(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Reason / Notes</label>
                <textarea
                  rows={3}
                  value={doctorApptReason}
                  onChange={(e) => setDoctorApptReason(e.target.value)}
                  placeholder="Routine checkup, headache, hypertension follow-up..."
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
              </div>

              <div className="flex gap-2 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setShowDoctorApptModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-sm"
                >
                  Confirm Booking
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Book Lab Test with Select Test Dropdown */}
      {showLabApptModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Schedule Diagnostic Lab Test</h3>
            <form onSubmit={handleBookLabAppt} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Select Diagnostic Lab</label>
                <select
                  required
                  value={selectedLabId || ''}
                  onChange={(e) => setSelectedLabId(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-purple-600"
                >
                  <option value="">-- Choose Diagnostic Lab --</option>
                  {labs.map((l) => (
                    <option key={l.id} value={l.id}>
                      {l.full_name || l.username} ({l.email})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Select Diagnostic Test</label>
                <select
                  value={labTestPreset}
                  onChange={(e) => setLabTestPreset(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-purple-600"
                >
                  {COMMON_LAB_TESTS.map((test) => (
                    <option key={test} value={test}>
                      {test}
                    </option>
                  ))}
                </select>
              </div>

              {labTestPreset === 'Custom / Other Diagnostic Test' && (
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Specify Custom Test</label>
                  <input
                    type="text"
                    required
                    value={labCustomTest}
                    onChange={(e) => setLabCustomTest(e.target.value)}
                    placeholder="e.g. Allergy Panel"
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-purple-600"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Date & Time</label>
                <input
                  type="datetime-local"
                  required
                  value={labApptDate}
                  onChange={(e) => setLabApptDate(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-purple-600"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Reason & Fasting Notes</label>
                <textarea
                  rows={2}
                  value={labApptReason}
                  onChange={(e) => setLabApptReason(e.target.value)}
                  placeholder="Fasting 12 hours required..."
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-purple-600"
                />
              </div>

              <div className="flex gap-2 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setShowLabApptModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold text-white bg-purple-600 hover:bg-purple-700 rounded-xl shadow-sm"
                >
                  Confirm Lab Slot
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Send Medical Query */}
      {showQueryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Send Health Query to Doctor</h3>
            <form onSubmit={handleSendQuery} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Urgency Level</label>
                <select
                  value={queryUrgency}
                  onChange={(e) => setQueryUrgency(e.target.value as QueryUrgency)}
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-bold focus:outline-none focus:ring-2 focus:ring-teal-600"
                >
                  <option value="LOW">LOW — Routine question / medication advice</option>
                  <option value="MEDIUM">MEDIUM — Moderate concern / symptom inquiry</option>
                  <option value="HIGH">HIGH — Urgent medical query</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Your Question</label>
                <textarea
                  rows={4}
                  required
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value)}
                  placeholder="Describe your symptoms or question for your physician..."
                  className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-teal-600"
                />
              </div>

              <div className="flex gap-2 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setShowQueryModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-bold text-white bg-teal-600 hover:bg-teal-700 rounded-xl shadow-sm flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Submit Question</span>
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

      <Footer />
    </div>
  );
}
