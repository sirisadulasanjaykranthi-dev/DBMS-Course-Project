-- =======================================================
-- Solar Installation and Maintenance Service Management System
-- Database Schema: solar_service_db
-- =======================================================

-- Create Database if not exists
CREATE DATABASE IF NOT EXISTS solar_service_db;
USE solar_service_db;

-- Disable foreign key checks for clean recreation
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS Feedback;
DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Maintenance;
DROP TABLE IF EXISTS Installation;
DROP TABLE IF EXISTS Equipment;
DROP TABLE IF EXISTS Employee;
DROP TABLE IF EXISTS Customer;

SET FOREIGN_KEY_CHECKS = 1;

-- -------------------------------------------------------
-- 1. Customer Table
-- Stores details of residential, commercial, or industrial customers
-- -------------------------------------------------------
CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Phone VARCHAR(20) NOT NULL,
    Email VARCHAR(100) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- 2. Employee Table
-- Stores staff members including solar technicians and engineers
-- -------------------------------------------------------
CREATE TABLE Employee (
    EmpID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Role VARCHAR(50) NOT NULL,
    Phone VARCHAR(20) NOT NULL,
    Salary DECIMAL(10,2) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- 3. Equipment Table
-- Solar hardware components (Panels, Inverters, Batteries, etc.)
-- -------------------------------------------------------
CREATE TABLE Equipment (
    EquipID INT PRIMARY KEY AUTO_INCREMENT,
    EquipName VARCHAR(100) NOT NULL,
    Type VARCHAR(50) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- 4. Installation Table
-- Tracks rooftop/ground-mount solar project setups
-- Referential integrity: ON DELETE CASCADE for Customer, RESTRICT for Employee
-- -------------------------------------------------------
CREATE TABLE Installation (
    InstallID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    EmpID INT NOT NULL,
    InstallationDate DATE NOT NULL,
    Capacity VARCHAR(50) NOT NULL,
    Status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    Cost DECIMAL(10,2) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_installation_customer FOREIGN KEY (CustomerID) 
        REFERENCES Customer(CustomerID) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    CONSTRAINT fk_installation_employee FOREIGN KEY (EmpID) 
        REFERENCES Employee(EmpID) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- 5. Maintenance Table
-- Tracks scheduled or ad-hoc maintenance visits and repairs
-- -------------------------------------------------------
CREATE TABLE Maintenance (
    MaintID INT PRIMARY KEY AUTO_INCREMENT,
    InstallID INT NOT NULL,
    VisitDate DATE NOT NULL,
    WorkDescription VARCHAR(255) NOT NULL,
    Cost DECIMAL(10,2) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_maintenance_installation FOREIGN KEY (InstallID) 
        REFERENCES Installation(InstallID) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- 6. Payment Table
-- Records payments received from customers
-- -------------------------------------------------------
CREATE TABLE Payment (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    PaymentDate DATE NOT NULL,
    Mode VARCHAR(30) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_customer FOREIGN KEY (CustomerID) 
        REFERENCES Customer(CustomerID) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;

-- -------------------------------------------------------
-- 7. Feedback Table
-- Records client feedback and ratings for completed installations
-- -------------------------------------------------------
CREATE TABLE Feedback (
    FeedbackID INT PRIMARY KEY AUTO_INCREMENT,
    InstallID INT NOT NULL,
    Rating INT NOT NULL CHECK (Rating BETWEEN 1 AND 5),
    Comments VARCHAR(255),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_installation FOREIGN KEY (InstallID) 
        REFERENCES Installation(InstallID) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
) ENGINE=InnoDB;
