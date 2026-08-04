# Appointment Management API

A RESTful Appointment Management System built with Django and Django REST Framework.

## Features

- User Authentication (JWT)
- User Authentication (authtoken)
- Custom User Model
- Role-based Permissions (Admin, Doctor, Patient)
- Doctor Working Hours
- Appointment Booking
- Available Time Slot Generation
- Appointment Cancellation
- Down Payment via ZarinPal
- Payment Verification
- Final Payment Registration
- Search, Pagination and Filtering
- Swagger/OpenAPI Documentation 

---

## Technologies

- Python 3.12
- Django 4.2
- Django REST Framework
- SQLite (can be replaced with PostgreSQL)
- Simple JWT
- Simple authtoken
- ZarinPal Payment Gateway
- drf-spectacular (OpenAPI 3 Documentation)


---

## Installation

Clone the repository

```bash
git clone https://github.com/mohammadzakerii/Appointment-Management-System.git
cd appointment_management
```

Create a virtual environment

linux/macOS

```bash
python3 -m venv venv
```

windows

```bash
python -m venv venv
```

Activate the virtual environment

Linux/macOS

```bash
source venv/bin/activate
```

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Apply migrations

```bash
python manage.py migrate
```

Run the server

```bash
python manage.py runserver
```

---

## Authentication

This project implements two authentication methods:

- JWT Authentication using Simple JWT
- Token Authentication using Django REST Framework authtoken

Features:

- User Registration
- User Login
- User Logout
- JWT Refresh Token
- Token Blacklisting

## Appointment Flow

1. Doctor defines working hours.
2. Patient checks available time slots.
3. Patient books an appointment.
4. Patient pays the down payment through ZarinPal.
5. Payment is verified.
6. Appointment status becomes scheduled.
7. Patient visits the doctor.
8. Doctor or Admin registers the final payment.
9. Appointment status becomes completed.

---

## Permissions

| Role | Permissions |
|------|-------------|
| Admin | Full access |
| Doctor | Manage appointments and working hours |
| Patient | Book and manage own appointments |

---

## Payment

This project integrates with the ZarinPal payment gateway.

Implemented features:

- Payment Request
- Payment Verification
- Down Payment
- Remaining Payment Registration

---

## API Documentation


Swagger/OpenAPI documentation is available using drf-spectacular.

Swagger UI:

http://127.0.0.1:8000/api/docs





---

## Author

Mohamad Zakeri

Backend Developer