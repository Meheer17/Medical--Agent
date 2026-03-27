-- Create database
CREATE DATABASE IF NOT EXISTS cliniq_db;

-- Create user 'mahi' with all privileges
CREATE USER IF NOT EXISTS 'mahi'@'localhost' IDENTIFIED BY 'mahi@123';

-- Grant all privileges on cliniq_db
GRANT ALL PRIVILEGES ON cliniq_db.* TO 'mahi'@'localhost';

-- Grant global privileges
GRANT ALL PRIVILEGES ON *.* TO 'mahi'@'localhost' WITH GRANT OPTION;

-- Flush privileges to apply changes
FLUSH PRIVILEGES;

-- Show created user
SELECT User, Host FROM mysql.user WHERE User='mahi';

-- Show databases
SHOW DATABASES;

-- Use the database
USE cliniq_db;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NULL,
    role ENUM('DOCTOR', 'PATIENT', 'LAB') DEFAULT 'PATIENT' NOT NULL,
    doctor_code VARCHAR(20) UNIQUE NULL,
    linked_doctor_id INT NULL,
    phone VARCHAR(20) NULL,
    address VARCHAR(500) NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (linked_doctor_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_doctor_code (doctor_code),
    INDEX idx_linked_doctor_id (linked_doctor_id),
    INDEX idx_is_active (is_active)
);

-- Create doctor_appointments table
CREATE TABLE IF NOT EXISTS doctor_appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    reason TEXT,
    notes TEXT,
    status ENUM('SCHEDULED', 'CONFIRMED', 'CANCELLED', 'COMPLETED') DEFAULT 'SCHEDULED' NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_status (status),
    INDEX idx_appointment_date (appointment_date)
);

-- Create lab_appointments table
CREATE TABLE IF NOT EXISTS lab_appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT,
    lab_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    test_type VARCHAR(255) NOT NULL,
    reason TEXT,
    notes TEXT,
    status ENUM('SCHEDULED', 'CONFIRMED', 'CANCELLED', 'COMPLETED') DEFAULT 'SCHEDULED' NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (lab_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_lab_id (lab_id),
    INDEX idx_status (status),
    INDEX idx_appointment_date (appointment_date)
);

-- Create lab_reports table
CREATE TABLE IF NOT EXISTS lab_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    uploaded_by_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT NOT NULL,
    mime_type VARCHAR(50) DEFAULT 'application/pdf' NOT NULL,
    test_results TEXT,
    notes TEXT,
    ai_summary LONGTEXT NULL COMMENT 'AI-generated summary of lab report',
    ai_key_findings LONGTEXT NULL COMMENT 'JSON array of key findings from report',
    ai_abnormal_values LONGTEXT NULL COMMENT 'JSON array of abnormal/out-of-range values',
    ai_clinical_significance LONGTEXT NULL COMMENT 'AI interpretation of clinical significance',
    ai_criticality VARCHAR(50) DEFAULT 'low' NULL COMMENT 'AI-assessed criticality: critical, medium, low',
    ai_doctor_recommendation LONGTEXT NULL COMMENT 'Recommendations including mandatory doctor visit reminder',
    ai_analysis_status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED') DEFAULT 'PENDING' NOT NULL COMMENT 'Status of AI analysis',
    ai_analysis_error TEXT NULL COMMENT 'Error message if analysis failed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES lab_appointments(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_appointment_id (appointment_id),
    INDEX idx_uploaded_by_id (uploaded_by_id),
    INDEX idx_ai_analysis_status (ai_analysis_status),
    INDEX idx_created_at (created_at),
    UNIQUE KEY unique_appointment_id (appointment_id)
);

-- Create queries table for single query/response system
CREATE TABLE IF NOT EXISTS queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    query_text TEXT NOT NULL,
    response_text TEXT NULL,
    urgency ENUM('LOW', 'MEDIUM', 'HIGH') DEFAULT 'MEDIUM' NOT NULL,
    is_responded BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    responded_at DATETIME NULL,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_is_responded (is_responded),
    INDEX idx_urgency (urgency),
    INDEX idx_created_at (created_at)
);