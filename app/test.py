# test_api.py - Manual API Testing Script

import requests
import json
from datetime import date, timedelta
import pytest
import httpx
from fastapi.testclient import TestClient
from api import app

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_books_api():
    """Test Books CRUD operations"""
    print("=== Testing Books API ===")
    
    # Test GET all books
    print("\n1. Testing GET /api/books")
    response = requests.get(f"{BASE_URL}/api/books")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test GET books with search
    print("\n2. Testing GET /api/books with search")
    response = requests.get(f"{BASE_URL}/api/books?search=1984&page=1&limit=5")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test POST new book
    print("\n3. Testing POST /api/books")
    new_book = {
        "isbn": "978-0-123456-78-9",
        "title": "Test Book for API",
        "subtitle": "A comprehensive guide",
        "category_id": 1,
        "total_copies": 3,
        "available_copies": 3,
        "price": 25.99,
        "publisher_id": 1,
        "authors": [
            {"author_id": 1, "role": "Primary Author"}
        ]
    }
    response = requests.post(f"{BASE_URL}/api/books", json=new_book)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        book_id = response.json()["data"]["book_id"]
        
        # Test GET specific book
        print(f"\n4. Testing GET /api/books/{book_id}")
        response = requests.get(f"{BASE_URL}/api/books/{book_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test PUT update book
        print(f"\n5. Testing PUT /api/books/{book_id}")
        update_data = {
            "title": "Updated Test Book",
            "price": 29.99
        }
        response = requests.put(f"{BASE_URL}/api/books/{book_id}", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test DELETE book
        print(f"\n6. Testing DELETE /api/books/{book_id}")
        response = requests.delete(f"{BASE_URL}/api/books/{book_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

def test_members_api():
    """Test Members CRUD operations"""
    print("\n\n=== Testing Members API ===")
    
    # Test GET all members
    print("\n1. Testing GET /api/members")
    response = requests.get(f"{BASE_URL}/api/members")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test POST new member
    print("\n2. Testing POST /api/members")
    start_date = date.today()
    end_date = start_date + timedelta(days=365)
    
    new_member = {
        "membership_number": "TEST2024001",
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "phone_number": "+1-555-0199",
        "membership_type": "Regular",
        "membership_start_date": start_date.isoformat(),
        "membership_expiry_date": end_date.isoformat(),
        "max_books_allowed": 5
    }
    response = requests.post(f"{BASE_URL}/api/members", json=new_member)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        member_id = response.json()["data"]["member_id"]
        
        # Test GET specific member
        print(f"\n3. Testing GET /api/members/{member_id}")
        response = requests.get(f"{BASE_URL}/api/members/{member_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test PUT update member
        print(f"\n4. Testing PUT /api/members/{member_id}")
        update_data = {
            "membership_type": "Premium",
            "max_books_allowed": 10
        }
        response = requests.put(f"{BASE_URL}/api/members/{member_id}", json=update_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

def test_utility_endpoints():
    """Test utility endpoints"""
    print("\n\n=== Testing Utility Endpoints ===")
    
    endpoints = [
        "/api/categories",
        "/api/authors", 
        "/api/publishers",
        "/api/stats",
        "/health"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting GET {endpoint}")
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(" ## Success")
        else:
            print(f" ** Failed: {response.text}")

def test_loan_system():
    """Test loan system functionality"""
    print("\n\n=== Testing Loan System ===")
    
    # Create a loan
    print("\n1. Testing POST /api/loans")
    due_date = date.today() + timedelta(days=14)
    loan_data = {
        "member_id": 1,  # Assuming member exists
        "book_id": 1,    # Assuming book exists
        "due_date": due_date.isoformat()
    }
    response = requests.post(f"{BASE_URL}/api/loans", json=loan_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Get loans
    print("\n2. Testing GET /api/loans")
    response = requests.get(f"{BASE_URL}/api/loans")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def run_all_tests():
    """Run all API tests"""
    print(" Starting API Tests...")
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Test health check first
        print("\n=== Health Check ===")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print(" ** API is not healthy. Please check if the server is running.")
            return
        print(" ## API is healthy")
        
        # Run tests
        test_books_api()
        test_members_api()
        test_utility_endpoints()
        test_loan_system()
        
        print("\n @@ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print(f" ** Could not connect to {BASE_URL}")
        print("Please ensure the FastAPI server is running on port 8000")
    except Exception as e:
        print(f" ** Test failed with error: {e}")

if __name__ == "__main__":
    run_all_tests()

# pytest_tests.py - Unit Tests using pytest

client = TestClient(app)

class TestBooksAPI:
    """Test suite for Books API"""
    
    def test_get_books(self):
        """Test GET /api/books"""
        response = client.get("/api/books")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert data["success"] is True
    
    def test_get_books_with_pagination(self):
        """Test GET /api/books with pagination"""
        response = client.get("/api/books?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 5
    
    def test_get_books_with_search(self):
        """Test GET /api/books with search"""
        response = client.get("/api/books?search=python")
        assert response.status_code == 200
    
    def test_get_nonexistent_book(self):
        """Test GET /api/books/{id} for non-existent book"""
        response = client.get("/api/books/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_create_book_invalid_data(self):
        """Test POST /api/books with invalid data"""
        invalid_book = {
            "title": "Test Book"
            # Missing required fields
        }
        response = client.post("/api/books", json=invalid_book)
        assert response.status_code == 422  # Validation error

class TestMembersAPI:
    """Test suite for Members API"""
    
    def test_get_members(self):
        """Test GET /api/members"""
        response = client.get("/api/members")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert data["success"] is True
    
    def test_get_members_with_filter(self):
        """Test GET /api/members with filters"""
        response = client.get("/api/members?membership_type=Regular&is_active=true")
        assert response.status_code == 200
    
    def test_get_nonexistent_member(self):
        """Test GET /api/members/{id} for non-existent member"""
        response = client.get("/api/members/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False

class TestUtilityEndpoints:
    """Test suite for utility endpoints"""
    
    def test_get_categories(self):
        """Test GET /api/categories"""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
    
    def test_get_authors(self):
        """Test GET /api/authors"""
        response = client.get("/api/authors")
        assert response.status_code == 200
    
    def test_get_publishers(self):
        """Test GET /api/publishers"""
        response = client.get("/api/publishers")
        assert response.status_code == 200
    
    def test_get_stats(self):
        """Test GET /api/stats"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_books" in data["data"]
        assert "total_members" in data["data"]
    
    def test_health_check(self):
        """Test GET /health"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data

class TestErrorHandling:
    """Test suite for error handling"""
    
    def test_404_endpoint(self):
        """Test non-existent endpoint"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self):
        """Test invalid JSON payload"""
        response = client.post(
            "/api/books", 
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422

# Run tests with: python -m pytest pytest_tests.py -v

# database_setup.py - Database Setup Script

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database_and_user():
    """Create database and user if they don't exist"""
    
    # Connect as root to create database and user
    root_connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user='root',
        password=input("Enter MySQL root password: ")
    )
    
    cursor = root_connection.cursor()
    
    try:
        # Create database
        db_name = os.getenv('DB_NAME', 'LibraryManagementSystem')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f" ## Database '{db_name}' created/verified")
        
        # Create user
        db_user = os.getenv('DB_USER', 'library_user')
        db_password = os.getenv('DB_PASSWORD', 'userpassword')
        
        cursor.execute(f"CREATE USER IF NOT EXISTS '{db_user}'@'localhost' IDENTIFIED BY '{db_password}'")
        cursor.execute(f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        print(f" ## User '{db_user}' created/verified with permissions")
        
    except mysql.connector.Error as e:
        print(f" ** Error: {e}")
    finally:
        cursor.close()
        root_connection.close()

def test_application_connection():
    """Test connection with application credentials"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'library_user'),
            password=os.getenv('DB_PASSWORD', 'userpassword'),
            database=os.getenv('DB_NAME', 'LibraryManagementSystem')
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        if result:
            print("## Application database connection successful")
        
        cursor.close()
        connection.close()
        
    except mysql.connector.Error as e:
        print(f" ** Application connection failed: {e}")

def main():
    """Main setup function"""
    print("Setting up Library Management Database...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print(" ** .env file not found. Please copy .env.example to .env and configure it.")
        return
    
    create_database_and_user()
    test_application_connection()
    
    print("\n Next steps:")
    print("1. Run the SQL schema from Question 1 to create tables")
    print("2. Start the FastAPI application: python main.py")
    print("3. Visit http://localhost:8000/docs for API documentation")

if __name__ == "__main__":
    main()

# benchmark.py - Performance Benchmarking Script

import asyncio
import aiohttp
import time
import statistics
from concurrent.futures import ThreadPoolExecutor

BASE_URL = "http://localhost:8000"

async def benchmark_endpoint(session, url, num_requests=100):
    """Benchmark a single endpoint"""
    response_times = []
    success_count = 0
    
    for i in range(num_requests):
        start_time = time.time()
        try:
            async with session.get(url) as response:
                await response.read()
                if response.status == 200:
                    success_count += 1
                response_times.append(time.time() - start_time)
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
    
    return {
        'total_requests': num_requests,
        'successful_requests': success_count,
        'success_rate': (success_count / num_requests) * 100,
        'avg_response_time': statistics.mean(response_times) * 1000,  # ms
        'min_response_time': min(response_times) * 1000,
        'max_response_time': max(response_times) * 1000,
        'median_response_time': statistics.median(response_times) * 1000
    }

async def run_benchmarks():
    """Run benchmarks on key endpoints"""
    endpoints = [
        "/api/books",
        "/api/members", 
        "/api/categories",
        "/api/stats",
        "/health"
    ]
    
    print("*## Starting Performance Benchmarks...")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            url = f"{BASE_URL}{endpoint}"
            print(f"\nBenchmarking: {endpoint}")
            
            # Test connection first
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        print(f" ** Endpoint not available (status: {response.status})")
                        continue
            except:
                print(" ** Could not connect to endpoint")
                continue
            
            # Run benchmark
            results = await benchmark_endpoint(session, url, 50)
            
            print(f"## Results for {endpoint}:")
            print(f"   Success Rate: {results['success_rate']:.1f}%")
            print(f"   Avg Response Time: {results['avg_response_time']:.2f}ms")
            print(f"   Min Response Time: {results['min_response_time']:.2f}ms")
            print(f"   Max Response Time: {results['max_response_time']:.2f}ms")
            print(f"   Median Response Time: {results['median_response_time']:.2f}ms")

if __name__ == "__main__":
    asyncio.run(run_benchmarks())