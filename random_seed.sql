-- =======================================================
-- Solar Installation and Maintenance Service Management System
-- Random Sample SQL Dataset: random_seed.sql
-- Use this file to populate additional realistic test records
-- =======================================================

USE solar_service_db;

-- 1. Insert Random Additional Customers
INSERT INTO Customer (Name, Phone, Email, Address) VALUES
('Karthik Subramanian', '9712345672', 'karthik.s@outlook.com', 'Flat 304, Green Palms, T. Nagar, Chennai'),
('Ananya Deshmukh', '9823456781', 'ananya.d@gmail.com', 'Villa 14, Palm Meadows, Banjara Hills, Hyderabad'),
('Rohit Verma', '9898765432', 'rohit.v@yahoo.com', 'House 55, 4th Block, Koramangala, Bengaluru'),
('Meera Kulkarni', '9654321098', 'meera.k@gmail.com', 'B-12, Sagar Society, Shivaji Nagar, Pune'),
('Sanjay Rao', '9745632189', 'sanjay.rao@gmail.com', 'Tower C-901, Sector 62, Noida'),
('Pooja Chawla', '9567890123', 'pooja.c@rediffmail.com', 'Block CD, Salt Lake Sector 1, Kolkata');

-- 2. Insert Random Solar Equipment Hardware
INSERT INTO Equipment (EquipName, Type, Price) VALUES
('Adani 550W Mono PERC Bifacial Solar Panel', 'Solar Panel', 21500.00),
('Growatt 6kVA Smart Hybrid Solar Inverter', 'Inverter', 52000.00),
('Luminous 150Ah Solar Tubular Battery', 'Energy Storage', 16500.00),
('Havells 4-String DC Combiner Box & SPD', 'Electrical Safety', 5800.00);

-- 3. Insert Random Installation Projects linked to Customers & Employees
-- Note: Adjust CustomerID and EmpID based on available IDs
INSERT INTO Installation (CustomerID, EmpID, InstallationDate, Capacity, Status, Cost) VALUES
(6, 1, '2026-04-10', '8 kW Hybrid System', 'In Progress', 395000.00),
(7, 2, '2026-04-15', '5 kW On-Grid Rooftop', 'Scheduled', 255000.00),
(8, 3, '2026-03-25', '12 kW Commercial Array', 'Completed', 580000.00),
(9, 1, '2026-04-02', '3.3 kW Home Solar', 'Completed', 175000.00);

-- 4. Insert Random Maintenance Service Visits
INSERT INTO Maintenance (InstallID, VisitDate, WorkDescription, Cost) VALUES
(6, '2026-04-20', 'Pre-commissioning array earthing continuity test and MC4 crimp inspection', 2200.00),
(8, '2026-04-18', 'Comprehensive panel dusting, thermal hotspot analysis, and junction cleaning', 3800.00);

-- 5. Insert Random Payment Receipts
INSERT INTO Payment (CustomerID, Amount, PaymentDate, Mode) VALUES
(6, 200000.00, '2026-04-08', 'Bank Transfer'),
(6, 195000.00, '2026-04-12', 'UPI'),
(7, 100000.00, '2026-04-14', 'Card'),
(8, 300000.00, '2026-03-22', 'Bank Transfer'),
(9, 175000.00, '2026-04-01', 'UPI');

-- 6. Insert Random Customer Feedback Reviews
INSERT INTO Feedback (InstallID, Rating, Comments) VALUES
(8, 5, 'Exceptional 12 kW setup for our office. Electricity bills dropped by 82% from month one!'),
(9, 4, 'Very clean rooftop installation. Net metering took 10 days, system runs reliably.');
