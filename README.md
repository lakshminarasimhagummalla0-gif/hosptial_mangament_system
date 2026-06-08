# CareSync - Modern Mini Hospital Management System

CareSync is a clean, professional, and visually stunning **Hospital Management System** designed for medical centers to manage OP registrations, doctor listings, patient appointments, and pharmacy inventory.

Built using **Python Flask**, **SQLAlchemy**, and a premium modern **Bootstrap 5 + CSS Glassmorphism** frontend, this project is fully functional, responsive, and suitable as a software engineering mini-project for resumes and college submissions.

---

## 🚀 Key Features & Modules

### 1. **Interactive Dashboard**
- Real-time statistics cards (Total Patients, Active Doctors, Scheduled Appointments, Medicine Catalog).
- Low Stock warnings for medications (< 10 units).
- Summary logs displaying recently registered patients and upcoming appointments.
- Quick navigation shortcuts.

### 2. **OP Patient Registration**
- Quick patient registry with validation.
- **Auto-generated Unique OP Numbers** in the format `OP-YYYY-XXXX` (e.g., `OP-2026-0001`).
- Dynamic patient search (live client-side filtering + backend queries).
- Fully interactive inline modals to edit details, and safe confirmation dialogs to delete profiles.

### 3. **Doctor Directory**
- Add medical practitioners with specialization, phone, email, and available times.
- View doctor directory lists and update schedules.
- Doctors automatically populate appointment booking selectors.

### 4. **Appointment Management**
- Book appointments by matching registered patients with active doctors.
- Real-time date boundary checking (past dates disabled).
- Time-slot scheduling selectors.
- Update appointment status: Mark as **Completed** or **Cancelled** with instant badge states.

### 5. **Pharmacy & Medicine Inventory**
- Tracks stock levels, prices, batch numbers, and expiry dates.
- Automatic **Low Stock alerts** highlighting critical levels.
- **Quick Restock modal** to update quantities without reloading pages.
- Expiry date validation with red warnings on the screen.

---

## 🛠️ Technology Stack
*   **Backend:** Python Flask
*   **ORM / Database Layer:** Flask-SQLAlchemy (Supports SQLite locally & MySQL/Postgre in production)
*   **Database:** MySQL (Production/Production-ready) / SQLite (Local default)
*   **Frontend:** HTML5, Modern CSS3 (Glassmorphism, animations, gradients), Vanilla JavaScript (Live search, alerts, clock)
*   **Framework:** Bootstrap 5 (Responsive Layout with sticky sidebar)
*   **WSGI Server:** Gunicorn (For Render cloud deployment)

---

## 📂 Project Structure
```text
hospital_management_system/
├── app.py                     # Main Flask application, routing logic, and database schemas
├── requirements.txt           # Python application dependencies
├── Procfile                   # Process configuration file for Render deployment
├── .gitignore                 # Config file specifying untracked local files
├── README.md                  # Complete documentation and setup manual
├── database/
│   ├── schema.sql             # Reference raw SQL Database Schema
│   └── sample_data.sql        # Reference raw SQL Seed Sample Data
└── templates/
    └── index.html             # Single unified layout containing CSS, JS, and all views (SPA style)
```

---

## 💻 Local Setup & Installation

### Option A: Quick Run (Using Default SQLite - Easiest)
CareSync has a built-in auto-configuration engine. If no MySQL database environment variables are set, it automatically initializes a local SQLite database file in the `instance/` folder and seeds it with mock patient, doctor, and inventory records so it looks beautiful instantly!

1.  **Clone / Download** this repository.
2.  **Open terminal** inside the project directory.
3.  Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    venv\Scripts\activate   # On Windows
    source venv/bin/activate  # On macOS/Linux
    ```
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Run the application:
    ```bash
    python app.py
    ```
6.  Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

### Option B: Local MySQL Configuration
To run CareSync using a local MySQL server instead of SQLite:

1.  Open your MySQL command-line client or phpMyAdmin.
2.  Create the database:
    ```sql
    CREATE DATABASE hospital_db;
    ```
3.  Create a `.env` file in the root of your project directory and configure the database environment variables:
    ```env
    SECRET_KEY=your_secret_key_here
    MYSQL_USER=root
    MYSQL_PASSWORD=your_mysql_password
    MYSQL_HOST=localhost
    MYSQL_PORT=3306
    MYSQL_DATABASE=hospital_db
    ```
4.  Run `python app.py`. Flask-SQLAlchemy will automatically detect the configuration, connect to your MySQL database, and create the schema tables and insert mock sample data!

---

## 🛠️ Git & GitHub Setup Guide

Follow these steps to store your project on GitHub (needed for Render deployment):

1.  **Initialize Git Repository:**
    ```bash
    git init
    ```
2.  **Stage and Commit Files:**
    ```bash
    git add .
    git commit -m "Initial commit - Modern Hospital Management System"
    ```
3.  **Link to GitHub Repository:**
    - Go to GitHub, create a new public/private repository named `hospital_management_system`. Do NOT initialize with README or .gitignore.
    - Copy the repository remote URL.
    - Run:
      ```bash
      git branch -M main
      git remote add origin <your-github-repo-url>
      git push -u origin main
      ```

---

## ☁️ Free Render Cloud Deployment Guide (100% Free of Cost)

Render is an excellent platform for deploying Flask applications. Follow these steps to host your app online with a free-tier MySQL database.

### Step 1: Set up a Free MySQL Database on Aiven.io
Render does not offer a free MySQL database natively. We can easily use **Aiven** (which offers a generous free tier for MySQL, Postgres, and Redis):

1.  Sign up for a free account at [Aiven.io](https://aiven.io).
2.  Click **Create Service** and select **MySQL**.
3.  Select the Cloud Provider (e.g., AWS or GCP) and a Region close to you.
4.  Choose the **Free Tier** plan.
5.  Name your service (e.g., `care-sync-mysql`) and click **Create Service**.
6.  Once the service starts (takes ~2 minutes), copy the **URI** connection string. It will look like this:
    `mysql://user:password@host:port/defaultdb?ssl-mode=REQUIRED`

### Step 2: Deploy Flask App on Render
1.  Sign up or log in at [Render.com](https://render.com).
2.  Click **New +** and select **Web Service**.
3.  Connect your GitHub account and select your `hospital_management_system` repository.
4.  Configure the service details:
    *   **Name:** `caresync-hms`
    *   **Region:** Select same region as your database
    *   **Branch:** `main`
    *   **Runtime:** `Python`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `gunicorn app:app` (Gunicorn is specified in the requirements)
    *   **Instance Type:** **Free**
5.  Click the **Advanced** drop-down to configure environment variables.

### Step 3: Add Environment Variables on Render
Click **Add Environment Variable** and insert:

| Key | Value | Notes |
| :--- | :--- | :--- |
| `SECRET_KEY` | `SomeRandomLongSecretString` | Secures sessions |
| `DATABASE_URL` | `mysql+pymysql://<user>:<password>@<host>:<port>/defaultdb` | Connection URI copied from Aiven (Be sure to replace `mysql://` with `mysql+pymysql://` at the start) |

*Note: Flask uses `pymysql` to connect to MySQL databases, which is why we change the prefix to `mysql+pymysql://`.*

6.  Click **Deploy Web Service**.
7.  Wait for the build log to complete. Your website will be live at the provided `.onrender.com` link!

---

## 🔒 License
This project is open-source. Feel free to download, customize, and submit it for your college course or portfolio!
