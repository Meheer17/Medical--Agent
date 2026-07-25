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
  DoctorAppointment,
  LabReport,
  HealthQuery,
  User,
  PatientProfile,
  AppointmentStatus,
  LabAppointment,
} from '@/types';
import {
  Stethoscope,
  Key,
  Copy,
  RotateCw,
  Users,
  Calendar,
  FileText,
  MessageSquare,
  Plus,
  Send,
  Check,
  Phone,
  MapPin,
  Mail,
  User as UserIcon,
  Sparkles,
  AlertTriangle,
  ChevronRight,
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

export default function DoctorDashboard() {
  const { user } = useAuth();
  const [doctorCode, setDoctorCode] = useState<string>('');
  const [patients, setPatients] = useState<User[]>([]);
  const [appointments, setAppointments] = useState<DoctorAppointment[]>([]);
  const [pendingQueries, setPendingQueries] = useState<HealthQuery[]>([]);
  const [labs, setLabs] = useState<User[]>([]);

  const [copied, setCopied] = useState(false);

  // Patient Inspection Modal State
  const [selectedPatient, setSelectedPatient] = useState<PatientProfile | null>(null);
  const [patientReports, setPatientReports] = useState<LabReport[]>([]);
  const [selectedReport, setSelectedReport] = useState<LabReport | null>(null);
  const [isLoadingPatientDetails, setIsLoadingPatientDetails] = useState(false);

  // Response Query Modal State
  const [respondingQuery, setRespondingQuery] = useState<HealthQuery | null>(null);
  const [responseText, setResponseText] = useState('');

  // Prescribe Lab Test Modal State
  const [showPrescribeModal, setShowPrescribeModal] = useState(false);
  const [prescribePatientId, setPrescribePatientId] = useState<number | null>(null);
  const [prescribeLabId, setPrescribeLabId] = useState<number | null>(null);
  const [prescribeTestPreset, setPrescribeTestPreset] = useState<string>(COMMON_LAB_TESTS[0]);
  const [prescribeCustomTest, setPrescribeCustomTest] = useState('');
  const [prescribeDate, setPrescribeDate] = useState('');
  const [prescribeReason, setPrescribeReason] = useState('');

  const [actionMessage, setActionMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(
    null
  );

  const fetchData = async () => {
    try {
      const [codeRes, patientsRes, apptsRes, queriesRes, labsRes] = await Promise.all([
        api.profiles.getMyCode().catch(() => ({ doctor_code: '' })),
        api.profiles.getMyPatients().catch(() => ({ doctor_id: 0, patient_count: 0, patients: [] })),
        api.appointments.getMyDoctorAppointments().catch(() => []),
        api.queries.getPendingQueries().catch(() => []),
        api.profiles.getLabs().catch(() => []),
      ]);

      if (codeRes.doctor_code) setDoctorCode(codeRes.doctor_code);
      setPatients(patientsRes.patients || []);
      setAppointments(apptsRes);
      setPendingQueries(queriesRes);
      setLabs(labsRes);
    } catch (e) {
      console.error('Failed to load doctor dashboard data', e);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCopyCode = () => {
    if (!doctorCode) return;
    navigator.clipboard.writeText(doctorCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRegenerateCode = async () => {
    try {
      const res = await api.profiles.regenerateCode();
      setDoctorCode(res.doctor_code);
      setActionMessage({ type: 'success', text: 'New Doctor Code generated!' });
    } catch (e: any) {
      setActionMessage({ type: 'error', text: e.message || 'Failed to regenerate code' });
    }
  };

  const handleUpdateStatus = async (apptId: number, newStatus: AppointmentStatus) => {
    try {
      await api.appointments.updateDoctorAppointment(apptId, { status: newStatus });
      setActionMessage({ type: 'success', text: `Appointment status updated to ${newStatus}` });
      fetchData();
    } catch (e: any) {
      setActionMessage({ type: 'error', text: e.message || 'Failed to update status' });
    }
  };

  const handleInspectPatient = async (patient: User) => {
    setIsLoadingPatientDetails(true);
    setSelectedPatient(null);
    setPatientReports([]);
    try {
      const profileData = await api.profiles.getPatientById(patient.id);
      const reportsData = await api.profiles.getPatientReports(patient.id);
      setSelectedPatient(profileData);
      setPatientReports(reportsData);
    } catch (e: any) {
      setActionMessage({ type: 'error', text: e.message || 'Failed to load patient history' });
    } finally {
      setIsLoadingPatientDetails(false);
    }
  };

  const handleRespondQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!respondingQuery || !responseText.trim()) return;
    try {
      await api.queries.respondQuery(respondingQuery.id, responseText);
      setActionMessage({ type: 'success', text: 'Response sent to patient!' });
      setRespondingQuery(null);
      setResponseText('');
      fetchData();
    } catch (e: any) {
      setActionMessage({ type: 'error', text: e.message || 'Failed to respond to query' });
    }
  };

  const handlePrescribeLabTest = async (e: React.FormEvent) => {
    e.preventDefault();
    const finalTestType =
      prescribeTestPreset === 'Custom / Other Diagnostic Test'
        ? prescribeCustomTest.trim()
        : prescribeTestPreset;

    if (!prescribePatientId || !prescribeLabId || !prescribeDate || !finalTestType) return;

    try {
      await api.appointments.doctorCreateLabAppointment({
        patient_id: prescribePatientId,
        lab_id: prescribeLabId,
        appointment_date: new Date(prescribeDate).toISOString(),
        test_type: finalTestType,
        reason: prescribeReason,
      });
      setActionMessage({ type: 'success', text: `Ordered "${finalTestType}" lab test for patient!` });
      setShowPrescribeModal(false);
      setPrescribeReason('');
      setPrescribeDate('');
      setPrescribeCustomTest('');
      fetchData();
    } catch (e: any) {
      setActionMessage({ type: 'error', text: e.message || 'Failed to prescribe lab test' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Banner */}
        <div className="bg-gradient-to-r from-emerald-900 via-teal-900 to-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl relative overflow-hidden">
          <div className="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1 text-emerald-300 text-xs font-semibold uppercase tracking-wider">
                <Stethoscope className="w-4 h-4" /> Doctor Portal
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold">
                Dr. {user?.full_name || user?.username}
              </h1>
              <p className="text-sm text-slate-300 mt-1">
                Inspect patient medical records, prescribe diagnostic tests, and respond to health inquiries.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <button
                onClick={() => setShowPrescribeModal(true)}
                className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow-md shadow-emerald-500/30 flex items-center gap-1.5 transition-all"
              >
                <Plus className="w-4 h-4" />
                <span>Prescribe Lab Test</span>
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

        {/* Top Grid: Doctor Code Widget & Roster Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Shareable Doctor Code Widget */}
          <div className="glass-card rounded-2xl p-6 border-l-4 border-l-emerald-600 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center font-bold">
                    <Key className="w-5 h-5" />
                  </div>
                  <h2 className="text-base font-bold text-slate-900">Shareable Doctor Code</h2>
                </div>
              </div>
              <p className="text-xs text-slate-500 mb-3">
                Share this code with your patients to link them directly to your practice:
              </p>

              <div className="flex items-center gap-2 mb-3">
                <div className="flex-1 px-3 py-2.5 bg-slate-900 text-emerald-400 font-mono text-sm font-bold tracking-widest rounded-xl text-center shadow-inner">
                  {doctorCode || 'DOC...'}
                </div>
                <button
                  onClick={handleCopyCode}
                  className="px-3 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold flex items-center gap-1 shadow-sm"
                  title="Copy to clipboard"
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>

              <button
                onClick={handleRegenerateCode}
                className="w-full py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 border border-slate-200 rounded-lg flex items-center justify-center gap-1.5 transition-colors"
              >
                <RotateCw className="w-3.5 h-3.5" />
                <span>Regenerate Doctor Code</span>
              </button>
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="glass-card rounded-2xl p-6 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">Linked Roster</span>
              <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-600 flex items-center justify-center">
                <Users className="w-4 h-4" />
              </div>
            </div>
            <div className="text-3xl font-extrabold text-slate-900">{patients.length}</div>
            <p className="text-xs text-slate-500 mt-2">Active linked patients under your care</p>
          </div>

          <div className="glass-card rounded-2xl p-6 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase text-slate-500 tracking-wider">Pending Health Queries</span>
              <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-600 flex items-center justify-center">
                <MessageSquare className="w-4 h-4" />
              </div>
            </div>
            <div className="text-3xl font-extrabold text-slate-900">{pendingQueries.length}</div>
            <p className="text-xs text-slate-500 mt-2">Unanswered patient inquiries</p>
          </div>
        </div>

        {/* Patient Health Queries Desk */}
        <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-amber-100 text-amber-700">
                <MessageSquare className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-900">Incoming Health Queries Desk</h2>
                <p className="text-xs text-slate-500">Categorized by urgency level (HIGH / MEDIUM / LOW)</p>
              </div>
            </div>
          </div>

          {pendingQueries.length === 0 ? (
            <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-xl">
              No pending health questions from your linked patients.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {pendingQueries.map((q) => (
                <div key={q.id} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <UrgencyBadge urgency={q.urgency} />
                      <span className="text-xs text-slate-400">
                        {new Date(q.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <button
                      onClick={() => {
                        setRespondingQuery(q);
                        setResponseText('');
                      }}
                      className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-lg shadow-sm flex items-center gap-1"
                    >
                      <Send className="w-3 h-3" /> Respond
                    </button>
                  </div>
                  <p className="text-xs font-semibold text-slate-800">Q: "{q.query_text}"</p>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Consultation Schedule & Linked Patient Roster */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Daily Appointments Schedule */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-emerald-600" /> Patient Consultations Schedule
            </h2>

            {appointments.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-xl">
                No patient consultations scheduled today.
              </div>
            ) : (
              <div className="space-y-3">
                {appointments.map((appt) => (
                  <div key={appt.id} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-bold text-slate-800">
                        {new Date(appt.appointment_date).toLocaleString()}
                      </div>
                      <StatusBadge status={appt.status} />
                    </div>
                    <div className="text-xs text-slate-600">Reason: {appt.reason || 'General Consultation'}</div>
                    {appt.notes && (
                      <div className="text-[11px] bg-blue-50 text-blue-800 p-2 rounded-lg font-medium">
                        {appt.notes}
                      </div>
                    )}

                    {/* Status Updater Buttons */}
                    <div className="flex gap-2 pt-2 border-t border-slate-200 text-xs">
                      {appt.status !== 'CONFIRMED' && (
                        <button
                          onClick={() => handleUpdateStatus(appt.id, 'CONFIRMED')}
                          className="px-2.5 py-1 bg-emerald-100 hover:bg-emerald-200 text-emerald-800 font-semibold rounded-lg"
                        >
                          Confirm
                        </button>
                      )}
                      {appt.status !== 'COMPLETED' && (
                        <button
                          onClick={() => handleUpdateStatus(appt.id, 'COMPLETED')}
                          className="px-2.5 py-1 bg-slate-200 hover:bg-slate-300 text-slate-800 font-semibold rounded-lg"
                        >
                          Mark Completed
                        </button>
                      )}
                      {appt.status !== 'CANCELLED' && (
                        <button
                          onClick={() => handleUpdateStatus(appt.id, 'CANCELLED')}
                          className="px-2.5 py-1 bg-red-100 hover:bg-red-200 text-red-800 font-semibold rounded-lg ml-auto"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Linked Patient Roster with Deep Inspection */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Users className="w-5 h-5 text-emerald-600" /> Linked Patient Roster
            </h2>

            {patients.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-xl">
                No patients linked yet. Share your Doctor Code to connect with patients.
              </div>
            ) : (
              <div className="space-y-3">
                {patients.map((pt) => (
                  <div
                    key={pt.id}
                    className="p-4 bg-slate-50 hover:bg-slate-100/80 border border-slate-200 rounded-xl flex items-center justify-between transition-colors"
                  >
                    <div className="space-y-0.5">
                      <div className="text-xs font-bold text-slate-900">{pt.full_name || pt.username}</div>
                      <div className="text-[11px] text-slate-500">{pt.email}</div>
                    </div>

                    <button
                      onClick={() => handleInspectPatient(pt)}
                      className="px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-sm flex items-center gap-1.5 transition-all"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      <span>Open Records</span>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Modal: Full Patient Record & Diagnostic History Inspection */}
        {(selectedPatient || isLoadingPatientDetails) && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-2xl space-y-6 max-h-[85vh] overflow-y-auto">
              {isLoadingPatientDetails ? (
                <div className="p-12 text-center text-slate-600 font-semibold text-sm">
                  Loading Patient Records & AI Diagnostics...
                </div>
              ) : selectedPatient && (
                <>
                  {/* Patient Profile Header */}
                  <div className="bg-gradient-to-r from-emerald-900 to-teal-900 text-white p-5 rounded-2xl flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <UserIcon className="w-5 h-5 text-emerald-300" />
                        <h3 className="text-xl font-bold">{selectedPatient.full_name || selectedPatient.username}</h3>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1 text-xs text-slate-200 mt-2">
                        <span className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5 text-emerald-400" /> {selectedPatient.email}</span>
                        <span className="flex items-center gap-1.5"><Phone className="w-3.5 h-3.5 text-emerald-400" /> {selectedPatient.phone || 'Phone not provided'}</span>
                        <span className="flex items-center gap-1.5 sm:col-span-2"><MapPin className="w-3.5 h-3.5 text-emerald-400" /> {selectedPatient.address || 'Address not provided'}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedPatient(null)}
                      className="text-white/80 hover:text-white font-bold p-1"
                    >
                      ✕
                    </button>
                  </div>

                  {/* Patient Reports List */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                        <Sparkles className="w-4 h-4 text-indigo-600" /> Diagnostic PDF Reports & AI Vision Analysis ({patientReports.length})
                      </h4>
                    </div>

                    {patientReports.length === 0 ? (
                      <div className="p-8 text-center text-xs text-slate-500 bg-slate-50 rounded-xl border border-dashed border-slate-300">
                        No lab report records found on file for this patient.
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {patientReports.map((rpt) => (
                          <div
                            key={rpt.id}
                            onClick={() => setSelectedReport(rpt)}
                            className="p-4 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl cursor-pointer transition-all space-y-2.5"
                          >
                            <div className="flex items-start justify-between">
                              <div>
                                <div className="text-xs font-bold text-slate-800 line-clamp-1">{rpt.file_name}</div>
                                <div className="text-[11px] text-slate-400">
                                  {new Date(rpt.created_at).toLocaleDateString()}
                                </div>
                              </div>
                              <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                                {rpt.ai_criticality || 'Normal'}
                              </span>
                            </div>

                            <p className="text-xs text-slate-600 line-clamp-2 italic">
                              "{rpt.ai_summary || 'Gemini Vision processing...'}"
                            </p>

                            <div className="text-[11px] text-emerald-700 font-semibold flex items-center justify-between pt-2 border-t border-slate-200">
                              <span>Open AI Analysis</span>
                              <ChevronRight className="w-4 h-4" />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Modal: Respond to Query */}
        {respondingQuery && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
              <h3 className="text-lg font-bold text-slate-900">Respond to Health Query</h3>
              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs space-y-1">
                <UrgencyBadge urgency={respondingQuery.urgency} />
                <p className="font-semibold text-slate-800 mt-1">"{respondingQuery.query_text}"</p>
              </div>

              <form onSubmit={handleRespondQuery} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Your Medical Advice</label>
                  <textarea
                    rows={4}
                    required
                    value={responseText}
                    onChange={(e) => setResponseText(e.target.value)}
                    placeholder="Provide clear medical advice or instructions..."
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-600"
                  />
                </div>

                <div className="flex gap-2 justify-end pt-2">
                  <button
                    type="button"
                    onClick={() => setRespondingQuery(null)}
                    className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-sm"
                  >
                    Send Response
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Prescribe Lab Test with Test Dropdown Options */}
        {showPrescribeModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
            <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
              <h3 className="text-lg font-bold text-slate-900">Prescribe Diagnostic Lab Test</h3>
              <form onSubmit={handlePrescribeLabTest} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Select Patient</label>
                  <select
                    required
                    value={prescribePatientId || ''}
                    onChange={(e) => setPrescribePatientId(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600"
                  >
                    <option value="">-- Choose Patient from Roster --</option>
                    {patients.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.full_name || p.username} ({p.email})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Select Diagnostic Lab</label>
                  <select
                    required
                    value={prescribeLabId || ''}
                    onChange={(e) => setPrescribeLabId(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600"
                  >
                    <option value="">-- Choose Pathology Lab --</option>
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
                    value={prescribeTestPreset}
                    onChange={(e) => setPrescribeTestPreset(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-600"
                  >
                    {COMMON_LAB_TESTS.map((test) => (
                      <option key={test} value={test}>
                        {test}
                      </option>
                    ))}
                  </select>
                </div>

                {prescribeTestPreset === 'Custom / Other Diagnostic Test' && (
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Specify Custom Test Name</label>
                    <input
                      type="text"
                      required
                      value={prescribeCustomTest}
                      onChange={(e) => setPrescribeCustomTest(e.target.value)}
                      placeholder="e.g., Cardiac Enzyme Marker Panel"
                      className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-600"
                    />
                  </div>
                )}

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Appointment Date & Time</label>
                  <input
                    type="datetime-local"
                    required
                    value={prescribeDate}
                    onChange={(e) => setPrescribeDate(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">Prescription Notes & Instructions</label>
                  <textarea
                    rows={2}
                    value={prescribeReason}
                    onChange={(e) => setPrescribeReason(e.target.value)}
                    placeholder="Fast for 12 hours prior to test..."
                    className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-600"
                  />
                </div>

                <div className="flex gap-2 justify-end pt-2">
                  <button
                    type="button"
                    onClick={() => setShowPrescribeModal(false)}
                    className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-sm"
                  >
                    Prescribe & Order Test
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
