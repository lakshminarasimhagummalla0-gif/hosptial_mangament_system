USE hospital_db;

-- Insert Sample Doctors (with default password 'doctor123' and unique email constraints)
INSERT INTO doctors (name, specialization, phone, email, password, availability) VALUES
('Dr. Sarah Jenkins', 'Cardiology', '+1-555-0199', 'sarah.jenkins@hospital.com', 'doctor123', 'Mon-Wed-Fri (9:00 AM - 1:00 PM)'),
('Dr. Robert Chen', 'Pediatrics', '+1-555-0188', 'robert.chen@hospital.com', 'doctor123', 'Mon-Tue-Thu-Fri (10:00 AM - 4:00 PM)'),
('Dr. Emily Taylor', 'Dermatology', '+1-555-0177', 'emily.taylor@hospital.com', 'doctor123', 'Tue-Thu-Sat (1:00 PM - 5:00 PM)'),
('Dr. Marcus Vance', 'Neurology', '+1-555-0166', 'marcus.vance@hospital.com', 'doctor123', 'Wed-Fri (10:00 AM - 2:00 PM)'),
('Dr. Sophia Patel', 'General Medicine', '+1-555-0155', 'sophia.patel@hospital.com', 'doctor123', 'Mon-Sat (9:00 AM - 5:00 PM)');

-- Insert Sample Patients (with default password 'patient123' and unique emails)
INSERT INTO patients (op_number, name, age, gender, phone, email, password, address) VALUES
('OP-2026-0001', 'John Doe', 45, 'Male', '+1-555-0123', 'john.doe@email.com', 'patient123', '123 Pine St, Metroville'),
('OP-2026-0002', 'Jane Smith', 29, 'Female', '+1-555-0456', 'jane.smith@email.com', 'patient123', '456 Oak Ave, Riverside'),
('OP-2026-0003', 'William Johnson', 72, 'Male', '+1-555-0789', 'william.j@email.com', 'patient123', '789 Maple Rd, Greenfield'),
('OP-2026-0004', 'Sophia Martinez', 8, 'Female', '+1-555-0987', 'sophia.m@email.com', 'patient123', '321 Elm St, Springfield'),
('OP-2026-0005', 'Michael Brown', 37, 'Male', '+1-555-0654', 'michael.b@email.com', 'patient123', '654 Birch Blvd, Hillside');

-- Insert Sample Appointments
INSERT INTO appointments (patient_id, doctor_id, appointment_date, time_slot, reason, status) VALUES
(1, 5, '2026-06-08', '10:00 AM', 'Routine annual checkup', 'Scheduled'),
(2, 1, '2026-06-09', '11:30 AM', 'Follow-up for hypertension', 'Scheduled'),
(4, 2, '2026-06-09', '02:00 PM', 'Mild fever and cough', 'Scheduled'),
(3, 4, '2026-06-10', '09:00 AM', 'Frequent headaches', 'Scheduled'),
(5, 3, '2026-06-08', '03:30 PM', 'Allergic skin reaction', 'Completed');

-- Insert Sample Medicines
INSERT INTO medicines (name, batch_number, stock_quantity, price, expiry_date) VALUES
('Paracetamol 500mg', 'BTC-PCM01', 500, 2.50, '2028-12-31'),
('Amoxicillin 250mg', 'BTC-AMX05', 120, 12.80, '2027-06-30'),
('Atorvastatin 20mg', 'BTC-ATV09', 85, 24.50, '2028-03-31'),
('Ibuprofen 400mg', 'BTC-IBU02', 300, 3.20, '2027-10-31'),
('Lisinopril 10mg', 'BTC-LIS04', 5, 18.00, '2027-02-28'),
('Metformin 500mg', 'BTC-MET08', 250, 8.50, '2028-05-31');

-- Insert Sample Prescriptions (Medicine Requests)
INSERT INTO prescriptions (patient_id, doctor_id, medicine_id, quantity, instructions, status) VALUES
(1, 5, 1, 10, 'Take 1 tablet every 8 hours as needed for fever', 'Dispensed'),
(2, 1, 3, 30, 'Take 1 tablet daily at night before sleep', 'Pending'),
(5, 3, 4, 15, 'Take 1 tablet twice a day after meals', 'Pending');
