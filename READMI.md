# Appointment Management API

A RESTful Appointment Management System built with Django and Django REST Framework.

## Features

- User Authentication (JWT)
- User Authentication (DRF Token Authentication)
- user Authentication (OTP)
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
- Unit Tests
- Dockerized Development Environment
- PostgreSQL Support

---

## Technologies

- Python 3.12
- Django 4.2
- Django REST Framework
- SQLite (Local Development)
- PostgreSQL (Docker)
- Simple JWT
- Django REST Framework Authtoken
- ZarinPal Payment Gateway
- drf-spectacular (OpenAPI 3 Documentation)
- Docker
- Docker Compose

---

## Installation

Clone the repository:

```bash
git clone https://github.com/mohammadzakerii/Appointment-Management-System.git
cd Appointment-Management-System
```

Create a virtual environment:

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Database

The project supports two database environments:

- **SQLite** for local development
- **PostgreSQL** for Docker environment

---

## Docker

The project includes a Dockerized environment using Django and PostgreSQL.

Environment variables can be configured using `.env.example`.

```bash
cp .env.example .env
```

The Docker environment uses PostgreSQL as the database.

---

## Authentication

This project implements two authentication methods:

- JWT Authentication using Simple JWT
- Token Authentication using Django REST Framework Authtoken

Authentication features include:


- User Registration
- OTP-based Authentication
- User Login
- User Logout
- JWT Access Token
- JWT Refresh Token
- Token Blacklisting
- DRF Token Authentication

---

## Appointment Flow

The main appointment workflow is:

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

## Appointment Management

The appointment system provides:

- Doctor working hour management
- Working days configuration
- Automatic time slot generation
- Available slot retrieval
- Appointment creation
- Appointment cancellation
- Appointment status management
- Doctor-specific appointment management
- Patient-specific appointment management

Available time slots are generated based on:

- Doctor working hours
- Appointment date
- Service duration
- Existing booked appointments

---

## Permissions

The application uses role-based permissions.

| Role | Permissions |
|------|------------|
| Admin | Full access |
| Doctor | Manage own appointments and working hours |
| Patient | Book and manage own appointments |

Access to resources is restricted based on the authenticated user's role and ownership where required.

---

## Payment

This project integrates with the **ZarinPal** payment gateway for appointment payments.

Implemented features:

- Payment Request
- Payment URL Generation
- Down Payment
- Payment Verification
- Payment Status Management
- Remaining Payment Registration
- Final Payment Registration

The payment flow supports down payment and final payment. 
After successful down payment verification, the appointment can proceed as scheduled. 
After the final payment is registered, the appointment status is updated to `completed`
---

## API Documentation

Swagger/OpenAPI documentation is provided using **drf-spectacular**.

### Swagger UI

http://127.0.0.1:8000/api/docs/

### OpenAPI Schema

http://127.0.0.1:8000/api/schema/

The Swagger interface can be used to:

- Explore API endpoints
- View request and response schemas
- Test API endpoints
- Authenticate requests
- Review API documentation

---

## Testing

The project includes automated tests for API endpoints and application logic.

Tests cover different parts of the application including:

- Authentication
- Appointment management
- Working hours
- Available time slots
- Permissions
- Payment functionality
- API behavior

Run tests locally:

```bash
python manage.py test
```

Run tests with Docker:

```bash
docker compose exec web python manage.py test
```

---

## Project Structure

A simplified project structure:

```text
Appointment-Management-System/
│
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
 
│
├── appointment/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── payment/
│   ├── models.py
│   ├── services.py
│   ├── serializers.py
│   ├── views.py
│   └── tests.py
│
└── ...
```

---

## Development Highlights

The project focuses on implementing real-world backend concepts, including:

- RESTful API design
- Role-based access control
- Custom permission classes
- Serializer-based validation
- Appointment scheduling logic
- Dynamic time slot generation
- Transactional database operations
- Payment gateway integration
- JWT authentication
- Token blacklisting
- Search, filtering and pagination
- Automated API testing
- Mocking external services
- Dockerized deployment environment
- PostgreSQL database integration

---

## Author

**Mohamad Zakeri**

Backend Developer

GitHub:

https://github.com/mohammadzakerii