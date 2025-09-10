DROP DATABASE IF EXISTS school_face_attendance;

CREATE DATABASE school_face_attendance;

USE school_face_attendance;

-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'staff') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students Table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    section VARCHAR(20),
    course VARCHAR(100),
    photo_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Faces Table
CREATE TABLE faces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    encoding LONGBLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Attendance Table
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('present', 'late', 'absent') DEFAULT 'present',
    FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
);

-- Logs Table
CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Seed sample students only (users will be seeded by Python seeder with hashed passwords)
INSERT INTO
    students (
        student_id,
        first_name,
        last_name,
        section,
        photo_path
    )
VALUES (
        '20240143',
        'Yuan',
        'Vasig',
        'BSCPE 2-B',
        'app/data/images/students/Vasig/vasig1.jpg'
    ),
    (
        '20240091',
        'Chiro',
        'Uy',
        'BSCPE 2-B',
        'app/data/images/students/Uy/uy1.jpg'
    ),
    (
        '20240086',
        'Justin',
        'Monoy',
        'BSCPE 2-B',
        'app/data/images/students/Monoy/monoy1.jpg'
    ),
    (
        '20240169',
        'Den',
        'Beguia',
        'BSCPE 2-B',
        'app/data/images/students/Beguia/beguia1.jpg'
    );