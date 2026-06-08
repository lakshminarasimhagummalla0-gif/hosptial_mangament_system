import os
from datetime import datetime, date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hospital_management_secret_key_123')

# Determine Database Connection (supports local SQLite, MySQL/Postgres in Prod)
db_uri = os.environ.get('DATABASE_URL')
if db_uri:
    # Render PostgreSQL compatibility fix
    if db_uri.startswith("postgres://"):
        db_uri = db_uri.replace("postgres://", "postgresql://", 1)
else:
    # Check for MySQL individual environment variables
    mysql_user = os.environ.get('MYSQL_USER')
    mysql_password = os.environ.get('MYSQL_PASSWORD')
    mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
    mysql_port = os.environ.get('MYSQL_PORT', '3306')
    mysql_db = os.environ.get('MYSQL_DATABASE', 'hospital_db')
    
    if mysql_user and mysql_password:
        db_uri = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
    else:
        # Fallback to local SQLite database in the flask instance folder
        os.makedirs(os.path.join(app.instance_path), exist_ok=True)
        db_uri = f"sqlite:///{os.path.join(app.instance_path, 'hospital.db')}"

app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ----------------- DATABASE MODELS -----------------

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    op_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), default='patient123', nullable=False)
    address = db.Column(db.Text)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade="all, delete-orphan")
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient {self.name} ({self.op_number})>"

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), default='doctor123', nullable=False)
    availability = db.Column(db.String(100), default='Mon-Sat (9:00 AM - 5:00 PM)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True, cascade="all, delete-orphan")
    prescriptions = db.relationship('Prescription', backref='doctor', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Doctor {self.name} - {self.specialization}>"

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, Cancelled, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Appointment P_ID:{self.patient_id} D_ID:{self.doctor_id} Date:{self.appointment_date}>"

class Medicine(db.Model):
    __tablename__ = 'medicines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    batch_number = db.Column(db.String(50), nullable=False)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    price = db.Column(db.Float, default=0.00, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    prescriptions = db.relationship('Prescription', backref='medicine', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Medicine {self.name} (Stock: {self.stock_quantity})>"

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    instructions = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending, Dispensed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Prescription Med:{self.medicine_id} Qty:{self.quantity} Status:{self.status}>"

# ----------------- DYNAMIC OP NUMBER GENERATION -----------------

def generate_op_number():
    """Generates a unique, chronological OP registration number like OP-YYYY-XXXX."""
    current_year = datetime.now().year
    prefix = f"OP-{current_year}-"
    
    last_patient = Patient.query.filter(Patient.op_number.like(f"{prefix}%")).order_by(Patient.id.desc()).first()
    if last_patient:
        try:
            last_seq = int(last_patient.op_number.split('-')[-1])
            new_seq = last_seq + 1
        except (ValueError, IndexError):
            new_seq = 1
    else:
        new_seq = 1
        
    return f"{prefix}{new_seq:04d}"

# ----------------- DATABASE SEEDING -----------------

def init_sample_data():
    """Seeds the database with high-quality sample data if tables are empty."""
    if Doctor.query.first() is None:
        doctors_sample = [
            Doctor(name='Dr. Sarah Jenkins', specialization='Cardiology', phone='+1-555-0199', email='sarah.jenkins@hospital.com', password='doctor123', availability='Mon-Wed-Fri (9:00 AM - 1:00 PM)'),
            Doctor(name='Dr. Robert Chen', specialization='Pediatrics', phone='+1-555-0188', email='robert.chen@hospital.com', password='doctor123', availability='Mon-Tue-Thu-Fri (10:00 AM - 4:00 PM)'),
            Doctor(name='Dr. Emily Taylor', specialization='Dermatology', phone='+1-555-0177', email='emily.taylor@hospital.com', password='doctor123', availability='Tue-Thu-Sat (1:00 PM - 5:00 PM)'),
            Doctor(name='Dr. Marcus Vance', specialization='Neurology', phone='+1-555-0166', email='marcus.vance@hospital.com', password='doctor123', availability='Wed-Fri (10:00 AM - 2:00 PM)'),
            Doctor(name='Dr. Sophia Patel', specialization='General Medicine', phone='+1-555-0155', email='sophia.patel@hospital.com', password='doctor123', availability='Mon-Sat (9:00 AM - 5:00 PM)')
        ]
        db.session.bulk_save_objects(doctors_sample)
        db.session.commit()

    if Patient.query.first() is None:
        patients_sample = [
            Patient(op_number='OP-2026-0001', name='John Doe', age=45, gender='Male', phone='+1-555-0123', email='john.doe@email.com', password='patient123', address='123 Pine St, Metroville'),
            Patient(op_number='OP-2026-0002', name='Jane Smith', age=29, gender='Female', phone='+1-555-0456', email='jane.smith@email.com', password='patient123', address='456 Oak Ave, Riverside'),
            Patient(op_number='OP-2026-0003', name='William Johnson', age=72, gender='Male', phone='+1-555-0789', email='william.j@email.com', password='patient123', address='789 Maple Rd, Greenfield'),
            Patient(op_number='OP-2026-0004', name='Sophia Martinez', age=8, gender='Female', phone='+1-555-0987', email='sophia.m@email.com', password='patient123', address='321 Elm St, Springfield'),
            Patient(op_number='OP-2026-0005', name='Michael Brown', age=37, gender='Male', phone='+1-555-0654', email='michael.b@email.com', password='patient123', address='654 Birch Blvd, Hillside')
        ]
        db.session.bulk_save_objects(patients_sample)
        db.session.commit()

    if Appointment.query.first() is None:
        appointments_sample = [
            Appointment(patient_id=1, doctor_id=5, appointment_date=date(2026, 6, 8), time_slot='10:00 AM', reason='Routine annual checkup', status='Scheduled'),
            Appointment(patient_id=2, doctor_id=1, appointment_date=date(2026, 6, 9), time_slot='11:30 AM', reason='Follow-up for hypertension', status='Scheduled'),
            Appointment(patient_id=4, doctor_id=2, appointment_date=date(2026, 6, 9), time_slot='02:00 PM', reason='Mild fever and cough', status='Scheduled'),
            Appointment(patient_id=3, doctor_id=4, appointment_date=date(2026, 6, 10), time_slot='09:00 AM', reason='Frequent headaches', status='Scheduled'),
            Appointment(patient_id=5, doctor_id=3, appointment_date=date(2026, 6, 8), time_slot='03:30 PM', reason='Allergic skin reaction', status='Completed')
        ]
        db.session.bulk_save_objects(appointments_sample)
        db.session.commit()

    if Medicine.query.first() is None:
        medicines_sample = [
            Medicine(name='Paracetamol 500mg', batch_number='BTC-PCM01', stock_quantity=500, price=2.50, expiry_date=date(2028, 12, 31)),
            Medicine(name='Amoxicillin 250mg', batch_number='BTC-AMX05', stock_quantity=120, price=12.80, expiry_date=date(2027, 6, 30)),
            Medicine(name='Atorvastatin 20mg', batch_number='BTC-ATV09', stock_quantity=85, price=24.50, expiry_date=date(2028, 3, 31)),
            Medicine(name='Ibuprofen 400mg', batch_number='BTC-IBU02', stock_quantity=300, price=3.20, expiry_date=date(2027, 10, 31)),
            Medicine(name='Lisinopril 10mg', batch_number='BTC-LIS04', stock_quantity=5, price=18.00, expiry_date=date(2027, 2, 28)),
            Medicine(name='Metformin 500mg', batch_number='BTC-MET08', stock_quantity=250, price=8.50, expiry_date=date(2028, 5, 31))
        ]
        db.session.bulk_save_objects(medicines_sample)
        db.session.commit()

    if Prescription.query.first() is None:
        prescriptions_sample = [
            Prescription(patient_id=1, doctor_id=5, medicine_id=1, quantity=10, instructions='Take 1 tablet every 8 hours as needed for fever', status='Dispensed'),
            Prescription(patient_id=2, doctor_id=1, medicine_id=3, quantity=30, instructions='Take 1 tablet daily before sleep', status='Pending'),
            Prescription(patient_id=5, doctor_id=3, medicine_id=4, quantity=15, instructions='Take 1 tablet twice a day after meals', status='Pending')
        ]
        db.session.bulk_save_objects(prescriptions_sample)
        db.session.commit()

# Create Tables & Seed Data
with app.app_context():
    db.create_all()
    init_sample_data()

# ----------------- SECURITY & UTILITY WRAPPERS -----------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session:
            flash('Session expired or authentication required.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session:
                flash('Session expired or authentication required.', 'warning')
                return redirect(url_for('login'))
            if session['role'] not in roles:
                flash('Unauthorized access scope.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_form(*keys, required=None):
    """Fetches and strips fields from request form. Returns None if required fields are missing."""
    data = {k: request.form.get(k, '').strip() for k in keys}
    if required and not all(data.get(k) for k in required):
        return None
    return data

def db_commit_or_rollback(success_msg, error_msg, redirect_to, success_category='success'):
    """Helper to commit database session, flash success/error, and redirect."""
    try:
        db.session.commit()
        flash(success_msg, success_category)
    except Exception as e:
        db.session.rollback()
        flash(f"{error_msg}: {str(e)}", 'danger')
    return redirect(url_for(redirect_to))

# ----------------- AUTHENTICATION ROUTES -----------------

# ----------------- AUTHENTICATION ROUTES -----------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Roles-based portal login entry endpoint."""
    if 'role' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        session.clear()
        role = request.form.get('role')
        username = request.form.get('username', '').strip()  # Matches Email or Username
        password = request.form.get('password', '').strip()
        
        if role == 'admin':
            if username == 'admin' and password == 'admin123':
                session.update({'role': 'admin', 'user_name': 'Administrator'})
                flash('Successfully logged in as System Admin.', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid System Admin credentials.', 'danger')
        else:
            user = Doctor.query.filter_by(email=username).first() if role == 'doctor' else Patient.query.filter((Patient.email == username) | (Patient.op_number == username)).first()
            if user and user.password == password:
                session.update({'role': role, 'user_id': user.id, 'user_name': user.name})
                flash(f"{'Logged in as' if role == 'doctor' else 'Welcome back,'} {user.name}!", 'success')
                return redirect(url_for('dashboard'))
            flash(f"Invalid {role.capitalize() if role else 'user'} credentials.", 'danger')
                
    return render_template('index.html', active_page='login', all_doctors=Doctor.query.all(), all_patients=Patient.query.all())

@app.route('/register', methods=['POST'])
def register():
    """Allows new patients to self-register from the portal login page."""
    data = get_form('name', 'age', 'gender', 'phone', 'email', 'password', 'address', 
                    required=['name', 'age', 'gender', 'phone', 'email', 'password'])
    if not data:
        flash('Please fill in all required registration fields.', 'danger')
        return redirect(url_for('login'))
        
    if Patient.query.filter_by(email=data['email']).first() or Doctor.query.filter_by(email=data['email']).first():
        flash('Email is already registered in the system.', 'danger')
        return redirect(url_for('login'))
        
    try:
        op_number = generate_op_number()
        new_patient = Patient(
            op_number=op_number,
            name=data['name'],
            age=int(data['age']),
            gender=data['gender'],
            phone=data['phone'],
            email=data['email'],
            password=data['password'],
            address=data['address'] or None
        )
        db.session.add(new_patient)
        db.session.commit()
        
        session.update({'role': 'patient', 'user_id': new_patient.id, 'user_name': new_patient.name})
        flash(f'Registration successful! Welcome to CareSync. Your unique OP Registration Code is: {op_number}', 'success')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f'Registration error: {str(e)}', 'danger')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    """Clear session data and logout."""
    session.clear()
    flash('Successfully logged out.', 'info')
    return redirect(url_for('login'))

# ----------------- MAIN PORTAL DASHBOARD -----------------

@app.route('/')
@login_required
def dashboard():
    """Dynamic Dashboard based on user session role."""
    role = session.get('role')
    if role == 'admin':
        return render_template(
            'index.html',
            patient_count=Patient.query.count(),
            doctor_count=Doctor.query.count(),
            appointment_count=Appointment.query.filter_by(status='Scheduled').count(),
            medicine_count=Medicine.query.count(),
            low_stock_count=Medicine.query.filter(Medicine.stock_quantity < 10).count(),
            recent_appointments=Appointment.query.order_by(Appointment.id.desc()).limit(5).all(),
            recent_patients=Patient.query.order_by(Patient.registered_at.desc()).limit(5).all(),
            active_page='dashboard'
        )
    elif role == 'doctor':
        doc_id = session.get('user_id')
        return render_template(
            'index.html',
            doctor=Doctor.query.get_or_404(doc_id),
            appointments=Appointment.query.filter_by(doctor_id=doc_id).order_by(Appointment.appointment_date.desc(), Appointment.time_slot).all(),
            patients=Patient.query.order_by(Patient.name).all(),
            medicines=Medicine.query.order_by(Medicine.name).all(),
            prescriptions=Prescription.query.filter_by(doctor_id=doc_id).order_by(Prescription.id.desc()).all(),
            active_page='dashboard'
        )
    elif role == 'patient':
        pat_id = session.get('user_id')
        return render_template(
            'index.html',
            patient=Patient.query.get_or_404(pat_id),
            appointments=Appointment.query.filter_by(patient_id=pat_id).order_by(Appointment.appointment_date.desc(), Appointment.time_slot).all(),
            prescriptions=Prescription.query.filter_by(patient_id=pat_id).order_by(Prescription.id.desc()).all(),
            doctors=Doctor.query.order_by(Doctor.name).all(),
            active_page='dashboard',
            date_today=date.today()
        )

# --- 1. PATIENT MANAGEMENT (ADMIN ONLY) ---

@app.route('/patients')
@role_required(['admin'])
def patients_list():
    q = request.args.get('q', '').strip()
    patients = Patient.query.filter(
        Patient.name.like(f"%{q}%") | Patient.op_number.like(f"%{q}%") | Patient.phone.like(f"%{q}%")
    ).all() if q else Patient.query.order_by(Patient.id.desc()).all()
    return render_template('index.html', patients=patients, search_query=q, active_page='patients')

@app.route('/patients/register', methods=['POST'])
@role_required(['admin'])
def patient_register():
    data = get_form('name', 'age', 'gender', 'phone', 'email', 'password', 'address',
                    required=['name', 'age', 'gender', 'phone', 'email'])
    if not data:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('patients_list'))
    
    if Patient.query.filter_by(email=data['email']).first() or Doctor.query.filter_by(email=data['email']).first():
        flash('Email is already registered in the system.', 'danger')
        return redirect(url_for('patients_list'))
        
    op_number = generate_op_number()
    db.session.add(Patient(
        op_number=op_number,
        name=data['name'],
        age=int(data['age']),
        gender=data['gender'],
        phone=data['phone'],
        email=data['email'],
        password=data['password'] or 'patient123',
        address=data['address'] or None
    ))
    return db_commit_or_rollback(f'Patient registered successfully. OP Number: {op_number}', 'Registration error', 'patients_list')

@app.route('/patients/edit/<int:id>', methods=['POST'])
@role_required(['admin'])
def patient_edit(id):
    patient = Patient.query.get_or_404(id)
    data = get_form('name', 'age', 'gender', 'phone', 'email', 'password', 'address',
                    required=['name', 'age', 'gender', 'phone', 'email'])
    if not data:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('patients_list'))
        
    patient.name = data['name']
    patient.age = int(data['age'])
    patient.gender = data['gender']
    patient.phone = data['phone']
    patient.email = data['email']
    if data['password']:
        patient.password = data['password']
    patient.address = data['address'] or None
    return db_commit_or_rollback('Patient record updated.', 'Error updating patient', 'patients_list')

@app.route('/patients/delete/<int:id>', methods=['POST'])
@role_required(['admin'])
def patient_delete(id):
    db.session.delete(Patient.query.get_or_404(id))
    return db_commit_or_rollback('Patient record deleted.', 'Deletion error', 'patients_list')

# --- 2. DOCTOR MANAGEMENT (ADMIN ONLY) ---

@app.route('/doctors')
@role_required(['admin'])
def doctors_list():
    return render_template('index.html', doctors=Doctor.query.order_by(Doctor.name).all(), active_page='doctors')

@app.route('/doctors/add', methods=['POST'])
@role_required(['admin'])
def doctor_add():
    data = get_form('name', 'specialization', 'phone', 'email', 'password', 'availability',
                    required=['name', 'specialization', 'phone', 'email'])
    if not data:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('doctors_list'))
        
    if Doctor.query.filter_by(email=data['email']).first() or Patient.query.filter_by(email=data['email']).first():
        flash('Email is already registered.', 'danger')
        return redirect(url_for('doctors_list'))
        
    db.session.add(Doctor(
        name=data['name'],
        specialization=data['specialization'],
        phone=data['phone'],
        email=data['email'],
        password=data['password'] or 'doctor123',
        availability=data['availability'] or 'Mon-Sat (9:00 AM - 5:00 PM)'
    ))
    return db_commit_or_rollback(f"Doctor Profile created for {data['name']}.", 'Error creating doctor record', 'doctors_list')

@app.route('/doctors/edit/<int:id>', methods=['POST'])
@role_required(['admin'])
def doctor_edit(id):
    doctor = Doctor.query.get_or_404(id)
    data = get_form('name', 'specialization', 'phone', 'email', 'password', 'availability',
                    required=['name', 'specialization', 'phone', 'email'])
    if not data:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('doctors_list'))
        
    doctor.name = data['name']
    doctor.specialization = data['specialization']
    doctor.phone = data['phone']
    doctor.email = data['email']
    if data['password']:
        doctor.password = data['password']
    doctor.availability = data['availability'] or 'Mon-Sat (9:00 AM - 5:00 PM)'
    return db_commit_or_rollback('Doctor profile updated.', 'Error updating doctor', 'doctors_list')

