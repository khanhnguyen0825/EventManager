# 🎫 Event Management System

A comprehensive event management and ticketing system built with microservices architecture using Flask.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

Event Management System is a full-stack web application designed for event organizers, venues, and ticket buyers. The system uses a **microservices architecture** with 6 independent services that communicate via REST APIs.

Perfect for:

- 🎪 Event management companies
- 🎤 Concert and conference organizers
- 🏢 Venue management
- 🎟️ Online ticket sales

## ✨ Features

### For Event Organizers (Admin)

- 👥 **Customer Management**: Track client information and collaboration history
- 📅 **Event Planning**: Create and manage events with detailed information
- 📍 **Venue Management**: Manage multiple venues with capacity and pricing
- 📊 **Reporting**: Generate post-event reports and analytics
- 🎫 **Ticket Tracking**: Monitor ticket sales and availability

### For Customers (Public)

- 🎟️ **Easy Booking**: Book tickets without registration
- 📧 **Email Confirmation**: Receive tickets with QR codes instantly
- 🔍 **Ticket Lookup**: Check ticket status by email
- 📱 **Mobile-Friendly**: Responsive design for all devices

### System Features

- ✅ Automatic QR code generation for tickets
- ✅ Email notifications with ticket details
- ✅ Limit 4 tickets per email per event
- ✅ Real-time ticket availability tracking
- ✅ Unique ticket codes (EV01-1, EV01-2, etc.)
- ✅ Event completion workflow with reporting

## 🏗️ Architecture

### Microservices Design

```
┌─────────────────────────────────────────────────────────────────┐
│                     Event Management System                      │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │  Auth   │          │Customer │          │  Event  │
   │ :5000   │─────────▶│ :5001   │◀─────────│  :5002  │
   └─────────┘          └─────────┘          └─────────┘
        │                     │                     │
        │              ┌──────┴──────┐             │
        │         ┌────▼────┐   ┌───▼─────┐       │
        │         │ Report  │   │  Place  │       │
        │         │  :5003  │   │  :5005  │       │
        │         └─────────┘   └─────────┘       │
        │                                          │
        │              ┌───────────┐               │
        └─────────────▶│  Public   │◀──────────────┘
                       │   :5004   │
                       └───────────┘
```

### Services Overview

| Service              | Port | Description                                 | Database      |
| -------------------- | ---- | ------------------------------------------- | ------------- |
| **Auth Service**     | 5000 | Admin authentication & session management   | Session-based |
| **Customer Service** | 5001 | Customer CRUD operations & history tracking | customers.db  |
| **Event Service**    | 5002 | Event management & ticket booking (Core)    | events.db     |
| **Report Service**   | 5003 | Post-event reporting & analytics            | reports.db    |
| **Public Service**   | 5004 | Public-facing ticket booking interface      | None          |
| **Place Service**    | 5005 | Venue management with pricing & capacity    | places.db     |

## 🛠️ Technologies

### Backend

- **Framework**: Flask 3.0.0
- **ORM**: Flask-SQLAlchemy 3.1.1
- **Database**: SQLite (development) - easily upgradable to PostgreSQL/MySQL
- **HTTP Client**: Requests 2.31.0

### Features & Libraries

- **QR Code Generation**: qrcode[pil] 7.4.2
- **Email Validation**: email-validator 2.1.0.post1
- **Environment Management**: python-dotenv 1.0.0
- **Email Service**: SMTP with MIME

### Frontend

- **Template Engine**: Jinja2
- **Styling**: HTML5, CSS3, Bootstrap
- **JavaScript**: Vanilla JS

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/event-management-system.git
cd event-management-system
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure Email (Optional)**

Create a `.env` file in `event_service/` directory:

```env
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

> **Note**: For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833?hl=en)

4. **Initialize Databases**

The databases will be created automatically on first run. Each service creates its own SQLite database in the `instance/` folder.

5. **Run the application**

**Option A: Run all services at once (Windows)**

```bash
run_all_services.bat
```

**Option B: Run each service individually**

```bash
# Terminal 1 - Auth Service
cd auth_service
python run.py

# Terminal 2 - Customer Service
cd customer_service
python run.py

# Terminal 3 - Event Service
cd event_service
python run.py

# Terminal 4 - Report Service
cd report_service
python run.py

# Terminal 5 - Public Service
cd public_service
python run.py

# Terminal 6 - Place Service
cd place_service
python run.py
```

6. **Access the application**

- **Admin Login**: http://localhost:5000 (username: `admin`, password: `admin123`)
- **Customer Management**: http://localhost:5001
- **Event Management**: http://localhost:5002
- **Reports**: http://localhost:5003
- **Public Booking** ⭐: http://localhost:5004 (For end users)
- **Venue Management**: http://localhost:5005

## 🚀 Usage

### For Event Organizers

1. **Login** at http://localhost:5000
   - Username: `admin`
   - Password: `admin123`

2. **Add Customers** at http://localhost:5001/customers/add
   - Enter customer details
   - Track collaboration history

3. **Create Events** at http://localhost:5002/events/add
   - Select customer
   - Set event details and total tickets
   - System auto-generates event code (EV01, EV02, etc.)

4. **Manage Venues** at http://localhost:5005/place/
   - Add venues with capacity and pricing
   - Track availability status

5. **Generate Reports** at http://localhost:5003/report/
   - Write post-event summaries
   - Track feedback and outcomes

### For Customers (Public Users)

1. **Browse Events** at http://localhost:5004/public/register
   - View available events
   - See ticket availability

2. **Book Tickets**
   - Enter your details (name, email, phone)
   - Select number of tickets (max 4 per email)
   - Submit booking

3. **Receive Confirmation**
   - Email with QR code sent instantly
   - Ticket code and event details included
   - Check-in instructions provided

4. **Check Your Tickets** at http://localhost:5004/public/lookup
   - Enter your email
   - View all your booked tickets

## 📚 API Documentation

### Event Service API

#### Get Events by Customer

```http
GET /events/api/by_customer/<customer_id>
```

#### Get Available Events

```http
GET /events/api/available
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "Tech Conference 2026",
    "date": "2026-03-15",
    "total_tickets": 100,
    "booked_count": 45
  }
]
```

#### Book Ticket

```http
POST /events/api/book_ticket
Content-Type: application/json

