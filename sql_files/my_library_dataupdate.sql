USE mylibrary;

-- ============================================================
-- INITIAL SEED DATA
-- ============================================================

-- USERS (8)
INSERT INTO users (user_name, phone_number, email) VALUES
('Anna Schmidt', '01511234567', 'anna.schmidt@email.com'),
('Liam Müller', '01522345678', 'liam.mueller@email.com'),
('Sofia Wagner', '01533456789', 'sofia.wagner@email.com'),
('Noah Becker', '01544567890', 'noah.becker@email.com'),
('Mia Hoffmann', '01555678901', 'mia.hoffmann@email.com'),
('Ben Schulz', '01566789012', 'ben.schulz@email.com'),
('Emma Koch', '01577890123', 'emma.koch@email.com'),
('Leon Richter', '01588901234', 'leon.richter@email.com');

-- BOOKS (10)
INSERT INTO books (isbn, title, author, genre, book_language, is_available) VALUES
('9783161484100', 'The Silent Ocean', 'Clara Vance', 'Fiction', 'English', TRUE),
('9781234567897', 'Data Driven', 'James Ortiz', 'Non-Fiction', 'English', TRUE),
('9780142437221', 'Der Lange Weg', 'Hannah Frei', 'Drama', 'German', TRUE),
('9783596900001', 'Sterne über Berlin', 'Felix Adler', 'Fiction', 'German', TRUE),
('9781566199094', 'Python for Everyone', 'Priya Nair', 'Technology', 'English', FALSE),
('9780062316097', 'The Last Algorithm', 'Marcus Lee', 'Sci-Fi', 'English', FALSE),
('9782070368228', 'Le Petit Mystère', 'Élodie Blanc', 'Mystery', 'French', TRUE),
('9783832195400', 'Reise ins Unbekannte', 'Nora Vogel', 'Adventure', 'German', TRUE),
('9780593132945', 'Whispers of Time', 'Ethan Park', 'Fantasy', 'English', FALSE),
('9781984821270', 'The Analyst', 'Rachel Kim', 'Thriller', 'English', FALSE);

-- LOANS (4) — matches the 4 books above marked is_available = FALSE
INSERT INTO loans (isbn, user_id, loan_date, due_date, extended_due_date, extension_count, return_date) VALUES
('9781566199094', 1, '2026-08-20', '2026-09-03', NULL, 0, NULL),
('9780062316097', 3, '2026-08-25', '2026-09-08', NULL, 0, NULL),
('9780593132945', 5, '2026-09-01', '2026-09-15', '2026-09-22', 1, NULL),
('9781984821270', 7, '2026-07-10', '2026-07-24', NULL, 0, '2026-07-20');

-- RESERVATIONS (2)
INSERT INTO reservations (isbn, user_id, status) VALUES
('9781566199094', 2, 'ACTIVE'),
('9780062316097', 4, 'ACTIVE');

-- ============================================================
-- ADDITIONAL USERS & BOOKS
-- ============================================================

-- ADDITIONAL USERS (6)
INSERT INTO users (user_name, phone_number, email) VALUES
('Paul Weber', '01599012345', 'paul.weber@email.com'),
('Lena Fischer', '01600123456', 'lena.fischer@email.com'),
('Jonas Krüger', '01611234567', 'jonas.krueger@email.com'),
('Hannah Zimmermann', '01622345678', 'hannah.zimmermann@email.com'),
('Felix Braun', '01633456789', 'felix.braun@email.com'),
('Clara Neumann', '01644567890', 'clara.neumann@email.com');