@app.route('/doctors/delete/<int:id>', methods=['POST'])
@role_required(['admin'])
def doctor_delete(id):
    doctor = Doctor.query.get_or_404(id)
    db.session.delete(doctor)
    return db_commit_or_rollback(f'Doctor profile for {doctor.name} deleted.', 'Error deleting doctor', 'doctors_list')

# --- 3. APPOINTMENT MANAGEMENT ---

@app.route('/appointments')
@login_required
@role_required(['admin'])
def appointments_list():
    """View all appointments (Admin Only)."""
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc(), Appointment.time_slot).all()
    patients = Patient.query.order_by(Patient.name).all()
    doctors = Doctor.query.order_by(Doctor.name).all()
    return render_template('index.html', appointments=appointments, patients=patients, doctors=doctors, active_page='appointments')

@app.route('/appointments/book', methods=['POST'])
@login_required
@role_required(['admin', 'patient'])
def appointment_book():
    """Allows patient to book for themselves or admin to book for any patient."""
    role = session.get('role')
    
    if role == 'patient':
        patient_id = session.get('user_id')
    else:
        patient_id = request.form.get('patient_id')
        
    doctor_id = request.form.get('doctor_id')
    appointment_date_str = request.form.get('appointment_date')
    time_slot = request.form.get('time_slot')
    reason = request.form.get('reason', '').strip()
    
    if not patient_id or not doctor_id or not appointment_date_str or not time_slot:
        flash('Please fill in all required scheduling fields.', 'danger')
        return redirect(url_for('dashboard'))
        
    try:
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        if appointment_date < date.today():
            flash('Cannot book appointments on past dates.', 'warning')
            return redirect(url_for('dashboard'))
            
        new_appointment = Appointment(
            patient_id=int(patient_id),
            doctor_id=int(doctor_id),
            appointment_date=appointment_date,
            time_slot=time_slot,
            reason=reason if reason else None,
            status='Scheduled'
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash('Appointment successfully scheduled!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Scheduling error: {str(e)}', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/appointments/cancel/<int:id>', methods=['POST'])
@role_required(['admin', 'patient'])
def appointment_cancel(id):
    """Cancel appointment."""
    appointment = Appointment.query.get_or_404(id)
    if session.get('role') == 'patient' and appointment.patient_id != session.get('user_id'):
        flash('Unauthorized cancellation request.', 'danger')
        return redirect(url_for('dashboard'))
        
    appointment.status = 'Cancelled'
    return db_commit_or_rollback('Appointment status set to Cancelled.', 'Error updating status', 'dashboard', 'info')

@app.route('/appointments/complete/<int:id>', methods=['POST'])
@role_required(['admin', 'doctor'])
def appointment_complete(id):
    """Mark appointment as complete."""
    appointment = Appointment.query.get_or_404(id)
    if session.get('role') == 'doctor' and appointment.doctor_id != session.get('user_id'):
        flash('Unauthorized operation.', 'danger')
        return redirect(url_for('dashboard'))
        
    appointment.status = 'Completed'
    return db_commit_or_rollback('Appointment status logged as Completed.', 'Error updating status', 'dashboard')

# --- 4. MEDICINE INVENTORY (ADMIN ONLY) ---

@app.route('/medicines')
@role_required(['admin'])
def medicines_list():
    q = request.args.get('q', '').strip()
    medicines = Medicine.query.filter(
        Medicine.name.like(f"%{q}%") | Medicine.batch_number.like(f"%{q}%")
    ).all() if q else Medicine.query.order_by(Medicine.name).all()
    return render_template('index.html', medicines=medicines, search_query=q, active_page='medicines', date_today=date.today())

@app.route('/medicines/add', methods=['POST'])
@role_required(['admin'])
def medicine_add():
    data = get_form('name', 'batch_number', 'stock_quantity', 'price', 'expiry_date',
                    required=['name', 'batch_number', 'expiry_date'])
    if not data:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('medicines_list'))
        
    if Medicine.query.filter_by(name=data['name']).first():
        flash(f'Medicine "{data["name"]}" already exists in inventory.', 'danger')
        return redirect(url_for('medicines_list'))
        
    try:
        db.session.add(Medicine(
            name=data['name'],
            batch_number=data['batch_number'],
            stock_quantity=int(data['stock_quantity'] or 0),
            price=float(data['price'] or 0.00),
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        ))
        return db_commit_or_rollback(f"Medicine \"{data['name']}\" added to database.", 'Error', 'medicines_list')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('medicines_list'))

