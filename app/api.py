# =====================================================
# LIBRARY MANAGEMENT SYSTEM - CRUD API
# FastAPI + MySQL + Pydantic
# =====================================================

from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================================================
# DATABASE CONNECTION POOL
# =====================================================

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'LibraryManagementSystem'),
    'pool_name': 'library_pool',
    'pool_size': 10,
    'pool_reset_session': True,
    'autocommit': False
}

# Global connection pool
connection_pool = None

def create_connection_pool():
    """Create MySQL connection pool"""
    global connection_pool
    try:
        connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)
        logger.info("✅ Database connection pool created successfully")
        return connection_pool
    except Exception as e:
        logger.error(f"❌ Failed to create connection pool: {e}")
        raise

def get_db_connection():
    """Get database connection from pool"""
    try:
        return connection_pool.get_connection()
    except Exception as e:
        logger.error(f"Failed to get database connection: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# =====================================================
# PYDANTIC MODELS
# =====================================================

class BookBase(BaseModel):
    isbn: str = Field(..., min_length=10, max_length=17)
    title: str = Field(..., min_length=1, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=200)
    publication_date: Optional[date] = None
    edition: Optional[int] = Field(1, ge=1)
    pages: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field("English", max_length=30)
    book_condition: Optional[str] = Field("New", pattern="^(New|Good|Fair|Poor|Damaged)$")
    location_shelf: Optional[str] = Field(None, max_length=20)
    total_copies: int = Field(..., ge=1)
    available_copies: Optional[int] = Field(None, ge=0)
    price: Optional[Decimal] = Field(None, ge=0)
    publisher_id: Optional[int] = None
    category_id: int = Field(..., gt=0)

    @validator('available_copies')
    def validate_available_copies(cls, v, values):
        if v is not None and 'total_copies' in values:
            if v > values['total_copies']:
                raise ValueError('Available copies cannot exceed total copies')
        return v

class BookCreate(BookBase):
    authors: Optional[List[Dict[str, Any]]] = []

class BookUpdate(BaseModel):
    isbn: Optional[str] = Field(None, min_length=10, max_length=17)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=200)
    publication_date: Optional[date] = None
    edition: Optional[int] = Field(None, ge=1)
    pages: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field(None, max_length=30)
    book_condition: Optional[str] = Field(None, pattern="^(New|Good|Fair|Poor|Damaged)$")
    location_shelf: Optional[str] = Field(None, max_length=20)
    total_copies: Optional[int] = Field(None, ge=1)
    available_copies: Optional[int] = Field(None, ge=0)
    price: Optional[Decimal] = Field(None, ge=0)
    publisher_id: Optional[int] = None
    category_id: Optional[int] = Field(None, gt=0)
    authors: Optional[List[Dict[str, Any]]] = None

class BookResponse(BaseModel):
    book_id: int
    isbn: str
    title: str
    subtitle: Optional[str]
    publication_date: Optional[date]
    edition: int
    pages: Optional[int]
    language: str
    book_condition: str
    location_shelf: Optional[str]
    total_copies: int
    available_copies: int
    price: Optional[Decimal]
    category_name: Optional[str]
    publisher_name: Optional[str]
    authors: Optional[str]
    created_at: datetime
    updated_at: datetime

class MemberBase(BaseModel):
    membership_number: str = Field(..., min_length=1, max_length=20)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(Male|Female|Other)$")
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    membership_type: Optional[str] = Field("Regular", pattern="^(Regular|Student|Senior|Premium)$")
    membership_start_date: date
    membership_expiry_date: date
    max_books_allowed: Optional[int] = Field(5, gt=0)

    @validator('membership_expiry_date')
    def validate_expiry_date(cls, v, values):
        if 'membership_start_date' in values and v <= values['membership_start_date']:
            raise ValueError('Expiry date must be after start date')
        return v

    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        if v and v > date.today():
            raise ValueError('Birth date cannot be in the future')
        return v

class MemberCreate(MemberBase):
    pass