-- ADDITIONAL BOOKS (10)
INSERT INTO books (isbn, title, author, genre, book_language, is_available) VALUES
('9780345539756', 'The Glass Garden', 'Sophie Lindqvist', 'Fantasy', 'English', TRUE),
('9783423347623', 'Der Stille Fluss', 'Karin Hoffmann', 'Drama', 'German', TRUE),
('9788401352836', 'El Último Verano', 'Marta Ruiz', 'Fiction', 'Spanish', TRUE),
('9788817067428', 'Il Giardino Segreto', 'Luca Bianchi', 'Mystery', 'Italian', FALSE),
('9782253067421', 'Les Ombres de Paris', 'Camille Laurent', 'Thriller', 'French', TRUE),
('9780062457042', 'Machine Minds', 'Devon Carter', 'Sci-Fi', 'English', FALSE),
('9781492670010', 'SQL for Beginners', 'Priya Nair', 'Technology', 'English', TRUE),
('9783442267012', 'Die Reise nach Norden', 'Jonas Weiss', 'Adventure', 'German', TRUE),
('9780316769488', 'Whispering Pines', 'Grace Bennett', 'Fiction', 'English', FALSE),
('9780241003008', 'The Data Detective', 'Marcus Lee', 'Non-Fiction', 'English', TRUE);

-- ============================================================
-- POPULAR ENGLISH NOVELS
-- ============================================================

-- 5 popular English-language novels
-- ISBNs checked against existing seed data for uniqueness
INSERT INTO books (isbn, title, author, genre, book_language, is_available) VALUES
('9780345339683', 'The Hobbit', 'J.R.R. Tolkien', 'Fiction', 'English', TRUE),
('9780743273565', 'The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', 'English', TRUE),
('9780061120084', 'To Kill a Mockingbird', 'Harper Lee', 'Fiction', 'English', TRUE),
('9780307474278', 'The Da Vinci Code', 'Dan Brown', 'Fiction', 'English', TRUE),
('9780307588371', 'Gone Girl', 'Gillian Flynn', 'Fiction', 'English', TRUE);

-- ============================================================
-- LOAN HISTORY FOR DASHBOARD "MOST POPULAR BOOKS"
-- ============================================================

-- Seed loan history so the Dashboard's "Most Popular Books" shows realistic data:
--   The Hobbit        -> 5 borrowers
--   Gone Girl         -> 3 borrowers
--   The Great Gatsby  -> 2 borrowers
-- All loans are already returned, so book availability is untouched.
-- user_id is looked up by name via subquery so this works regardless of your actual auto-increment values.
INSERT INTO loans (isbn, user_id, loan_date, due_date, return_date) VALUES
-- The Hobbit (5 borrowers)
('9780345339683', (SELECT user_id FROM users WHERE user_name = 'Anna Schmidt'),  '2026-06-01', '2026-06-15', '2026-06-14'),
('9780345339683', (SELECT user_id FROM users WHERE user_name = 'Liam Müller'),   '2026-06-20', '2026-07-04', '2026-07-02'),
('9780345339683', (SELECT user_id FROM users WHERE user_name = 'Sofia Wagner'),  '2026-07-10', '2026-07-24', '2026-07-22'),
('9780345339683', (SELECT user_id FROM users WHERE user_name = 'Noah Becker'),   '2026-08-01', '2026-08-15', '2026-08-13'),
('9780345339683', (SELECT user_id FROM users WHERE user_name = 'Mia Hoffmann'),  '2026-08-25', '2026-09-08', '2026-09-07'),

-- Gone Girl (3 borrowers)
('9780307588371', (SELECT user_id FROM users WHERE user_name = 'Ben Schulz'),    '2026-06-05', '2026-06-19', '2026-06-18'),
('9780307588371', (SELECT user_id FROM users WHERE user_name = 'Emma Koch'),     '2026-07-01', '2026-07-15', '2026-07-13'),
('9780307588371', (SELECT user_id FROM users WHERE user_name = 'Leon Richter'),  '2026-08-10', '2026-08-24', '2026-08-22'),

-- The Great Gatsby (2 borrowers)
('9780743273565', (SELECT user_id FROM users WHERE user_name = 'Paul Weber'),    '2026-06-15', '2026-06-29', '2026-06-27'),
('9780743273565', (SELECT user_id FROM users WHERE user_name = 'Lena Fischer'),  '2026-07-20', '2026-08-03', '2026-08-01');
