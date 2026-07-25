import {
  User,
  PatientProfile,
  DoctorAppointment,
  LabAppointment,
  LabReport,
  HealthQuery,
  UserRole,
  QueryUrgency,
  AppointmentStatus
} from '@/types';

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL || 'http://135.235.136.30:9000'
).replace(/\/+$/, '');

function getAuthHeader(): Record<string, string> {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('cliniq_token');
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
  }
  return {};
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = 'An error occurred';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || response.statusText;
    } catch {
      errorMessage = response.statusText;
    }
    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const api = {
  // Auth APIs
  auth: {
    signup: async (data: {
      email: string;
      username: string;
      password: string;
      full_name?: string;
      role: UserRole;
    }) => {
      return request<{ access_token: string; token_type: string; user: User }>(
        '/api/auth/signup',
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      );
    },
    login: async (data: { email: string; password: string }) => {
      return request<{ access_token: string; token_type: string; user: User }>(
        '/api/auth/login',
        {
          method: 'POST',
          body: JSON.stringify(data),
        }
      );
    },
    getProfile: async () => {
      return request<User>('/api/auth/profile');
    },
  },

  // Profiles & Linking APIs
  profiles: {
    getMe: async () => {
      return request<PatientProfile>('/api/profiles/me');
    },
    updateProfile: async (data: { full_name?: string; phone?: string; address?: string }) => {
      return request<PatientProfile>('/api/profiles/me', {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    linkDoctor: async (doctor_code: string) => {
      return request<{ message: string }>('/api/profiles/link-doctor', {
        method: 'POST',
        body: JSON.stringify({ doctor_code }),
      });
    },
    unlinkDoctor: async () => {
      return request<{ message: string }>('/api/profiles/unlink-doctor', {
        method: 'POST',
      });
    },
    getMyCode: async () => {
      return request<{ doctor_code: string }>('/api/profiles/my-code');
    },
    regenerateCode: async () => {
      return request<{ doctor_code: string }>('/api/profiles/regenerate-code');
    },
    getMyPatients: async () => {
      return request<{ doctor_id: number; patient_count: number; patients: User[] }>(
        '/api/profiles/my-patients'
      );
    },
    getDoctors: async () => {
      return request<User[]>('/api/profiles/doctors');
    },
    getLabs: async () => {
      return request<User[]>('/api/profiles/labs');
    },
    getPatientById: async (id: number) => {
      return request<PatientProfile>(`/api/profiles/patient/${id}`);
    },
    getPatientReports: async (id: number) => {
      return request<LabReport[]>(`/api/profiles/patient/${id}/reports`);
    },
  },

  // Appointment APIs
  appointments: {
    createDoctorAppointment: async (data: {
      doctor_id: number;
      appointment_date: string;
      reason?: string;
      notes?: string;
    }) => {
      return request<DoctorAppointment>('/api/appointments/doctor', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    getMyDoctorAppointments: async () => {
      return request<DoctorAppointment[]>('/api/appointments/doctor/my-appointments');
    },
    updateDoctorAppointment: async (
      id: number,
      data: {
        appointment_date?: string;
        reason?: string;
        notes?: string;
        status?: AppointmentStatus;
      }
    ) => {
      return request<DoctorAppointment>(`/api/appointments/doctor/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    cancelDoctorAppointment: async (id: number) => {
      return request<{ message: string }>(`/api/appointments/doctor/${id}`, {
        method: 'DELETE',
      });
    },

    createLabAppointment: async (data: {
      lab_id: number;
      appointment_date: string;
      test_type: string;
      reason?: string;
      notes?: string;
    }) => {
      return request<LabAppointment>('/api/appointments/lab', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    doctorCreateLabAppointment: async (data: {
      patient_id: number;
      lab_id: number;
      appointment_date: string;
      test_type: string;
      reason?: string;
      notes?: string;
    }) => {
      return request<LabAppointment>('/api/appointments/lab/doctor-create', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    getMyLabAppointments: async () => {
      return request<LabAppointment[]>('/api/appointments/lab/my-appointments');
    },
    updateLabAppointment: async (
      id: number,
      data: {
        appointment_date?: string;
        test_type?: string;
        reason?: string;
        notes?: string;
        status?: AppointmentStatus;
      }
    ) => {
      return request<LabAppointment>(`/api/appointments/lab/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },
    cancelLabAppointment: async (id: number) => {
      return request<{ message: string }>(`/api/appointments/lab/${id}`, {
        method: 'DELETE',
      });
    },
  },

  // Lab Report & AI APIs
  reports: {
    uploadReport: async (appointmentId: number, file: File, testResults?: string, notes?: string) => {
      const formData = new FormData();
      formData.append('file', file);
      if (testResults) formData.append('test_results', testResults);
      if (notes) formData.append('notes', notes);

      const headers: Record<string, string> = {};
      const token = localStorage.getItem('cliniq_token');
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await fetch(`${API_BASE_URL}/api/reports/lab/${appointmentId}`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to upload report');
      }

      return response.json() as Promise<LabReport>;
    },
    getReport: async (appointmentId: number) => {
      return request<LabReport>(`/api/reports/lab/${appointmentId}`);
    },
    reanalyzeReport: async (appointmentId: number) => {
      return request<{ message: string }>(`/api/reports/reanalyze/${appointmentId}`, {
        method: 'POST',
      });
    },
    getMyReports: async () => {
      return request<LabReport[]>('/api/reports/my-reports');
    },
    getDownloadUrl: (reportId: number) => {
      return `${API_BASE_URL}/api/file/${reportId}`;
    },
  },

  // Health Query APIs
  queries: {
    createQuery: async (data: { query_text: string; urgency: QueryUrgency }) => {
      return request<HealthQuery>('/api/queries', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },
    getQueries: async () => {
      return request<HealthQuery[]>('/api/queries');
    },
    getPendingCount: async () => {
      return request<{ pending_count: number }>('/api/queries/pending/count');
    },
    getPendingQueries: async () => {
      return request<HealthQuery[]>('/api/queries/pending/list');
    },
    respondQuery: async (id: number, response_text: string) => {
      return request<HealthQuery>(`/api/queries/${id}/respond`, {
        method: 'POST',
        body: JSON.stringify({ response_text }),
      });
    },
  },
};