class MemberUpdate(BaseModel):
    membership_number: Optional[str] = Field(None, min_length=1, max_length=20)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(Male|Female|Other)$")
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    membership_type: Optional[str] = Field(None, pattern="^(Regular|Student|Senior|Premium)$")
    membership_start_date: Optional[date] = None
    membership_expiry_date: Optional[date] = None
    is_active: Optional[bool] = None
    max_books_allowed: Optional[int] = Field(None, gt=0)

class MemberResponse(BaseModel):
    member_id: int
    membership_number: str
    first_name: str
    last_name: str
    date_of_birth: Optional[date]
    gender: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    address: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    membership_type: str
    membership_start_date: date
    membership_expiry_date: date
    is_active: bool
    max_books_allowed: int
    active_loans: Optional[int] = 0
    outstanding_fines: Optional[Decimal] = Decimal('0.00')
    created_at: datetime
    updated_at: datetime

class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int

class BookListResponse(BaseModel):
    success: bool = True
    data: List[BookResponse]
    pagination: PaginationResponse

class MemberListResponse(BaseModel):
    success: bool = True
    data: List[MemberResponse]
    pagination: PaginationResponse

class StandardResponse(BaseModel):
    success: bool = True
    message: str
    data: Any = None

# =====================================================
# FASTAPI APP INITIALIZATION
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_connection_pool()
    yield
    # Shutdown
    if connection_pool:
        # Close all connections in the pool
        pass

