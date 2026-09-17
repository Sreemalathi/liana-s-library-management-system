DROP SCHEMA IF EXISTS mylibrary;
CREATE SCHEMA mylibrary;
USE mylibrary;

CREATE TABLE books(
    isbn VARCHAR(15) PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    author VARCHAR(100),
    genre VARCHAR(50),
    book_language VARCHAR(50),
    is_available BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE users(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15),
    email VARCHAR(100) NOT NULL UNIQUE,
    max_loans INT NOT NULL DEFAULT 5
);

CREATE TABLE loans(
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(15) NOT NULL,
    user_id INT NOT NULL,
    loan_date DATE DEFAULT (CURRENT_DATE()) NOT NULL,
    due_date DATE NOT NULL,
    extended_due_date DATE,
    extension_count TINYINT NOT NULL DEFAULT 0,
    return_date DATE,
    FOREIGN KEY (isbn) REFERENCES books(isbn),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE reservations(
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(15) NOT NULL,
    user_id INT NOT NULL,
    reservation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ready_date DATETIME NULL,
    status ENUM('WAIT','READY','FULFILLED','CANCELLED','EXPIRED')
    NOT NULL DEFAULT 'WAIT',
    FOREIGN KEY (isbn) REFERENCES books(isbn),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM books;
SELECT COUNT(*) FROM loans;
SELECT COUNT(*) FROM reservations;