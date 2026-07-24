# ClinIQ — AI-Powered Medical Agent & Healthcare Ecosystem 🏥🤖

**ClinIQ** is an end-to-end, intelligent healthcare management platform that seamlessly connects **Patients**, **Doctors**, and **Diagnostic Labs**. Powered by **Google Gemini Multimodal Vision AI (`gemini-3.6-flash`)** and autonomous agentic function calling, ClinIQ automates medical report analysis, extracts critical diagnostic parameters, and automatically schedules follow-up consultations when abnormal lab values are detected.

---

## 📋 Table of Contents

- [🌟 Key Highlights & AI Capabilities](#-key-highlights--ai-capabilities)
- [🔐 User Logins & Role-Based Access Control](#-user-logins--role-based-access-control)
  - [1. Patient Role](#1-patient-role)
  - [2. Doctor Role](#2-doctor-role)
  - [3. Diagnostic Lab Role](#3-diagnostic-lab-role)
- [🤖 Where AI Plays a Role](#-where-ai-plays-a-role)
  - [1. Multimodal Vision PDF Analysis](#1-multimodal-vision-pdf-analysis)
  - [2. Structured Diagnostic Extraction](#2-structured-diagnostic-extraction)
  - [3. Autonomous Agentic Appointment Booking](#3-autonomous-agentic-appointment-booking)
  - [4. Async Background Processing](#4-async-background-processing)
- [⚡ Complete App Feature Matrix](#-complete-app-feature-matrix)
- [🛠️ Technical Architecture & Tech Stack](#️-technical-architecture--tech-stack)
- [📡 API Endpoints Summary](#-api-endpoints-summary)
- [🚀 Setup & Installation Guide](#-setup--installation-guide)
  - [Backend Setup](#backend-setup)
  - [Android App Setup](#android-app-setup)
- [🛡️ Security & Privacy](#️-security--privacy)

---

## 🌟 Key Highlights & AI Capabilities

- 📄 **Multimodal Vision PDF Parsing**: Converts PDF lab reports into high-resolution images and leverages Gemini Multimodal AI to read complex medical formatting, tables, and handwritten notes.
- ⚡ **Autonomous Agentic Doctor Booking**: AI evaluates lab results for criticality (`CRITICAL`, `MEDIUM`, `LOW`). If critical or medium abnormalities are found, the AI agent autonomously executes a function call to schedule a doctor appointment for the patient.
- 🔗 **Seamless Patient-Doctor Linking**: Patients link directly with their preferred doctor using a unique shareable Doctor Code (`DOC...`).
- 💬 **Urgency-Based Health Desk**: Direct messaging channel for patients to send health queries to doctors categorized by urgency (`HIGH`, `MEDIUM`, `LOW`).
- 📱 **Native Android MVVM App**: Rich UI with Material Design 3, view bindings, smooth navigation, and dark/light themes.

---

## 🔐 User Logins & Role-Based Access Control

ClinIQ provides three distinct user login types, each with a customized user interface and specific access privileges:

```
                  ┌────────────────────────┐
                  │   ClinIQ Ecosystem     │
                  └───────────┬────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
  │   PATIENT    │     │    DOCTOR    │     │     LAB      │
  │    LOGIN     │     │    LOGIN     │     │    LOGIN     │
  └──────────────┘     └──────────────┘     └──────────────┘
```

---

### 1. Patient Role (`PATIENT`)

Designed for individuals seeking healthcare tracking, lab report interpretation, and doctor consultations.

* **Login & Authentication**:
  * Sign up with Email, Username, Full Name, and Password selecting the `PATIENT` role.
  * Secure JWT Bearer authentication with automatic token refresh.
* **Capabilities & Features**:
  * 🔗 **Link to Doctor**: Connect with a physician by entering their unique **Doctor Code** (e.g., `DOC1A2B3C4D`). Option to view linked doctor details or unlink at any time.
  * 🩺 **Book Doctor Appointments**: Schedule virtual/in-person appointments with linked or available doctors. Choose appointment date/time, provide reason and notes, and track appointment status (`SCHEDULED`, `CONFIRMED`, `COMPLETED`, `CANCELLED`).
  * 🧪 **Schedule Lab Tests**: Book lab test slots at diagnostic centers for specific tests (e.g., *Complete Blood Count, Lipid Profile, Thyroid Panel*), add fasting notes, and track lab appointments.
  * 📊 **View AI-Analyzed Lab Reports**: View reports uploaded by labs alongside AI-generated summaries, key medical findings, extracted abnormal values highlighted in red, clinical significance, and official doctor recommendations.
  * ⬇️ **PDF Download**: Download original high-resolution lab report PDFs anytime.
  * 💬 **Send Medical Queries**: Contact linked doctors directly with questions. Set query urgency (`LOW`, `MEDIUM`, `HIGH`) and view doctor responses.
  * 🤖 **Receive Auto-Bookings**: Get automatically scheduled follow-up appointments when AI detects urgent or abnormal lab values.

---

### 2. Doctor Role (`DOCTOR`)

Designed for medical professionals managing patients, reviewing lab diagnostics, and answering medical inquiries.

* **Login & Authentication**:
  * Sign up selecting the `DOCTOR` role and log in via JWT authentication.
* **Capabilities & Features**:
  * 🔑 **Unique Doctor Code Generator**: Each doctor gets an automatically generated shareable Doctor Code (e.g., `DOC8F9E0D1C`). Can regenerate code as needed.
  * 👥 **Patient Roster (My Patients)**: View list of all patients linked to the doctor, access patient profiles, contact details, and full medical histories.
  * 📂 **Patient Medical History & Diagnostic Inspection**: Inspect all lab reports uploaded for linked patients, complete with original PDF file viewing, AI summaries, abnormal parameters, and criticality flags.
  * 📅 **Manage Consultations**: View daily schedule of patient appointments, update status (`CONFIRMED`, `COMPLETED`, `CANCELLED`), edit appointment notes, or reschedule.
  * 🧪 **Prescribe Lab Appointments**: Doctors can directly create/order diagnostic lab test appointments for their patients at specific labs.
  * 📨 **Patient Query Desk**: Review incoming patient health questions, view urgency badges (`HIGH`, `MEDIUM`, `LOW`), respond with medical advice, and monitor pending query counts.

---

### 3. Diagnostic Lab Role (`LAB`)

Designed for laboratories and pathology centers uploading patient diagnostic results.

* **Login & Authentication**:
  * Sign up selecting the `LAB` role and log in via JWT authentication.
* **Capabilities & Features**:
  * 📋 **Lab Schedule Management**: View lab test appointment requests initiated by patients or prescribed by doctors.
  * 📤 **Upload PDF Lab Reports**: Upload official diagnostic PDF files associated with patient appointments.
  * ⚡ **Automated AI Triggering**: Uploading a PDF automatically triggers background parsing and AI analysis.
  * 🔄 **Re-analyze Reports**: Ability to manually re-trigger AI analysis for any report if needed.
  * ✏️ **Edit & Manage Reports**: Update lab notes, manual result text, or delete reports.

---

## 🤖 Where AI Plays a Role

AI serves as an intelligent co-pilot in ClinIQ. The system leverages **Google Gemini API (`gemini-3.6-flash`)** configured via a custom **Genkit Manager** architecture:

```
[ Lab Uploads PDF ]
        │
        ▼
[ PyMuPDF (fitz) converts PDF pages ➔ PIL High-Res Images ]
        │
        ▼
[ Sent to Gemini Multimodal Vision API ]
        │
        ├── 📝 Summary & Key Findings Generation
        ├── 🚨 Abnormal Value Extraction & Reference Matching
        ├── 🩺 Clinical Significance & Guidance Formulation
        │
        ▼
[ Criticality Evaluation: CRITICAL | MEDIUM | LOW ]
        │
        ├── 🔴 CRITICAL / 🟡 MEDIUM ──► AI Agent Calls Function Tool: `book_doctor_appointment`
        │                                  └─► Auto-books Doctor Appointment (+1 day or +3 days)
        │
        └── 🟢 LOW ──────────────────► No auto-booking needed
```

### 1. Multimodal Vision PDF Analysis
Rather than relying solely on fragile plain-text extraction (which loses table formatting, columns, and visual reference ranges), ClinIQ uses **PyMuPDF (`fitz`)** to render each PDF page as a high-DPI image. These images are fed directly into **Gemini's Vision Engine**, allowing the model to accurately read tables, aligned numbers, reference intervals, and handwritten lab notes. *(If image conversion is unavailable, it gracefully falls back to PyPDF2 text parsing).*

### 2. Structured Diagnostic Extraction
Gemini processes the lab report and outputs structured medical data:
* **Summary**: A layman-friendly 2–3 sentence overview of the test results.
* **Key Findings**: Structured bullet points of key physiological parameters.
* **Abnormal Values**: Automatically identifies metrics outside standard reference ranges (e.g., `Glucose: 145 mg/dL (Normal: 70-99)`).
* **Clinical Significance**: Explains what elevated or reduced levels mean in clinical context.
* **Criticality Index**: Categorizes overall urgency into:
  * `CRITICAL`: Life-threatening or severely abnormal values requiring immediate intervention.
  * `MEDIUM`: Moderately abnormal values requiring medical follow-up.
  * `LOW`: Normal or borderline values.
* **Doctor Recommendation**: Always includes standard safety guidance instructing the patient to consult their doctor.

### 3. Autonomous Agentic Appointment Booking (Function Calling)
ClinIQ equips Gemini with a function calling tool: `book_doctor_appointment`.
* When the AI analyzes a report and assesses the criticality as **`CRITICAL`**, the AI agent **autonomously invokes the booking tool** to schedule a consultation with the patient's linked doctor for the **next morning (10:00 AM)**.
* When assessed as **`MEDIUM`**, the AI agent schedules an appointment **3 days later**.
* When assessed as **`LOW`**, the AI agent refrains from invoking the booking tool.
* The system attaches AI notes to the appointment (e.g., `[AI Auto-Booked - CRITICAL criticality] Elevated Fasting Blood Sugar (145 mg/dL)`).

### 4. Async Background Processing
AI processing is handled asynchronously via FastAPI `BackgroundTasks`. When a lab uploads a report, the upload response returns instantly (`201 Created`), while the PDF rendering, AI analysis, and potential auto-booking run safely in the background without freezing the UI.

---

## ⚡ Complete App Feature Matrix

| Feature | Patient | Doctor | Diagnostic Lab | AI Role |
| :--- | :---: | :---: | :---: | :--- |
| **Signup & JWT Login** | ✅ | ✅ | ✅ | Password hashing, JWT token issue |
| **Doctor Code Link/Unlink** | ✅ | ✅ (Generates) | — | Code generation (`secrets`) |
| **Book Doctor Appointments** | ✅ | ✅ | — | AI auto-books on critical reports |
| **Book Lab Appointments** | ✅ | ✅ (Prescribes) | ✅ | Schedule tracking |
| **Upload Lab Report PDF** | — | — | ✅ | Upload storage & validation |
| **PDF Multi-page Vision OCR** | — | — | — | PyMuPDF + Gemini Vision |
| **Abnormal Value Extraction** | ✅ | ✅ | ✅ | Gemini structured extraction |
| **Criticality Assessment** | ✅ | ✅ | ✅ | Gemini evaluation |
| **Auto-Appointment Booking** | ✅ | ✅ | — | Gemini Function Calling Tool |
| **Download PDF File** | ✅ | ✅ | ✅ | RBAC File Response |
| **Send/Receive Health Queries** | ✅ (Send) | ✅ (Respond) | — | Urgency sorting (`HIGH/MED/LOW`) |
| **View Patient Roster** | — | ✅ | — | Doctor-patient relationship tracking |

---

## 🛠️ Technical Architecture & Tech Stack

### Android Mobile App (`/App`)
- **Language**: Kotlin 1.9+
- **Architecture**: MVVM (Model-View-ViewModel), Repository Pattern
- **UI Components**: Material Design 3, ViewBinding, Dynamic Fragments, RecyclerViews, Custom Adapters
- **Networking**: Retrofit 2 + Gson Converter + OkHttp3 with `AuthInterceptor` (JWT Bearer tokens)
- **State & Concurrency**: Android Jetpack LiveData, ViewModel, Kotlin Coroutines
- **Session Management**: Encrypted SharedPreferences `SessionManager`

### Backend Service (`/Backend`)
- **Framework**: FastAPI (Python 3.10+) with Uvicorn ASGI Server
- **Database**: MongoDB (Async `motor` driver & `pymongo`)
- **Authentication**: JWT (JSON Web Tokens) with HS256, Passlib (`bcrypt`) password hashing
- **AI / LLM Framework**: Google Generative AI (`google-generativeai`) using `gemini-3.6-flash`, custom **Genkit Manager**
- **PDF & Vision Processing**: PyMuPDF (`fitz`), PyPDF2, Pillow (`PIL`)
- **File Management**: Secure local storage with role-based download authorization

```
                     ┌───────────────────────────┐
                     │   Android Client App      │
                     │  (Kotlin, MVVM, Retrofit) │
                     └─────────────┬─────────────┘
                                   │ HTTP / REST (JWT)
                                   ▼
                     ┌───────────────────────────┐
                     │     FastAPI Backend       │
                     │     (Python, Uvicorn)     │
                     └──────┬─────────────┬──────┘
                            │             │
              Async Motor   │             │  Generative AI
              Database      │             │  Vision & Tools
                            ▼             ▼
                     ┌──────────┐   ┌───────────┐
                     │ MongoDB  │   │  Google   │
                     │ Database │   │ Gemini AI │
                     └──────────┘   └───────────┘
```

---

## 📡 API Endpoints Summary

### Authentication (`/api/auth`)
- `POST /api/auth/signup` — Register a new account (`PATIENT`, `DOCTOR`, or `LAB`)
- `POST /api/auth/login` — Authenticate and receive JWT access token
- `POST /api/auth/refresh-token` — Refresh expired JWT token
- `GET  /api/auth/profile` — Get profile info based on user role

### User Profiles & Linking (`/api/profiles`)
- `GET  /api/profiles/me` — Get current user details
- `PUT  /api/profiles/me` — Update patient profile (name, phone, address)
- `POST /api/profiles/link-doctor` — Link patient to doctor using doctor code
- `POST /api/profiles/unlink-doctor` — Unlink patient from current doctor
- `GET  /api/profiles/my-code` — Retrieve unique Doctor Code (Doctors only)
- `GET  /api/profiles/regenerate-code` — Generate new Doctor Code (Doctors only)
- `GET  /api/profiles/my-patients` — List all patients linked to doctor
- `GET  /api/profiles/patient/{id}` — Get specific linked patient profile
- `GET  /api/profiles/patient/{id}/reports` — Get all lab reports for a linked patient
- `GET  /api/profiles/doctors` — List all active doctors
- `GET  /api/profiles/labs` — List all active labs

### Doctor & Lab Appointments (`/api/appointments`)
- `POST /api/appointments/doctor` — Patient creates doctor appointment
- `GET  /api/appointments/doctor/my-appointments` — Get doctor appointments for logged-in user
- `PUT  /api/appointments/doctor/{id}` — Update appointment status/time
- `DELETE /api/appointments/doctor/{id}` — Cancel doctor appointment
- `POST /api/appointments/lab` — Patient creates lab test appointment
- `POST /api/appointments/lab/doctor-create` — Doctor prescribes lab appointment for patient
- `GET  /api/appointments/lab/my-appointments` — Get lab appointments for logged-in user
- `PUT  /api/appointments/lab/{id}` — Update lab appointment
- `DELETE /api/appointments/lab/{id}` — Cancel lab appointment

### Lab Reports & AI Engine (`/api/reports`)
- `POST /api/reports/lab/{appointment_id}` — Upload PDF report & trigger background AI analysis
- `GET  /api/reports/lab/{appointment_id}` — Get lab report details & AI analysis
- `POST /api/reports/reanalyze/{appointment_id}` — Re-trigger AI analysis on report
- `GET  /api/reports/my-reports` — Get all reports accessible by current user
- `GET  /api/reports/download/{appointment_id}` — Download original PDF file

### Medical Queries (`/api/queries`)
- `POST /api/queries` — Patient sends query to linked doctor
- `GET  /api/queries` — Get query conversation list
- `GET  /api/queries/pending/count` — Get count of pending queries (Doctors only)
- `GET  /api/queries/pending/list` — Get list of unanswered queries (Doctors only)
- `POST /api/queries/{id}/respond` — Doctor posts response to patient query

---

## 🚀 Setup & Installation Guide

### Prerequisites
- **Python**: 3.10 or higher
- **MongoDB**: Running instance on `localhost:27017` or MongoDB Atlas URI
- **Google Gemini API Key**: Obtainable from [Google AI Studio](https://aistudio.google.com/)
- **Android Studio**: Jellyfish / Ladybug or newer with Android SDK 34+

---

### Backend Setup

1. **Navigate to the Backend directory**:
   ```bash
   cd Backend
   ```

2. **Create and activate a Python virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your credentials:
   ```ini
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=cliniq_db
   SECRET_KEY=your-super-secret-jwt-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   GOOGLE_AI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.6-flash
   DEBUG=True
   HOST=0.0.0.0
   PORT=8000
   ```

5. **Start the FastAPI Server**:
   ```bash
   python main.py
   ```
   The backend API will run at `http://localhost:8000`.
   - **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
   - **ReDoc Documentation**: `http://localhost:8000/redoc`

---

### Android App Setup

1. **Open the `App` directory in Android Studio**:
   ```bash
   cd App
   ```

2. **Configure Backend URL**:
   Ensure `RetrofitClient.kt` points to your running FastAPI server IP:
   ```kotlin
   // For Android Emulator:
   private const val BASE_URL = "http://10.0.2.2:8000/"
   // For Physical Device on same Wi-Fi:
   // private const val BASE_URL = "http://192.168.X.X:8000/"
   ```

3. **Build & Run**:
   - Build project using Gradle: `./gradlew assembleDebug`
   - Install APK onto an emulator or physical device.

---

## 🛡️ Security & Privacy

- 🔒 **Role-Based File Authorization**: Lab report PDFs can only be downloaded by the patient, their linked doctor, or the uploading lab.
- 🔑 **Password Hashing**: Industry-standard `bcrypt` password hashing via Passlib.
- 🛡️ **JWT Stateless Authentication**: Secure token verification with strict expiration and header checks.
- 🩺 **Medical Disclaimer**: AI summaries explicitly recommend professional doctor consultations for proper medical diagnosis.

---

<p center="text-align">Built with ❤️ using FastAPI, Google Gemini AI, Kotlin, and MongoDB.</p>