{
  "event_id": 1,
  "quantity": 2,
  "buyer_name": "John Doe",
  "buyer_email": "john@example.com",
  "buyer_phone": "0123456789"
}
```

**Response:**

```json
{
  "success": true,
  "ticket_ids": [1, 2],
  "quantity": 2
}
```

#### Lookup Tickets

```http
GET /events/api/lookup_ticket?email=john@example.com
```

### Customer Service API

#### Get Customer by ID

```http
GET /customers/api/<customer_id>
```

#### Auto-Create Customer

```http
POST /customers/api/auto_create
Content-Type: application/json

{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "0987654321"
}
```

### Place Service API

#### Get All Venues

```http
GET /place/api/venues
```

#### Create Venue

```http
POST /place/api/venues
Content-Type: application/json

{
  "name": "Grand Hall",
  "type": "Conference Room",
  "capacity": 500,
  "address": "123 Main St",
  "price_per_hour": 1000000
}
```

## 📁 Project Structure

```
project/
│
├── 📄 requirements.txt              # Python dependencies
├── 🚀 run_all_services.bat          # Launch all services
├── 📖 README.md                     # This file
│
├── 🔐 auth_service/                 # Authentication service
│   ├── run.py
│   └── app/
│       ├── routes.py
│       ├── templates/
│       └── static/
│
├── 👥 customer_service/             # Customer management
│   ├── run.py
│   ├── app/
│   │   ├── models.py               # Customer model
│   │   ├── routes.py
│   │   ├── templates/
│   │   └── static/
│   └── instance/
│       └── customers.db
│
├── 🎫 event_service/                # Event & ticketing (CORE)
│   ├── run.py
│   ├── app/
│   │   ├── models.py               # Event, Ticket models
│   │   ├── routes.py
│   │   ├── email_service.py        # Email with QR codes
│   │   ├── templates/
│   │   └── static/
│   └── instance/
│       └── events.db
│
├── 📊 report_service/               # Reporting & analytics
│   ├── run.py
│   ├── app/
│   │   ├── models.py               # Report model
│   │   ├── routes.py
│   │   ├── templates/
│   │   └── static/
│   └── instance/
│       └── reports.db
│
├── 🌐 public_service/               # Public booking interface
│   ├── run.py
│   └── app/
│       ├── routes.py
│       ├── templates/
│       └── static/
│
├── 📍 place_service/                # Venue management
│   ├── run.py
│   ├── app/
│   │   ├── models.py               # Venue model
│   │   ├── routes.py
│   │   ├── templates/
│   │   └── static/
│   └── instance/
│       └── places.db
│
└── 📚 docs/
    └── HUONG_DAN_VAN_DAP_DEFENSE.md
```

## 🎨 Screenshots

### Admin Dashboard

Manage customers, events, and venues from a centralized dashboard.

### Event Management

Create events with automatic ticket generation and tracking.

### Public Booking Interface

User-friendly ticket booking without registration required.

### Email Confirmation

Professional email with QR code and event details.

## 🔐 Security & Validation

- **Authentication**: Session-based authentication for admin users
- **Input Validation**: Email validation, quantity checks
- **Business Rules**:
  - Maximum 4 tickets per email per event
  - Unique ticket codes for each booking
  - QR code security with encoded ticket information
- **Email Verification**: Uses email-validator library

## 📝 Database Schema

### Customer Model

```python
- id: Integer (Primary Key)
- name: String(100)
- email: String(100)
- phone: String(20)
- address: String(200)
- history: Text
- feedback: Text
```

### Event Model

```python
- id: Integer (Primary Key)
- event_code: String(10) UNIQUE
- name: String(100)
- date: String(50)
- description: Text
- customer_id: Integer
- total_tickets: Integer
- is_completed: Boolean
- created_at: DateTime
```

### Ticket Model

```python
- id: Integer (Primary Key)
- event_id: Integer (Foreign Key)
- ticket_code: String(30) UNIQUE
- status: String(20)  # available/booked/cancelled
- buyer_name: String(100)
- buyer_email: String(100)
- buyer_phone: String(20)
- booked_at: DateTime
```

### Venue Model

```python
- id: Integer (Primary Key)
- name: String(100)
- type: String(50)
- capacity: Integer
- address: String(200)
- price_per_hour: Float
- status: String(20)  # available/booked
```

### Report Model

```python
- id: Integer (Primary Key)
- event_id: Integer
- summary: Text
- feedback: Text
- created_at: DateTime
```

### Coding Standards

- Follow PEP 8 style guide for Python code
- Write clear commit messages
- Add comments for complex logic
- Update documentation for new features
