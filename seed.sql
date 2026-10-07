-- =======================================================
-- Solar Installation and Maintenance Service Management System
-- Initial Seed Data: seed.sql
-- =======================================================

USE solar_service_db;

-- 1. Seed Customers
INSERT INTO Customer (Name, Phone, Email, Address) VALUES
('Rajesh Patel', '9876543210', 'rajesh.patel@gmail.com', 'Flat 402, Green Meadows, Ahmedabad'),
('Priya Sharma', '9812345678', 'priya.sharma@yahoo.com', 'House 12, Sector 15, Gurugram'),
('Vikram Singh', '9723456789', 'vikram.singh@outlook.com', 'Plot 88, Banjara Hills, Hyderabad'),
('Sunita Verma', '9654321876', 'sunita.verma@gmail.com', '21B, Anna Nagar, Chennai'),
('Amit Deshmukh', '9543210987', 'amit.d@rediffmail.com', '45 Shivaji Park, Pune');

-- 2. Seed Employees
INSERT INTO Employee (Name, Role, Phone, Salary) VALUES
('Ramesh Kumar', 'Lead Solar Engineer', '9898012345', 55000.00),
('Ananya Sen', 'Installation Specialist', '9898023456', 42000.00),
('Kiran Rao', 'Field Maintenance Technician', '9898034567', 35000.00),
('Deepak Verma', 'Electrical Safety Inspector', '9898045678', 48000.00),
('Neha Gupta', 'Customer Support Coordinator', '9898056789', 32000.00);

-- 3. Seed Equipment
INSERT INTO Equipment (EquipName, Type, Price) VALUES
('Loom Solar 540W Mono PERC Panel', 'Solar Panel', 18500.00),
('Microtek 5kVA Hybrid Solar Inverter', 'Inverter', 45000.00),
('Exide 48V 100Ah LiFePO4 Battery', 'Energy Storage', 72000.00),
('Aluminium Rooftop Mounting Rail Kit', 'Mounting Hardware', 8500.00),
('Bi-directional Net Meter 3-Phase', 'Metering Device', 6200.00),
('Surge Protection Device & MCB Box', 'Electrical Safety', 4200.00);

-- 4. Seed Installations
INSERT INTO Installation (CustomerID, EmpID, InstallationDate, Capacity, Status, Cost) VALUES
(1, 1, '2026-01-15', '5 kW On-Grid', 'Completed', 245000.00),
(2, 2, '2026-02-10', '3 kW Hybrid', 'Completed', 180000.00),
(3, 1, '2026-03-01', '10 kW Commercial', 'In Progress', 490000.00),
(4, 2, '2026-03-20', '3 kW Rooftop', 'Pending', 165000.00),
(5, 3, '2026-04-05', '7 kW Off-Grid', 'Scheduled', 360000.00);

-- 5. Seed Maintenance Visits
INSERT INTO Maintenance (InstallID, VisitDate, WorkDescription, Cost) VALUES
(1, '2026-03-15', 'Routine quarterly panel wash, wiring inspection, and voltage check', 2500.00),
(1, '2026-06-20', 'Inverter firmware update and MC4 connector tightening', 1800.00),
(2, '2026-04-12', 'Battery state-of-health test and thermal hotspot scanning', 3200.00),
(3, '2026-05-18', 'Pre-commissioning array safety check and earth resistance test', 4500.00);

-- 6. Seed Payments
INSERT INTO Payment (CustomerID, Amount, PaymentDate, Mode) VALUES
(1, 100000.00, '2026-01-10', 'Bank Transfer'),
(1, 145000.00, '2026-01-20', 'UPI'),
(2, 90000.00, '2026-02-05', 'UPI'),
(2, 90000.00, '2026-02-15', 'Card'),
(3, 200000.00, '2026-02-28', 'Bank Transfer'),
(4, 50000.00, '2026-03-18', 'Cash');

-- 7. Seed Feedback
INSERT INTO Feedback (InstallID, Rating, Comments) VALUES
(1, 5, 'Exceptional service! Power bill dropped by 85%. Ramesh Kumar was very knowledgeable.'),
(2, 4, 'Very smooth installation. System working seamlessly during peak summer.'),
(3, 5, 'Commercial rooftop setup is on schedule. Highly professional team.');
