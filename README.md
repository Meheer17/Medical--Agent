# Nithin App - FastAPI Backend

A FastAPI backend application with user authentication, JWT tokens, and MySQL database integration.

## Features

- ✅ User Registration (Signup)
- ✅ User Login with JWT tokens
- ✅ JWT Token Refresh
- ✅ Password hashing with bcrypt
- ✅ MySQL database integration with SQLAlchemy ORM
- ✅ CORS support for frontend integration
- ✅ User profile endpoint
- ✅ Comprehensive error handling
- 🚀 Ready for future integration with Tesseract, Genkit, and Ollama LLM

## Project Structure

```
nithin-app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── database.py          # Database setup and session management
├── models.py            # SQLAlchemy ORM models (User model)
├── schemas.py           # Pydantic models for request/response validation
├── auth.py              # Password hashing and JWT utilities
├── routes_auth.py       # Authentication routes (signup, login, refresh)
├── dependencies.py      # FastAPI dependencies for authentication
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
└── README.md           # This file
```

## Installation

### 1. Clone and Setup

```bash
cd /var/home/mahi17/Github/nithin-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Copy `.env.example` to `.env` and update with your MySQL credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=mysql+mysql-connector-python://root:your_password@localhost:3306/nithin_db
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 4. Create MySQL Database

```bash
mysql -u root -p
CREATE DATABASE nithin_db;
```

### 5. Run the Application

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication Routes

#### 1. Signup (User Registration)
- **Endpoint**: `POST /api/auth/signup`
- **Description**: Register a new user account
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "john_doe",
    "password": "SecurePass123!",
    "full_name": "John Doe"
  }
  ```
- **Response** (201):
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": false,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
  ```

#### 2. Login
- **Endpoint**: `POST /api/auth/login`
- **Description**: Authenticate user and get JWT token
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "SecurePass123!"
  }
  ```
- **Response** (200):
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "john_doe",
      "full_name": "John Doe",
      "is_active": true,
      "is_verified": false,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  }
  ```

#### 3. Refresh Token
- **Endpoint**: `POST /api/auth/refresh-token`
- **Description**: Get a new access token
- **Query Parameter**: `token` - current valid JWT token
- **Response** (200): Same as login response

### User Routes

#### 4. Get Current User
- **Endpoint**: `GET /api/users/me`
- **Description**: Get current authenticated user information
- **Headers**: `Authorization: Bearer {token}`
- **Response** (200): User object

### Health Check

#### 5. Health Check
- **Endpoint**: `GET /health`
- **Description**: Check if API is running
- **Response** (200):
  ```json
  {
    "status": "healthy",
    "message": "API is running successfully"
  }
  ```

## Testing with cURL

### Signup
```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

### Get Current User (use the token from login)
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Models

### User Model
- `id`: Primary key (Auto-increment)
- `email`: Unique email address
- `username`: Unique username (3-50 chars)
- `hashed_password`: Bcrypt hashed password
- `full_name`: Optional full name
- `is_active`: Account active status
- `is_verified`: Email verification status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

## Security Features

✅ Password hashing with bcrypt
✅ JWT token-based authentication
✅ CORS support
✅ Input validation with Pydantic
✅ SQL injection prevention (SQLAlchemy ORM)
✅ Error handling without exposing sensitive info

## Future Integration

This backend is prepared for future enhancements:
- **Tesseract**: Document/Image processing capabilities
- **Genkit**: Google's AI framework for LLM interactions
- **Ollama**: Local LLM model hosting
- **Agentic Features**: AI agent capabilities

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication failures)
- `403`: Forbidden (deactivated account)
- `404`: Not Found
- `500`: Internal Server Error

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | localhost:3306 |
| `SECRET_KEY` | JWT signing key | dev-key |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `DEBUG` | Debug mode | True |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

## Notes

⚠️ **Production Checklist**:
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Update `CORS` allowed origins
- [ ] Use environment-specific `.env` files
- [ ] Setup HTTPS
- [ ] Configure database backups
- [ ] Setup proper logging

## Support

For issues or questions, please contact the development team.
