CREATE DATABASE IF NOT EXISTS mediscan;
USE mediscan;

CREATE TABLE IF NOT EXISTS analyses (
    id VARCHAR(100) PRIMARY KEY,
    filename VARCHAR(255),
    file_url TEXT,
    status VARCHAR(50),
    diagnosis TEXT,
    confidence FLOAT,
    detail TEXT,
    created_at DATETIME
);