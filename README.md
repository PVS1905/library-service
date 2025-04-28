# library-service
A Django REST API for managing library and book borrowing

## Installation
Clone the repository, create a virtual environment, and install dependencies

```shell
git clone https://github.com/PVS1905/library-service.git
cd library-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```
Apply migrations and run the server

```shell
python manage.py migrate
python manage.py runserver
```

### Authentication

This project uses JWT authentication.

Register: POST /api/user/register/
Login: POST /api/user/token/

```shell
Authorize: Bearer <your_token>
```
### API Documentation
Interactive API documentation is available at:

Swagger UI: http://localhost:8000/api/schema/swagger-ui/
Raw Schema: http://localhost:8000/api/schema/

Key features:

Filter borrowings (Admins only) by user ID and status is_active
Example: ?user_id=2, ?is_active=True

Authorize and test protected endpoints directly from Swagger UI

### Features

Manage Books, Borrowings
Create borrowings for available books
Filter borrowings by user ID and is_active status
JWT authentication (register/login)
Unit tests for main functionality
Swagger UI with drf-spectacular