@app.route('/medicines/edit/<int:id>', methods=['POST'])
@role_required(['admin'])
def medicine_edit(id):
    medicine = Medicine.query.get_or_404(id)
    data = get_form('name', 'batch_number', 'stock_quantity', 'price', 'expiry_date',
                    required=['name', 'batch_number', 'expiry_date'])
    if not data:
        flash('Please fill in all required fields.', 'danger')
        return redirect(url_for('medicines_list'))
        
    existing = Medicine.query.filter_by(name=data['name']).first()
    if existing and existing.id != id:
        flash(f'Another medicine with the name "{data["name"]}" already exists.', 'danger')
        return redirect(url_for('medicines_list'))
        
    try:
        medicine.name = data['name']
        medicine.batch_number = data['batch_number']
        medicine.stock_quantity = int(data['stock_quantity'] or 0)
        medicine.price = float(data['price'] or 0.00)
        medicine.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        return db_commit_or_rollback('Medicine catalog updated.', 'Error', 'medicines_list')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('medicines_list'))

@app.route('/medicines/update-stock/<int:id>', methods=['POST'])
@role_required(['admin'])
def medicine_update_stock(id):
    medicine = Medicine.query.get_or_404(id)
    try:
        medicine.stock_quantity = int(request.form.get('stock_quantity', '0').strip())
        return db_commit_or_rollback(f'Stock level adjusted for {medicine.name}.', 'Error updating stock', 'medicines_list')
    except Exception as e:
        flash(f'Error updating stock: {e}', 'danger')
        return redirect(url_for('medicines_list'))