app = FastAPI(
    title="Library Management System API",
    description="Complete CRUD API for Library Management with Books and Members",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# =====================================================
# MIDDLEWARE
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure appropriately for production
)

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def execute_query(query: str, params: tuple = None, fetch_one: bool = False, fetch_all: bool = True):
    """Execute database query with connection handling"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount
            
        connection.commit()
        return result
    except mysql.connector.Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def execute_transaction(queries_and_params: List[tuple]):
    """Execute multiple queries in a transaction"""
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        results = []
        for query, params in queries_and_params:
            cursor.execute(query, params or ())
            if cursor.description:  # SELECT query
                results.append(cursor.fetchall())
            else:  # INSERT/UPDATE/DELETE
                results.append(cursor.rowcount)
        
        connection.commit()
        return results
    except mysql.connector.Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Transaction error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Transaction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# =====================================================
# BOOK ENDPOINTS
# =====================================================

@app.get("/api/books", response_model=BookListResponse, tags=["Books"])
async def get_books(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    available: Optional[bool] = Query(None)
):
    """Get all books with pagination, search, and filtering"""
    offset = (page - 1) * limit
    
    # Build query
    base_query = """
        SELECT 
            b.book_id, b.isbn, b.title, b.subtitle, b.publication_date,
            b.edition, b.pages, b.language, b.book_condition, b.location_shelf,
            b.total_copies, b.available_copies, b.price, b.created_at, b.updated_at,
            c.category_name, p.publisher_name,
            GROUP_CONCAT(CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') as authors
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.category_id
        LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
        LEFT JOIN book_authors ba ON b.book_id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.author_id
        WHERE 1=1
    """
    
    params = []
    count_params = []
    
    if search:
        base_query += " AND (b.title LIKE %s OR b.isbn LIKE %s OR CONCAT(a.first_name, ' ', a.last_name) LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
        count_params.extend([search_param, search_param, search_param])
    
    if category:
        base_query += " AND c.category_name = %s"
        params.append(category)
        count_params.append(category)
    
    if available is not None:
        if available:
            base_query += " AND b.available_copies > 0"
        else:
            base_query += " AND b.available_copies = 0"
    
    # Get books
    books_query = base_query + " GROUP BY b.book_id ORDER BY b.title LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    books = execute_query(books_query, tuple(params))
    
    # Get total count
    count_query = """
        SELECT COUNT(DISTINCT b.book_id) as total
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.category_id
        LEFT JOIN book_authors ba ON b.book_id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.author_id
        WHERE 1=1
    """
    
    if search:
        count_query += " AND (b.title LIKE %s OR b.isbn LIKE %s OR CONCAT(a.first_name, ' ', a.last_name) LIKE %s)"
    if category:
        count_query += " AND c.category_name = %s"
    if available is not None:
        if available:
            count_query += " AND b.available_copies > 0"
        else:
            count_query += " AND b.available_copies = 0"
    
    count_result = execute_query(count_query, tuple(count_params), fetch_one=True)
    total = count_result['total'] if count_result else 0
    
    return BookListResponse(
        data=[BookResponse(**book) for book in books],
        pagination=PaginationResponse(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit
        )
    )

@app.get("/api/books/{book_id}", response_model=StandardResponse, tags=["Books"])
async def get_book(book_id: int):
    """Get a specific book by ID"""
    query = """
        SELECT 
            b.*, c.category_name, p.publisher_name, p.address as publisher_address,
            GROUP_CONCAT(
                JSON_OBJECT(
                    'author_id', a.author_id,
                    'name', CONCAT(a.first_name, ' ', a.last_name),
                    'role', ba.author_role
                )
            ) as authors
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.category_id
        LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
        LEFT JOIN book_authors ba ON b.book_id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.author_id
        WHERE b.book_id = %s
        GROUP BY b.book_id
    """
    
    book = execute_query(query, (book_id,), fetch_one=True)
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Parse authors JSON (MySQL GROUP_CONCAT with JSON_OBJECT)
    if book.get('authors'):
        try:
            import json
            authors_list = book['authors'].split(',')
            book['authors'] = [json.loads(author) for author in authors_list]
        except:
            book['authors'] = []
    else:
        book['authors'] = []
    
    return StandardResponse(message="Book retrieved successfully", data=book)

@app.post("/api/books", response_model=StandardResponse, status_code=status.HTTP_201_CREATED, tags=["Books"])
async def create_book(book: BookCreate):
    """Create a new book"""
    try:
        # Prepare book insertion
        book_query = """
            INSERT INTO books (
                isbn, title, subtitle, publication_date, edition, pages, language,
                book_condition, location_shelf, total_copies, available_copies,
                price, publisher_id, category_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        available_copies = book.available_copies if book.available_copies is not None else book.total_copies
        
        book_params = (
            book.isbn, book.title, book.subtitle, book.publication_date,
            book.edition, book.pages, book.language, book.book_condition,
            book.location_shelf, book.total_copies, available_copies,
            book.price, book.publisher_id, book.category_id
        )
        
        queries = [(book_query, book_params)]
        
        # Execute transaction
        results = execute_transaction(queries)
        
        # Get the inserted book ID (this would need to be handled differently in a real transaction)
        # For simplicity, we'll do a separate query to get the ID
        book_id_query = "SELECT LAST_INSERT_ID() as book_id"
        book_id_result = execute_query(book_id_query, fetch_one=True)
        book_id = book_id_result['book_id']
        
        # Insert book-author relationships if provided
        if book.authors:
            for author in book.authors:
                author_query = "INSERT INTO book_authors (book_id, author_id, author_role) VALUES (%s, %s, %s)"
                execute_query(author_query, (book_id, author['author_id'], author.get('role', 'Primary Author')), fetch_all=False)
        
        return StandardResponse(
            message="Book created successfully",
            data={"book_id": book_id}
        )
        
    except mysql.connector.IntegrityError as e:
        if "isbn" in str(e).lower():
            raise HTTPException(status_code=409, detail="Book with this ISBN already exists")
        raise HTTPException(status_code=400, detail="Data integrity error")

@app.put("/api/books/{book_id}", response_model=StandardResponse, tags=["Books"])
async def update_book(book_id: int, book: BookUpdate):
    """Update a book"""
    # Check if book exists
    existing_book = execute_query("SELECT book_id FROM books WHERE book_id = %s", (book_id,), fetch_one=True)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Build dynamic update query
    update_fields = []
    params = []

    for field, value in book.dict(exclude_unset=True).items():
        if field != "authors" and value is not None:
            update_fields.append(f"{field} = %s")
            params.append(value)

    if update_fields:
        query = f"UPDATE books SET {', '.join(update_fields)}, updated_at = NOW() WHERE book_id = %s"
        params.append(book_id)
        execute_query(query, tuple(params), fetch_all=False)

    # Update authors if provided
    if book.authors is not None:
        # Delete existing relationships
        execute_query("DELETE FROM book_authors WHERE book_id = %s", (book_id,), fetch_all=False)

        # Insert new relationships
        for author in book.authors:
            author_query = "INSERT INTO book_authors (book_id, author_id, author_role) VALUES (%s, %s, %s)"
            execute_query(author_query, (book_id, author["author_id"], author.get("role", "Primary Author")), fetch_all=False)

    return StandardResponse(message="Book updated successfully")


@app.delete("/api/members/{member_id}", response_model=StandardResponse, tags=["Members"])
async def delete_member(member_id: int):
    """Delete (deactivate) a member"""
    # Check if member exists
    existing_member = execute_query("SELECT member_id FROM members WHERE member_id = %s", (member_id,), fetch_one=True)
    if not existing_member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check for active loans
    active_loans = execute_query(
        'SELECT COUNT(*) as count FROM loan_transactions WHERE member_id = %s AND loan_status = "Active"',
        (member_id,), fetch_one=True
    )
    
    if active_loans['count'] > 0:
        raise HTTPException(status_code=400, detail="Cannot delete member with active loans. Please return all books first.")
    
    # Soft delete by deactivating
    execute_query(
        "UPDATE members SET is_active = 0, updated_at = NOW() WHERE member_id = %s",
        (member_id,), fetch_all=False
    )
    
    return StandardResponse(message="Member deactivated successfully")

# =====================================================
# UTILITY ENDPOINTS
# =====================================================

@app.get("/api/categories", response_model=StandardResponse, tags=["Utilities"])
async def get_categories():
    """Get all categories"""
    categories = execute_query("SELECT * FROM categories ORDER BY category_name")
    return StandardResponse(message="Categories retrieved successfully", data=categories)

@app.get("/api/authors", response_model=StandardResponse, tags=["Utilities"])
async def get_authors(search: Optional[str] = Query(None)):
    """Get all authors with optional search"""
    if search:
        query = "SELECT * FROM authors WHERE first_name LIKE %s OR last_name LIKE %s ORDER BY last_name, first_name"
        params = (f"%{search}%", f"%{search}%")
    else:
        query = "SELECT * FROM authors ORDER BY last_name, first_name"
        params = None
    
    authors = execute_query(query, params)
    return StandardResponse(message="Authors retrieved successfully", data=authors)

@app.get("/api/publishers", response_model=StandardResponse, tags=["Utilities"])
async def get_publishers():
    """Get all publishers"""
    publishers = execute_query("SELECT * FROM publishers ORDER BY publisher_name")
    return StandardResponse(message="Publishers retrieved successfully", data=publishers)

@app.get("/api/stats", response_model=StandardResponse, tags=["Utilities"])
async def get_dashboard_stats():
    """Get dashboard statistics"""
    stats = {}
    
    # Total books
    total_books = execute_query("SELECT COUNT(*) as count FROM books", fetch_one=True)
    stats['total_books'] = total_books['count']
    
    # Available books
    available_books = execute_query("SELECT SUM(available_copies) as count FROM books", fetch_one=True)
    stats['available_books'] = available_books['count'] or 0
    
    # Total active members
    total_members = execute_query("SELECT COUNT(*) as count FROM members WHERE is_active = 1", fetch_one=True)
    stats['total_members'] = total_members['count']
    
    # Active loans
    active_loans = execute_query('SELECT COUNT(*) as count FROM loan_transactions WHERE loan_status = "Active"', fetch_one=True)
    stats['active_loans'] = active_loans['count']
    
    # Overdue loans
    overdue_loans = execute_query('SELECT COUNT(*) as count FROM loan_transactions WHERE loan_status = "Active" AND due_date < CURDATE()', fetch_one=True)
    stats['overdue_loans'] = overdue_loans['count']
    
    # Outstanding fines
    outstanding_fines = execute_query('SELECT COALESCE(SUM(amount - paid_amount), 0) as total FROM fines WHERE payment_status = "Unpaid"', fetch_one=True)
    stats['outstanding_fines'] = float(outstanding_fines['total'])
    
    return StandardResponse(message="Statistics retrieved successfully", data=stats)

# =====================================================
# LOAN MANAGEMENT ENDPOINTS (BONUS)
# =====================================================

class LoanCreate(BaseModel):
    member_id: int = Field(..., gt=0)
    book_id: int = Field(..., gt=0)
    staff_id: Optional[int] = None
    loan_date: date = Field(default_factory=date.today)
    due_date: date
    notes: Optional[str] = None

    @validator('due_date')
    def validate_due_date(cls, v, values):
        if 'loan_date' in values and v <= values['loan_date']:
            raise ValueError('Due date must be after loan date')
        return v

@app.post("/api/loans", response_model=StandardResponse, status_code=status.HTTP_201_CREATED, tags=["Loans"])
async def create_loan(loan: LoanCreate):
    """Create a new book loan"""
    # Check if book is available
    book = execute_query("SELECT available_copies FROM books WHERE book_id = %s", (loan.book_id,), fetch_one=True)
    if not book or book['available_copies'] <= 0:
        raise HTTPException(status_code=400, detail="Book is not available for loan")
    
    # Check if member exists and is active
    member = execute_query("SELECT is_active, max_books_allowed FROM members WHERE member_id = %s", (loan.member_id,), fetch_one=True)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if not member['is_active']:
        raise HTTPException(status_code=400, detail="Member account is not active")
    
    # Check member's current loan count
    current_loans = execute_query(
        'SELECT COUNT(*) as count FROM loan_transactions WHERE member_id = %s AND loan_status = "Active"',
        (loan.member_id,), fetch_one=True
    )
    if current_loans['count'] >= member['max_books_allowed']:
        raise HTTPException(status_code=400, detail="Member has reached maximum book loan limit")
    
    # Create loan transaction
    loan_query = """
        INSERT INTO loan_transactions (member_id, book_id, staff_id, loan_date, due_date, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    params = (loan.member_id, loan.book_id, loan.staff_id, loan.loan_date, loan.due_date, loan.notes)
    execute_query(loan_query, params, fetch_all=False)
    
    # Update book availability (trigger should handle this, but let's be explicit)
    execute_query("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s", (loan.book_id,), fetch_all=False)
    
    return StandardResponse(message="Book loan created successfully")

@app.put("/api/loans/{transaction_id}/return", response_model=StandardResponse, tags=["Loans"])
async def return_book(transaction_id: int):
    """Return a borrowed book"""
    # Check if loan exists and is active
    loan = execute_query(
        "SELECT * FROM loan_transactions WHERE transaction_id = %s AND loan_status = 'Active'",
        (transaction_id,), fetch_one=True
    )
    if not loan:
        raise HTTPException(status_code=404, detail="Active loan not found")
    
    # Update loan status
    execute_query(
        "UPDATE loan_transactions SET loan_status = 'Returned', return_date = CURDATE(), updated_at = NOW() WHERE transaction_id = %s",
        (transaction_id,), fetch_all=False
    )
    
    # Update book availability
    execute_query("UPDATE books SET available_copies = available_copies + 1 WHERE book_id = %s", (loan['book_id'],), fetch_all=False)
    
    return StandardResponse(message="Book returned successfully")

@app.get("/api/loans", response_model=StandardResponse, tags=["Loans"])
async def get_loans(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    member_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None, pattern="^(Active|Returned|Overdue|Lost|Damaged)$")
):
    """Get all loans with filtering"""
    offset = (page - 1) * limit
    
    base_query = """
        SELECT 
            lt.transaction_id, lt.loan_date, lt.due_date, lt.return_date, lt.loan_status,
            CONCAT(m.first_name, ' ', m.last_name) as member_name, m.membership_number,
            b.title, b.isbn,
            CASE 
                WHEN lt.due_date < CURDATE() AND lt.loan_status = 'Active' THEN 'Overdue'
                WHEN DATEDIFF(lt.due_date, CURDATE()) <= 3 AND lt.loan_status = 'Active' THEN 'Due Soon'
                ELSE lt.loan_status
            END as display_status
        FROM loan_transactions lt
        JOIN members m ON lt.member_id = m.member_id
        JOIN books b ON lt.book_id = b.book_id
        WHERE 1=1
    """
    
    params = []
    count_params = []
    
    if member_id:
        base_query += " AND lt.member_id = %s"
        params.append(member_id)
        count_params.append(member_id)
    
    if status:
        base_query += " AND lt.loan_status = %s"
        params.append(status)
        count_params.append(status)
    
    # Get loans
    loans_query = base_query + " ORDER BY lt.loan_date DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    loans = execute_query(loans_query, tuple(params))
    
    # Get total count
    count_query = """
        SELECT COUNT(*) as total
        FROM loan_transactions lt
        JOIN members m ON lt.member_id = m.member_id
        JOIN books b ON lt.book_id = b.book_id
        WHERE 1=1
    """
    if member_id:
        count_query += " AND lt.member_id = %s"
    if status:
        count_query += " AND lt.loan_status = %s"
    
    count_result = execute_query(count_query, tuple(count_params), fetch_one=True)
    total = count_result['total'] if count_result else 0
    
    return StandardResponse(
        message="Loans retrieved successfully",
        data={
            "loans": loans,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    )

# =====================================================
# ERROR HANDLERS
# =====================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"}
    )

# =====================================================
# HEALTH CHECK & ROOT ENDPOINTS
# =====================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Library Management System API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "books": "/api/books",
            "members": "/api/members",
            "loans": "/api/loans",
            "categories": "/api/categories",
            "authors": "/api/authors",
            "publishers": "/api/publishers",
            "stats": "/api/stats"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        result = execute_query("SELECT 1 as status", fetch_one=True)
        db_status = "healthy" if result else "unhealthy"
    except:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

# =====================================================
# MAIN APPLICATION ENTRY POINT
# =====================================================

if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )

@app.delete("/api/books/{book_id}", response_model=StandardResponse, tags=["Books"])
async def delete_book(book_id: int):
    """Delete a book"""
    # Check if book exists
    existing_book = execute_query("SELECT book_id FROM books WHERE book_id = %s", (book_id,), fetch_one=True)
    if not existing_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Check for active loans
    active_loans = execute_query(
        'SELECT COUNT(*) as count FROM loan_transactions WHERE book_id = %s AND loan_status = "Active"',
        (book_id,), fetch_one=True
    )
    
    if active_loans['count'] > 0:
        raise HTTPException(status_code=400, detail="Cannot delete book with active loans")
    
    # Delete book (CASCADE will handle book_authors)
    execute_query("DELETE FROM books WHERE book_id = %s", (book_id,), fetch_all=False)
    
    return StandardResponse(message="Book deleted successfully")

# =====================================================
# MEMBER ENDPOINTS
# =====================================================

@app.get("/api/members", response_model=MemberListResponse, tags=["Members"])
async def get_members(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    membership_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    """Get all members with pagination, search, and filtering"""
    offset = (page - 1) * limit
    
    base_query = """
        SELECT 
            m.*,
            COUNT(lt.transaction_id) as active_loans,
            COALESCE(SUM(CASE WHEN f.payment_status = 'Unpaid' THEN f.amount ELSE 0 END), 0) as outstanding_fines
        FROM members m
        LEFT JOIN loan_transactions lt ON m.member_id = lt.member_id AND lt.loan_status = 'Active'
        LEFT JOIN fines f ON m.member_id = f.member_id AND f.payment_status = 'Unpaid'
        WHERE 1=1
    """
    
    params = []
    count_params = []
    
    if search:
        base_query += " AND (m.first_name LIKE %s OR m.last_name LIKE %s OR m.membership_number LIKE %s OR m.email LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param, search_param])
        count_params.extend([search_param, search_param, search_param, search_param])
    
    if membership_type:
        base_query += " AND m.membership_type = %s"
        params.append(membership_type)
        count_params.append(membership_type)
    
    if is_active is not None:
        base_query += " AND m.is_active = %s"
        params.append(is_active)
        count_params.append(is_active)
    
    # Get members
    members_query = base_query + " GROUP BY m.member_id ORDER BY m.last_name, m.first_name LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    members = execute_query(members_query, tuple(params))
    
    # Get total count
    count_query = "SELECT COUNT(*) as total FROM members m WHERE 1=1"
    if search:
        count_query += " AND (m.first_name LIKE %s OR m.last_name LIKE %s OR m.membership_number LIKE %s OR m.email LIKE %s)"
    if membership_type:
        count_query += " AND m.membership_type = %s"
    if is_active is not None:
        count_query += " AND m.is_active = %s"
    
    count_result = execute_query(count_query, tuple(count_params), fetch_one=True)
    total = count_result['total'] if count_result else 0
    
    return MemberListResponse(
        data=[MemberResponse(**member) for member in members],
        pagination=PaginationResponse(
            page=page,
            limit=limit,
            total=total,
            pages=(total + limit - 1) // limit
        )
    )

@app.get("/api/members/{member_id}", response_model=StandardResponse, tags=["Members"])
async def get_member(member_id: int):
    """Get a specific member by ID with loan history"""
    member_query = """
        SELECT 
            m.*,
            COUNT(CASE WHEN lt.loan_status = 'Active' THEN 1 END) as active_loans,
            COUNT(CASE WHEN lt.loan_status = 'Returned' THEN 1 END) as completed_loans,
            COALESCE(SUM(CASE WHEN f.payment_status = 'Unpaid' THEN f.amount ELSE 0 END), 0) as outstanding_fines
        FROM members m
        LEFT JOIN loan_transactions lt ON m.member_id = lt.member_id
        LEFT JOIN fines f ON m.member_id = f.member_id AND f.payment_status = 'Unpaid'
        WHERE m.member_id = %s
        GROUP BY m.member_id
    """
    
    member = execute_query(member_query, (member_id,), fetch_one=True)
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Get recent loan history
    loan_history_query = """
        SELECT 
            lt.transaction_id, lt.loan_date, lt.due_date, lt.return_date, lt.loan_status,
            b.title, b.isbn,
            GROUP_CONCAT(CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') as authors
        FROM loan_transactions lt
        JOIN books b ON lt.book_id = b.book_id
        LEFT JOIN book_authors ba ON b.book_id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.author_id
        WHERE lt.member_id = %s
        GROUP BY lt.transaction_id
        ORDER BY lt.loan_date DESC
        LIMIT 10
    """
    
    loan_history = execute_query(loan_history_query, (member_id,))
    member['loan_history'] = loan_history
    
    return StandardResponse(message="Member retrieved successfully", data=member)

@app.post("/api/members", response_model=StandardResponse, status_code=status.HTTP_201_CREATED, tags=["Members"])
async def create_member(member: MemberCreate):
    """Create a new member"""
    try:
        query = """
            INSERT INTO members (
                membership_number, first_name, last_name, date_of_birth, gender,
                email, phone_number, address, city, postal_code, membership_type,
                membership_start_date, membership_expiry_date, max_books_allowed
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            member.membership_number, member.first_name, member.last_name,
            member.date_of_birth, member.gender, member.email, member.phone_number,
            member.address, member.city, member.postal_code, member.membership_type,
            member.membership_start_date, member.membership_expiry_date, member.max_books_allowed
        )
        
        execute_query(query, params, fetch_all=False)
        
        # Get the inserted member ID
        member_id_result = execute_query("SELECT LAST_INSERT_ID() as member_id", fetch_one=True)
        member_id = member_id_result['member_id']
        
        return StandardResponse(
            message="Member created successfully",
            data={"member_id": member_id}
        )
        
    except mysql.connector.IntegrityError as e:
        if "membership_number" in str(e).lower() or "email" in str(e).lower():
            raise HTTPException(status_code=409, detail="Member with this membership number or email already exists")
        raise HTTPException(status_code=400, detail="Data integrity error")

@app.put("/api/members/{member_id}", response_model=StandardResponse, tags=["Members"])
async def update_member(member_id: int, member: MemberUpdate):
    """Update a member"""
    # Check if member exists
    existing_member = execute_query("SELECT member_id FROM members WHERE member_id = %s", (member_id,), fetch_one=True)
    if not existing_member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Build dynamic update query
    update_fields = []
    params = []

    for field, value in member.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            params.append(value)

    if update_fields:
        query = f"UPDATE members SET {', '.join(update_fields)}, updated_at = NOW() WHERE member_id = %s"
        params.append(member_id)
        execute_query(query, tuple(params), fetch_all=False)

    return StandardResponse(message="Member updated successfully")