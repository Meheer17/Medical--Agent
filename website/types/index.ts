export type UserRole = 'PATIENT' | 'DOCTOR' | 'LAB';
export type QueryUrgency = 'LOW' | 'MEDIUM' | 'HIGH';
export type AppointmentStatus = 'SCHEDULED' | 'CONFIRMED' | 'CANCELLED' | 'COMPLETED';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  is_verified?: boolean;
  created_at: string;
  updated_at?: string;
}

export interface PatientProfile extends User {
  phone?: string;
  address?: string;
  linked_doctor_id?: number | null;
}

export interface DoctorProfile extends User {
  doctor_code?: string;
}

export interface DoctorAppointment {
  id: number;
  patient_id: number;
  doctor_id: number;
  appointment_date: string;
  reason?: string;
  notes?: string;
  status: AppointmentStatus;
  created_at: string;
  updated_at: string;
}

export interface LabAppointment {
  id: number;
  patient_id: number;
  doctor_id?: number | null;
  lab_id: number;
  appointment_date: string;
  test_type: string;
  reason?: string;
  notes?: string;
  status: AppointmentStatus;
  created_at: string;
  updated_at: string;
}

export interface LabReport {
  id: number;
  appointment_id: number;
  uploaded_by_id: number;
  file_name: string;
  file_size: number;
  mime_type: string;
  test_results?: string;
  notes?: string;
  ai_summary?: string;
  ai_key_findings?: string; // JSON string or text
  ai_abnormal_values?: string; // JSON string or text
  ai_clinical_significance?: string;
  ai_criticality?: 'critical' | 'medium' | 'low' | string;
  ai_doctor_recommendation?: string;
  ai_analysis_status: 'pending' | 'completed' | 'failed' | string;
  ai_analysis_error?: string;
  created_at: string;
  updated_at: string;
}

export interface HealthQuery {
  id: number;
  patient_id: number;
  doctor_id: number;
  query_text: string;
  response_text?: string | null;
  urgency: QueryUrgency;
  is_responded: boolean;
  created_at: string;
  responded_at?: string | null;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
