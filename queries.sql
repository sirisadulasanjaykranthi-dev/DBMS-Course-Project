-- =======================================================
-- Solar Installation and Maintenance Service Management System
-- Demonstrative SQL Queries Reference: queries.sql
-- Used for College Presentation-III & Viva Voce
-- =======================================================

USE solar_service_db;

-- =======================================================
-- 1. BASIC CRUD OPERATIONS
-- =======================================================

-- 1.1 SELECT: View all customers ordered by ID
SELECT CustomerID, Name, Phone, Email, Address, CreatedAt
FROM Customer
ORDER BY CustomerID DESC;

-- 1.2 INSERT: Register a new customer
INSERT INTO Customer (Name, Phone, Email, Address)
VALUES ('Rahul Sharma', '9876543210', 'rahul@gmail.com', 'Hyderabad');

-- 1.3 UPDATE: Modify customer contact details
UPDATE Customer
SET Phone = '9876543211', Address = 'Plot 104, Jubilee Hills, Hyderabad'
WHERE CustomerID = 6;

-- 1.4 DELETE: Remove a customer record (Cascades to related installations & payments)
DELETE FROM Customer
WHERE CustomerID = 6;


-- =======================================================
-- 2. RELATIONAL JOIN QUERIES (Multi-table Associations)
-- =======================================================

-- 2.1 INNER JOIN: Installations with Customer Name and Technician Name
SELECT 
    i.InstallID,
    c.Name AS CustomerName,
    c.Phone AS CustomerPhone,
    e.Name AS AssignedTechnician,
    e.Role AS TechnicianRole,
    i.InstallationDate,
    i.Capacity,
    i.Status,
    i.Cost
FROM Installation i
INNER JOIN Customer c ON i.CustomerID = c.CustomerID
INNER JOIN Employee e ON i.EmpID = e.EmpID
ORDER BY i.InstallationDate DESC;

-- 2.2 INNER JOIN: Pending Installations filter
SELECT 
    i.InstallID, 
    c.Name AS CustomerName, 
    c.Phone,
    i.Capacity,
    i.InstallationDate,
    i.Cost
FROM Installation i
JOIN Customer c ON i.CustomerID = c.CustomerID
WHERE i.Status = 'Pending';

-- 2.3 MULTI-TABLE JOIN: Maintenance details with Installation & Customer
SELECT 
    m.MaintID,
    m.VisitDate,
    c.Name AS CustomerName,
    i.Capacity,
    m.WorkDescription,
    m.Cost
FROM Maintenance m
JOIN Installation i ON m.InstallID = i.InstallID
JOIN Customer c ON i.CustomerID = c.CustomerID
ORDER BY m.VisitDate DESC;

-- 2.4 Customer Payment History with Customer Info
SELECT 
    p.PaymentID,
    c.Name AS CustomerName,
    p.Amount,
    p.PaymentDate,
    p.Mode
FROM Payment p
JOIN Customer c ON p.CustomerID = c.CustomerID
ORDER BY p.PaymentDate DESC;

-- 2.5 Feedback with Project Details
SELECT 
    f.FeedbackID,
    i.InstallID,
    c.Name AS CustomerName,
    f.Rating,
    f.Comments,
    f.CreatedAt
FROM Feedback f
JOIN Installation i ON f.InstallID = i.InstallID
JOIN Customer c ON i.CustomerID = c.CustomerID
ORDER BY f.Rating DESC;


-- =======================================================
-- 3. AGGREGATE, GROUP BY & ORDER BY QUERIES
-- =======================================================

-- 3.1 Total Maintenance Cost Grouped by Installation
SELECT 
    InstallID, 
    COUNT(MaintID) AS TotalVisits,
    SUM(Cost) AS TotalMaintenanceCost
FROM Maintenance
GROUP BY InstallID
ORDER BY TotalMaintenanceCost DESC;

-- 3.2 Technician Workload (Total Installations Handled per Employee)
SELECT 
    e.EmpID,
    e.Name AS EmployeeName, 
    e.Role,
    COUNT(i.InstallID) AS AssignedProjects
FROM Employee e
LEFT JOIN Installation i ON e.EmpID = i.EmpID
GROUP BY e.EmpID, e.Name, e.Role
ORDER BY AssignedProjects DESC;

-- 3.3 Revenue & Collections Summary by Payment Mode
SELECT 
    Mode, 
    COUNT(PaymentID) AS TransactionCount,
    SUM(Amount) AS TotalCollected
FROM Payment
GROUP BY Mode
ORDER BY TotalCollected DESC;

-- 3.4 Installation Project Status Breakdown
SELECT 
    Status, 
    COUNT(InstallID) AS ProjectCount,
    SUM(Cost) AS ProjectedValue
FROM Installation
GROUP BY Status;

-- 3.5 Average Customer Satisfaction Rating
SELECT 
    ROUND(AVG(Rating), 2) AS AverageRating,
    COUNT(FeedbackID) AS TotalReviews
FROM Feedback;


-- =======================================================
-- 4. DASHBOARD KPI METRICS (COUNT & SUM)
-- =======================================================
SELECT COUNT(*) AS TotalCustomers FROM Customer;
SELECT COUNT(*) AS TotalEmployees FROM Employee;
SELECT COUNT(*) AS TotalInstallations FROM Installation;
SELECT COUNT(*) AS TotalEquipment FROM Equipment;
SELECT COUNT(*) AS TotalMaintenance FROM Maintenance;
SELECT COUNT(*) AS TotalPayments FROM Payment;
SELECT IFNULL(SUM(Cost), 0) AS TotalInstallationRevenue FROM Installation;
SELECT IFNULL(SUM(Amount), 0) AS TotalPaymentsCollected FROM Payment;