@app.route('/medicines/delete/<int:id>', methods=['POST'])
@role_required(['admin'])
def medicine_delete(id):
    medicine = Medicine.query.get_or_404(id)
    db.session.delete(medicine)
    return db_commit_or_rollback(f'Medicine "{medicine.name}" deleted.', 'Error', 'medicines_list')

# --- 5. PRESCRIPTION MANAGEMENT (ROLE-BASED FLOW) ---

@app.route('/prescriptions')
@role_required(['admin'])
def prescriptions_list():
    """List all prescriptions in the system for dispensing (Admin Only)."""
    return render_template('index.html', prescriptions=Prescription.query.order_by(Prescription.id.desc()).all(), active_page='prescriptions')

@app.route('/prescriptions/add', methods=['POST'])
@role_required(['doctor'])
def prescription_add():
    """Allows doctors to request medicines for patients."""
    patient_id = request.form.get('patient_id')
    medicine_id = request.form.get('medicine_id')
    quantity = request.form.get('quantity', '1').strip()
    instructions = request.form.get('instructions', '').strip()
    
    if not patient_id or not medicine_id or not quantity:
        flash('Complete all prescription fields.', 'danger')
        return redirect(url_for('dashboard'))
        
    try:
        db.session.add(Prescription(
            patient_id=int(patient_id),
            doctor_id=session.get('user_id'),
            medicine_id=int(medicine_id),
            quantity=int(quantity),
            instructions=instructions or None,
            status='Pending'
        ))
        return db_commit_or_rollback('Prescription/Medicine request successfully logged.', 'Error generating prescription', 'dashboard')
    except Exception as e:
        flash(f'Error generating prescription: {e}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/prescriptions/dispense/<int:id>', methods=['POST'])
