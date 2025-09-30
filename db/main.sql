-- =====================================================
-- Library Management System - Database Schema
-- Compatible with MySQL 8+
-- =====================================================

DROP DATABASE IF EXISTS LibraryManagementSystem;
CREATE DATABASE LibraryManagementSystem;
USE LibraryManagementSystem;

-- =====================================================
-- Authors
-- =====================================================
CREATE TABLE authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    nationality VARCHAR(50),
    biography TEXT,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_author_name (last_name, first_name)
);

-- =====================================================
-- Publishers
-- =====================================================
CREATE TABLE publishers (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    publisher_name VARCHAR(100) NOT NULL UNIQUE,
    address VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Categories
-- =====================================================
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Books
-- =====================================================
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(17) NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    subtitle VARCHAR(200),
    publication_date DATE,
    edition INT DEFAULT 1,
    pages INT,
    language VARCHAR(30) DEFAULT 'English',
    book_condition ENUM('New','Good','Fair','Poor','Damaged') DEFAULT 'New',
    location_shelf VARCHAR(20),
    total_copies INT NOT NULL,
    available_copies INT,
    price DECIMAL(10,2),
    publisher_id INT,
    category_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_books_publisher FOREIGN KEY (publisher_id) REFERENCES publishers(publisher_id) ON DELETE SET NULL,
    CONSTRAINT fk_books_category FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE CASCADE
);

-- =====================================================
-- Book-Author (many-to-many)
-- =====================================================
CREATE TABLE book_authors (
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    author_role VARCHAR(50) DEFAULT 'Primary Author',
    PRIMARY KEY (book_id, author_id),
    CONSTRAINT fk_ba_book FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    CONSTRAINT fk_ba_author FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE CASCADE
);

-- =====================================================
-- Members
-- =====================================================
CREATE TABLE members (
    member_id INT AUTO_INCREMENT PRIMARY KEY,
    membership_number VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE,
    gender ENUM('Male','Female','Other'),
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(50),
    postal_code VARCHAR(10),
    membership_type ENUM('Regular','Student','Senior','Premium') DEFAULT 'Regular',
    membership_start_date DATE NOT NULL,
    membership_expiry_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    max_books_allowed INT DEFAULT 5,
    CONSTRAINT chk_max_books CHECK (max_books_allowed > 0),
    INDEX idx_member_name (last_name, first_name)
);

-- =====================================================
-- Staff
-- =====================================================
CREATE TABLE staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    CONSTRAINT chk_salary CHECK (salary > 0),
    INDEX idx_staff_name (last_name, first_name)
);

-- =====================================================
-- Loan Transactions
-- =====================================================
CREATE TABLE loan_transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    book_id INT NOT NULL,
    staff_id INT,
    loan_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    loan_status ENUM('Active','Returned','Overdue','Lost','Damaged') DEFAULT 'Active',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_lt_member FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    CONSTRAINT fk_lt_book FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    CONSTRAINT fk_lt_staff FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE SET NULL
);

-- =====================================================
-- Fines
-- =====================================================
CREATE TABLE fines (
    fine_id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    transaction_id INT,
    amount DECIMAL(10,2) NOT NULL,
    paid_amount DECIMAL(10,2) DEFAULT 0,
    payment_status ENUM('Unpaid','Paid','Partial') DEFAULT 'Unpaid',
    issued_date DATE NOT NULL,
    paid_date DATE,
    CONSTRAINT chk_fine_amount CHECK (amount >= 0),
    CONSTRAINT chk_paid_amount CHECK (paid_amount >= 0),
    CONSTRAINT fk_fine_member FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,
    CONSTRAINT fk_fine_transaction FOREIGN KEY (transaction_id) REFERENCES loan_transactions(transaction_id) ON DELETE CASCADE
);
