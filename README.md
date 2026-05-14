# Open Banking Marketplace Application

**Design and Implementation of an Open-Banking Marketplace Application for Loan Transactions**

By ILOEGBUNAM VALERIAN CHIMDINDU  
Veritas University, Abuja, Nigeria  
Department of Computer Science

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Installation](#installation)
7. [Usage](#usage)
8. [Screenshots](#screenshots)
9. [API Documentation](#api-documentation)
10. [Contributors](#contributors)

---

## Overview

The Open Banking Marketplace is a web-based platform that connects borrowers with multiple financial institutions (lenders) through secure Open Banking APIs. The system enables borrowers to link their bank accounts, receive AI-driven credit scores, and obtain personalized loan offers from various lenders. Lenders can create loan products, review applications, and make competitive offers.

This project implements the research work titled *"Design and Implementation of an Open-Banking Marketplace Application for Loan Transactions"* submitted to Veritas University, Abuja.

---

## Key Features

### For Borrowers
- **User Registration & Authentication** - Role-based access control with borrower/lender/admin roles
- **Bank Account Linking** - Simulated Open Banking integration with major Nigerian banks
- **Loan Application** - Submit loan applications with detailed financial information
- **AI Credit Scoring** - Machine learning-based credit assessment using bank transaction data
- **Loan Comparison** - Compare offers from multiple lenders side by side
- **Real-time Notifications** - Get notified about application status and new offers
- **Repayment Tracking** - Track loan repayments and payment schedules

### For Lenders
- **Product Management** - Create and manage loan products with flexible terms
- **Application Review** - Review incoming applications with credit score insights
- **Loan Offers** - Make personalized loan offers to qualified borrowers
- **Analytics Dashboard** - Track product performance and application metrics

### For Administrators
- **System Analytics** - Monitor platform usage, loan metrics, and user activity
- **User Management** - Manage users and verification statuses
- **Data Visualization** - Interactive charts for applications, users, and financial data

---

## System Architecture

The application follows a modular Django architecture with the following components:

```
openbanking_marketplace/
|-- openbanking_marketplace/    # Project configuration
|-- apps/
|   |-- accounts/               # User authentication & profiles
|   |-- loans/                  # Loan products, applications & credit scoring
|   |-- marketplace/            # Dashboard & marketplace views
|   |-- banking/                # Open Banking integration (simulated)
|   |-- notifications/          # Notification system
|   |-- analytics/              # Admin analytics & reporting
|-- templates/                  # HTML templates
|-- static/                     # CSS, JS, images
|-- media/                      # User uploads
|-- manage.py                   # Django management script
|-- requirements.txt            # Python dependencies
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Django 5.0 (Python) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Database** | SQLite (development) / PostgreSQL (production) |
| **Cache** | Database cache (development) / Redis (production) |
| **Styling** | Custom CSS with CSS variables |
| **Charts** | Chart.js |
| **Icons** | Font Awesome 6 |
| **Fonts** | Inter (Google Fonts) |

---

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd openbanking_marketplace
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main app: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

---

## Usage

### As a Borrower
1. Register as a borrower
2. Complete your profile with personal and financial information
3. Link your bank account(s) through the Open Banking integration
4. Browse available loan products
5. Submit a loan application
6. Wait for credit scoring and loan offers from lenders
7. Compare and accept the best offer

### As a Lender
1. Register as a lender with company details
2. Create loan products with your terms and conditions
3. Review incoming loan applications
4. Check applicant credit scores
5. Make personalized loan offers
6. Track accepted offers and disbursements

### As an Administrator
1. Access the admin panel at `/admin/`
2. Monitor system analytics and user activity
3. Manage users, loan products, and applications
4. View reports and data visualizations

---

## API Documentation

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register/` | POST | Register a new user |
| `/login/` | POST | User login |
| `/logout/` | GET | User logout |
| `/profile/` | GET/POST | View/edit profile |

### Loan Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/loans/products/` | GET | List loan products |
| `/loans/products/<id>/` | GET | Product details |
| `/loans/apply/` | GET/POST | Submit loan application |
| `/loans/my-applications/` | GET | List my applications |
| `/loans/credit-score/` | GET | View credit score |

### Banking Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/banking/accounts/` | GET | List linked accounts |
| `/banking/accounts/link/` | GET/POST | Link new account |

---

## Contributors

**ILOEGBUNAM VALERIAN CHIMDINDU**  
Student, Computer Science Department  
Veritas University, Abuja, Nigeria  
Supervised by Mr. Ezeiruaku Chidozie Perpetua

---

## License

This project is developed for academic purposes at Veritas University, Abuja.

---

## Acknowledgments

Special thanks to:
- Mr. Ezeiruaku Chidozie Perpetua - Project Supervisor
- Veritas University, Abuja - For providing the academic environment
- All open-source contributors whose libraries made this project possible