@role_required(['admin'])
def prescription_dispense(id):
    """Allows Admin to dispense pending medicines, deducting stock quantity."""
    prescription = Prescription.query.get_or_404(id)
    if prescription.status == 'Dispensed':
        flash('Prescription has already been dispensed.', 'warning')
        return redirect(url_for('prescriptions_list'))
        
    medicine = Medicine.query.get(prescription.medicine_id)
    if not medicine:
        flash('Medicine not found in catalog.', 'danger')
        return redirect(url_for('prescriptions_list'))
        
    if medicine.stock_quantity < prescription.quantity:
        flash(f'Insufficient stock for {medicine.name}. Available: {medicine.stock_quantity}. Requested: {prescription.quantity}.', 'danger')
        return redirect(url_for('prescriptions_list'))
        
    medicine.stock_quantity -= prescription.quantity
    prescription.status = 'Dispensed'
    return db_commit_or_rollback(f'Dispensed {prescription.quantity} units of {medicine.name}. Stock updated successfully.', 'Error dispensing', 'prescriptions_list')

# --- ERROR PAGE HANDLERS ---

@app.errorhandler(404)
@app.errorhandler(500)
def handle_errors(e):
    code = getattr(e, 'code', 500)
    msg = "Page Not Found" if code == 404 else "Internal Server Error"
    return render_template('index.html', content_error=f"{code} - {msg}", active_page=''), code

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
