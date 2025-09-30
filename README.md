# Library Management System - FastAPI CRUD Application

A complete RESTful API for library management built with FastAPI, MySQL, and Pydantic. This application provides comprehensive CRUD operations for managing books, members, and loans with robust data validation and interactive documentation.

## 🚀 Features

### Core Functionality
- **Books Management**: Complete CRUD operations with advanced search and filtering
- **Members Management**: Full member lifecycle with loan tracking
- **Loan System**: Book borrowing and return functionality
- **Advanced Search**: Multi-field search across books and members
- **Pagination**: Efficient data handling with customizable page sizes
- **Data Validation**: Robust input validation using Pydantic models

### Technical Features
- **Interactive Documentation**: Auto-generated Swagger UI and ReDoc
- **Database Connection Pooling**: Efficient MySQL connection management
- **Error Handling**: Comprehensive error responses with meaningful messages
- **Type Safety**: Full type hints and validation
- **RESTful Design**: Following REST API best practices
- **Health Checks**: Database connectivity monitoring

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI 0.104.1
- **Database**: MySQL 8.0+
- **Validation**: Pydantic 2.4.2
- **Server**: Uvicorn with ASGI
- **Database Connector**: mysql-connector-python
- **Environment Management**: python-dotenv

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- MySQL 8.0 or higher
- pip (Python package installer)
- Git

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/library-management-fastapi.git
cd library-management-fastapi
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Create Database
```sql
-- Connect to MySQL and run:
CREATE DATABASE LibraryManagementSystem;
USE LibraryManagementSystem;

-- Run the complete database schema from Question 1
-- (Execute the SQL file from the database design)
```

#### Sample Data (Optional)
The database schema includes sample data for testing. You can also add your own test data.

### 5. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your database credentials
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=LibraryManagementSystem
PORT=8000
DEBUG=true
```

### 6. Run the Application
```bash
# Start the development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the Python script directly
python main.py
```

The API will be available at:
- **Application**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## 📚 API Documentation

### Books Endpoints

#### GET /api/books
Get all books with pagination and filtering
```bash
curl "http://localhost:8000/api/books?page=1&limit=10&search=python&available=true"
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 10, max: 100)
- `search` (str): Search in title, ISBN, or author names
- `category` (str): Filter by category name
- `available` (bool): Filter by availability

#### GET /api/books/{book_id}
Get a specific book by ID
```bash
curl "http://localhost:8000/api/books/1"
```

#### POST /api/books
Create a new book
```bash
curl -X POST "http://localhost:8000/api/books" \
-H "Content-Type: application/json" \
-d '{
  "isbn": "978-0-123456-78-9",
  "title": "Advanced Python Programming",
  "category_id": 6,
  "total_copies": 5,
  "price": 29.99,
  "authors": [
    {
      "author_id": 1,
      "role": "Primary Author"
    }
  ]
}'
```

#### PUT /api/books/{book_id}
Update a book
```bash
curl -X PUT "http://localhost:8000/api/books/1" \
-H "Content-Type: application/json" \
-d '{
  "title": "Updated Title",
  "price": 35.99
}'
```

#### DELETE /api/books/{book_id}
Delete a book
```bash
curl -X DELETE "http://localhost:8000/api/books/1"
```

### Members Endpoints

#### GET /api/members
Get all members with pagination and filtering
```bash
curl "http://localhost:8000/api/members?page=1&limit=10&search=john&membership_type=Premium"
```

**Query Parameters:**
- `page` (int): Page number
- `limit` (int): Items per page
- `search` (str): Search in name, membership number, or email
- `membership_type` (str): Filter by membership type
- `is_active` (bool): Filter by active status

#### GET /api/members/{member_id}
Get a specific member with loan history
```bash
curl "http://localhost:8000/api/members/1"
```

#### POST /api/members
Create a new member
```bash
curl -X POST "http://localhost:8000/api/members" \
-H "Content-Type: application/json" \
-d '{
  "membership_number": "LIB2024001",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@email.com",
  "membership_type": "Regular",
  "membership_start_date": "2024-01-01",
  "membership_expiry_date": "2025-01-01"
}'
```

#### PUT /api/members/{member_id}
Update a member
```bash
curl -X PUT "http://localhost:8000/api/members/1" \
-H "Content-Type: application/json" \
-d '{
  "email": "newemail@example.com",
  "membership_type": "Premium"
}'
```

#### DELETE /api/members/{member_id}
Deactivate a member
```bash
curl -X DELETE "http://localhost:8000/api/members/1"
```

### Loan Management Endpoints

#### POST /api/loans
Create a book loan
```bash
curl -X POST "http://localhost:8000/api/loans" \
-H "Content-Type: application/json" \
-d '{
  "member_id": 1,
  "book_id": 1,
  "due_date": "2024-02-15"
}'
```

#### PUT /api/loans/{transaction_id}/return
Return a borrowed book
```bash
curl -X PUT "http://localhost:8000/api/loans/1/return"
```

#### GET /api/loans
Get all loans with filtering
```bash
curl "http://localhost:8000/api/loans?member_id=1&status=Active"
```

### Utility Endpoints

#### GET /api/categories
Get all book categories
```bash
curl "http://localhost:8000/api/categories"
```

#### GET /api/authors
Get all authors with optional search
```bash
curl "http://localhost:8000/api/authors?search=stephen"
```

#### GET /api/publishers
Get all publishers
```bash
curl "http://localhost:8000/api/publishers"
```

#### GET /api/stats
Get dashboard statistics
```bash
curl "http://localhost:8000/api/stats"
```

### Health Check

#### GET /health
Check application and database health
```bash
curl "http://localhost:8000/health"
```

## 🧪 Testing

### Manual Testing
Use the interactive documentation at http://localhost:8000/docs to test all endpoints with a user-friendly interface.

### Automated Testing (Optional)
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## 📊 Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Response data here
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description"
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [
    // Array of items
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "pages": 10
  }
}
```

## 🔒 Data Validation

The application uses Pydantic models for comprehensive data validation:

- **Email validation** for email fields
- **Date validation** ensuring logical date relationships
- **String length validation** for all text fields
- **Numeric validation** for IDs, prices, and counts
- **Enum validation** for status fields
- **Custom validators** for business logic

## 🚀 Production Deployment

### Environment Variables
Set the following for production:
```bash
DB_HOST=your-production-db-host
DB_USER=your-db-user
DB_PASSWORD=your-secure-password
DB_NAME=LibraryManagementSystem
ENV=production
DEBUG=false
```

### Running with Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure MySQL is running
   - Verify database credentials in `.env`
   - Check if database exists

2. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

3. **Port Already in Use**
   - Change port in `.env` file
   - Or kill process using port 8000

4. **Permission Errors**
   - Ensure proper database user permissions
   - Check file system permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

- **Your Name** - [GitHub Profile](https://github.com/yourusername)

## 🙏 Acknowledgments

- FastAPI documentation and community
- MySQL documentation
- Pydantic validation library
- All contributors and testers

---

## 📈 API Performance

- **Response Time**: < 100ms for most operations
- **Concurrent Requests**: Supports high concurrency with async/await
- **Connection Pooling**: Efficient database connection management
- **Memory Usage**: Optimized with proper connection cleanup

## 🔄 Future Enhancements

- [ ] Authentication & Authorization (JWT)
- [ ] Role-based access control
- [ ] Fine management system
- [ ] Reservation system
- [ ] Email notifications
- [ ] Audit logging
- [ ] Data export features
- [ ] Advanced reporting
- [ ] Mobile app API extensions

For detailed API documentation with request/response examples, visit http://localhost:8000/docs after starting the application.