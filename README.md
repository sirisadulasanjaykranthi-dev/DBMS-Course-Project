# Solar Installation & Maintenance Service Management System (SolarOps DBMS)
**College Presentation-III & Viva Voce Database Project**

A complete, production-grade Relational Database Management System (RDBMS) web application built using **Python Flask** and **MySQL Server 8.0**, connected natively via **`mysql-connector-python`**.

---

## 1. Project Introduction
In the renewable solar energy industry, companies routinely handle rooftop solar consultations, equipment inventories, installation work orders, scheduled maintenance visits, customer payments, and client reviews. 

Managing this information across spreadsheets or disconnected flat files causes:
* **Data Redundancy & Anomaly:** Inconsistent customer records and phone numbers.
* **Orphaned Records:** Work orders referencing deleted employees or customers.
* **Untracked Revenue:** Discrepancies between installation cost and actual customer receipts.
* **Missed Maintenance:** Inability to track system health and periodic cleaning schedules.

**SolarOps DBMS** solves these challenges through a centralized, normalized MySQL relational database connected to an intuitive web dashboard supporting full **CRUD operations** (Create, Read, Update, Delete), multi-table **JOINs**, and **referential integrity enforcement**.

---

## 2. Key Features
* **Real MySQL Integration:** Direct connection to MySQL Server 8.0 without mock or SQLite data. Every action executes actual SQL queries.
* **Relational Schema (7 Tables):** Models Customers, Staff, Equipment, Installations, Maintenance Visits, Payments, and Feedback.
* **Full CRUD Operations:** Supports inserting, viewing, editing, and deleting records in every entity.
* **Foreign Key Constraints & Cascade Rules:** Clean cascade on installation child records and restrict rules on technicians.
* **Live KPI Dashboard:** Metrics calculated using SQL aggregate queries (`SELECT COUNT(*)`, `SELECT SUM(*)`, `IFNULL`).
* **Multi-Table SQL JOINs:** Displays joined views linking Customers, Technicians, Projects, and Service visits.
* **Interactive Presentation SQL Lab (`/reports`):** A dedicated presentation view displaying SQL queries alongside live database tables for professors.
* **Web Setup & Diagnostics (`/db-setup`):** Diagnostic tool to test connection parameters and seed records in 1 click.

---

## 3. Technology Stack
* **Backend:** Python 3.12 + Flask
* **Database:** MySQL Server 8.0 (InnoDB Engine)
* **Database Connector:** `mysql-connector-python`
* **Configuration:** `python-dotenv` (.env environment management)
* **Frontend:** HTML5, CSS3, JavaScript (ES6)
* **UI Framework:** Bootstrap 5.3 & Bootstrap Icons
* **Database Management Tool:** MySQL Workbench 8.0

---

## 4. Database Design (Schema Architecture)

The database name is **`solar_service_db`**. It comprises 7 interconnected tables with primary keys, foreign keys, and indexes:

```
[ Customer ] (1) <──── (M) [ Installation ] (1) <──── (M) [ Maintenance ]
     │                              │
     │                              └─────────── (1) <──── (M) [ Feedback ]
     │ (1)                          ▲
     │                              │ (M)
     ▼ (M)                          │
 [ Payment ]                   [ Employee ]
```

### Table Specifications:

1. **`Customer`** (Primary Customer Entity)
   * `CustomerID` INT PRIMARY KEY AUTO_INCREMENT
   * `Name` VARCHAR(100) NOT NULL
   * `Phone` VARCHAR(20) NOT NULL
   * `Email` VARCHAR(100) NOT NULL
   * `Address` VARCHAR(255) NOT NULL
   * `CreatedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

2. **`Employee`** (Engineers, Technicians, Inspectors)
   * `EmpID` INT PRIMARY KEY AUTO_INCREMENT
   * `Name` VARCHAR(100) NOT NULL
   * `Role` VARCHAR(50) NOT NULL
   * `Phone` VARCHAR(20) NOT NULL
   * `Salary` DECIMAL(10,2) NOT NULL
   * `CreatedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

3. **`Equipment`** (Inventory of Panels, Inverters, Batteries)
   * `EquipID` INT PRIMARY KEY AUTO_INCREMENT
   * `EquipName` VARCHAR(100) NOT NULL
   * `Type` VARCHAR(50) NOT NULL
   * `Price` DECIMAL(10,2) NOT NULL
   * `CreatedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

4. **`Installation`** (Solar Project Orders)
   * `InstallID` INT PRIMARY KEY AUTO_INCREMENT
   * `CustomerID` INT (FOREIGN KEY &rarr; Customer, ON DELETE CASCADE)
   * `EmpID` INT (FOREIGN KEY &rarr; Employee, ON DELETE RESTRICT)
   * `InstallationDate` DATE NOT NULL
   * `Capacity` VARCHAR(50) NOT NULL
   * `Status` VARCHAR(30) NOT NULL (Pending, Scheduled, In Progress, Completed)
   * `Cost` DECIMAL(10,2) NOT NULL
   * `CreatedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

5. **`Maintenance`** (Routine & Diagnostic Servicing)
   * `MaintID` INT PRIMARY KEY AUTO_INCREMENT
   * `InstallID` INT (FOREIGN KEY &rarr; Installation, ON DELETE CASCADE)
   * `VisitDate` DATE NOT NULL
   * `WorkDescription` VARCHAR(255) NOT NULL
   * `Cost` DECIMAL(10,2) NOT NULL
   * `CreatedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

6. **`Payment`** (Customer Billing Ledger)
   * `PaymentID` INT PRIMARY KEY AUTO_INCREMENT
   * `CustomerID` INT (FOREIGN KEY &rarr; Customer, ON DELETE CASCADE)
   * `Amount` DECIMAL(10,2) NOT NULL
   * `PaymentDate` DATE NOT NULL
   * `Mode` VARCHAR(30) NOT NULL (Cash, UPI, Card, Bank Transfer)
   * `CreatedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

7. **`Feedback`** (Client Satisfaction Ratings)
   * `FeedbackID` INT PRIMARY KEY AUTO_INCREMENT
   * `InstallID` INT (FOREIGN KEY &rarr; Installation, ON DELETE CASCADE)
   * `Rating` INT NOT NULL CHECK (Rating BETWEEN 1 AND 5)
   * `Comments` VARCHAR(255)
   * `CreatedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

---

## 5. Folder Structure
```
solar-service-dbms/
│
├── app.py                     # Main Flask web application controller & routes
├── database.py                # MySQL connection manager & parameterized queries
├── init_db.py                 # CLI script to initialize database & seed data
├── requirements.txt           # Python package dependencies
├── .env                       # Active MySQL credentials & configuration
├── .env.example               # Template environment configuration
├── schema.sql                 # Complete MySQL DDL table definitions
├── seed.sql                   # Realistic sample data for all 7 tables
├── queries.sql                # Reference SQL queries for Presentation-III & Viva
├── README.md                  # Comprehensive setup & viva documentation
│
├── templates/
│   ├── base.html              # Master layout with navbar, alerts, modals
│   ├── index.html             # Dashboard with live MySQL KPI counts & recent logs
│   ├── customers.html         # Customer listing with search and delete modal
│   ├── customer_form.html     # Add/Edit Customer form
│   ├── customer_view.html     # Customer profile with linked projects and payments
│   ├── employees.html         # Employee directory
│   ├── employee_form.html     # Add/Edit Employee form
│   ├── equipment.html         # Solar equipment inventory table
│   ├── equipment_form.html    # Add/Edit Equipment form
│   ├── installations.html     # Installation projects list (relational JOIN)
│   ├── installation_form.html # Add/Edit Installation form with dynamic dropdowns
│   ├── installation_view.html # Installation detail with maintenance & feedback
│   ├── maintenance.html       # Maintenance visits list (relational JOIN)
│   ├── maintenance_form.html  # Add/Edit Maintenance form
│   ├── payments.html          # Payments list with sum total
│   ├── payment_form.html      # Add/Edit Payment form
│   ├── feedback.html          # Feedback reviews list with star rating display
│   ├── feedback_form.html     # Add Feedback form
│   ├── reports.html           # Presentation SQL Lab (JOIN, GROUP BY, SUM, COUNT)
│   └── db_setup.html          # Web-based database status & initialization
│
└── static/
    ├── css/
    │   └── style.css          # Custom solar-themed styling & cards
    └── js/
        └── script.js          # Dynamic modal confirmation and table search
```

---

## 6. Installation & Setup Guide

### Step 1: Open Terminal / PowerShell in Project Folder
Navigate to the project directory:
```powershell
cd "c:\solar installation and maintainence service management system"
```

### Step 2: Activate Virtual Environment
A virtual environment `venv` is already set up. Activate it:
```powershell
.\venv\Scripts\Activate.ps1
```
*(If on Command Prompt `cmd.exe`: `venv\Scripts\activate.bat`)*

### Step 3: Install Dependencies (If not already installed)
```powershell
pip install -r requirements.txt
```

---

## 7. Configuring MySQL Password

1. Open the `.env` file in the project folder with any text editor (Notepad, VS Code):
```ini
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_mysql_password
MYSQL_DATABASE=solar_service_db
```
2. Replace `your_actual_mysql_password` with your real MySQL `root` password set during your MySQL Server installation.
3. Save the file.

---

## 8. Initializing the Database

You can initialize the database using either the **Terminal CLI script** or **MySQL Workbench**:

### Option A: Using the CLI Script (Recommended & Fastest)
Run:
```powershell
python init_db.py
```
This script will:
* Verify connection to MySQL Server on `localhost:3306`.
* Create `solar_service_db` database.
* Execute `schema.sql` (creating all 7 tables with constraints).
* Execute `seed.sql` (populating realistic records).
* Output record counts for all 7 tables.

### Option B: Using MySQL Workbench
1. Open **MySQL Workbench**.
2. Connect to your `Local instance MySQL80`.
3. Open `schema.sql` (**File &rarr; Open SQL Script**) and click the **Lightning Bolt (Execute)** icon.
4. Open `seed.sql` and click **Execute**.
5. Refresh the **SCHEMAS** panel on the left; you will see `solar_service_db` with all 7 tables populated.

---

## 9. Running the Web Application

Start the Flask server:
```powershell
python app.py
```

You will see:
```
Starting Solar Service DBMS on http://127.0.0.1:5000 ...
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 10. Step-by-Step Live Demonstration for Examiners

### DEMO 1 — VIEW RECORDS
1. **In MySQL Workbench:** Run:
   ```sql
   USE solar_service_db;
   SELECT * FROM Customer;
   ```
   Note the 5 existing customer rows.
2. **In the Web App:** Click **Customers** in the navigation bar.
3. Show the examiner that the web UI displays the exact same 5 records directly queried from MySQL via `SELECT * FROM Customer ORDER BY CustomerID DESC`.

---

### DEMO 2 — INSERT RECORD
1. **In the Web App:**
   * Go to **Customers** &rarr; click **Add Customer**.
   * Fill in the test data:
     * **Name:** `Rahul Sharma`
     * **Phone:** `9876543210`
     * **Email:** `rahul@gmail.com`
     * **Address:** `Hyderabad`
   * Click **Add Customer (INSERT)**.
   * A green alert appears: *"Customer 'Rahul Sharma' registered successfully in MySQL!"*
   * The new record immediately appears at the top of the table.
2. **In MySQL Workbench:** Run:
   ```sql
   SELECT * FROM Customer WHERE Name = 'Rahul Sharma';
   ```
   Show the examiner that the record is now physically present in MySQL with an auto-generated `CustomerID`.

---

### DEMO 3 — DELETE RECORD
1. **In the Web App:**
   * Find the newly inserted `Rahul Sharma` record in the Customers table.
   * Click the red **Trash/Delete** icon on that row.
   * A confirmation modal appears asking: *"Are you sure you want to permanently delete this record from MySQL?"*
   * Click **Delete Record**.
   * A green alert confirms: *"Customer 'Rahul Sharma' deleted successfully from MySQL."*
2. **In MySQL Workbench:** Run:
   ```sql
   SELECT * FROM Customer WHERE Name = 'Rahul Sharma';
   ```
   Show the examiner that the query returns **0 rows**, proving the record was physically deleted from MySQL with transaction commit.

---

### DEMO 4 — DEMONSTRATE RELATIONAL JOINS & AGGREGATES
1. Click **SQL Lab** in the navigation bar (`http://127.0.0.1:5000/reports`).
2. Show the examiner:
   * **Multi-Table JOIN:** Shows Installation combined with Customer Name and Employee Name.
   * **Maintenance Cost GROUP BY:** Sums service expenses per installation project.
   * **Technician Workload:** Counts active installations assigned to each technician.
   * **Payment Mode Revenue:** Aggregates money collected across UPI, Card, Cash, and Bank Transfer.

---

## 11. Presentation-III Screenshot Checklist

Prepare your slide deck with these 16 clear screenshots:

| # | Screenshot Description | Where to Capture |
|---|------------------------|------------------|
| 1 | Main Dashboard | Web App (`/`) |
| 2 | Customer List BEFORE insertion | Web App (`/customers`) |
| 3 | Add Customer Form filled with Rahul Sharma | Web App (`/customers/add`) |
| 4 | Customer List AFTER insertion with success banner | Web App (`/customers`) |
| 5 | MySQL Workbench showing inserted record | Workbench `SELECT * FROM Customer;` |
| 6 | Customer List with Rahul Sharma selected | Web App (`/customers`) |
| 7 | Delete Confirmation Modal open | Web App (`/customers`) |
| 8 | Customer List AFTER deletion with success banner | Web App (`/customers`) |
| 9 | MySQL Workbench showing Rahul Sharma removed | Workbench `SELECT * FROM Customer;` |
| 10 | Installation Projects List (JOIN view) | Web App (`/installations`) |
| 11 | New Installation Form with foreign key dropdowns | Web App (`/installations/add`) |
| 12 | Employee Directory | Web App (`/employees`) |
| 13 | Equipment Inventory Table | Web App (`/equipment`) |
| 14 | Maintenance Visits List | Web App (`/maintenance`) |
| 15 | Payment Transactions & Receipts List | Web App (`/payments`) |
| 16 | Feedback Reviews List & SQL Lab Reports | Web App (`/feedback` & `/reports`) |

---

## 12. Explanation of Every Module for Viva

* **Customer Module:** Manages the primary contact records. Demonstrates basic CRUD, string input validation, and `ON DELETE CASCADE` down to child tables.
* **Employee Module:** Manages solar engineers and technicians. Demonstrates `ON DELETE RESTRICT` referential integrity (cannot delete a technician who is currently assigned to an active installation).
* **Equipment Module:** Inventory catalog of solar panels, inverters, and batteries with unit pricing. Demonstrates numeric decimal handling in SQL.
* **Installation Module:** Relational core of the system. Bridges Customer and Employee tables using foreign keys (`CustomerID` and `EmpID`). Demonstrates multi-table INNER JOINs.
* **Maintenance Module:** Tracks periodic panel cleaning, testing, and inverter servicing. Uses `InstallID` as a foreign key with `ON DELETE CASCADE`.
* **Payment Module:** Tracks financial inflows categorized by payment mode (Cash, UPI, Card, Bank Transfer). Uses `CustomerID` as foreign key. Demonstrates `SUM()` aggregate queries.
* **Feedback Module:** Client reviews with rating constraints (`CHECK (Rating BETWEEN 1 AND 5)`). Linked to `Installation`.
* **SQL Lab (`/reports`):** Demonstrates query optimization, multi-table joins, and grouped aggregate summaries for presentation purposes.

---

## 13. 2-Minute Presentation Script

> *"Respected Examiners and Professors, good morning/afternoon.*
> 
> *Today I present our DBMS project: **Solar Installation and Maintenance Service Management System**.*
> 
> *The solar energy sector requires precise tracking of client rooftops, equipment inventory, technician allocations, warranty maintenance, and payments. Manual tracking in spreadsheets leads to duplicate records, orphaned work orders, and financial mismatches.*
> 
> *To solve this, we designed a normalized relational database in **MySQL 8.0** named `solar_service_db`, comprising 7 structured tables: Customer, Employee, Equipment, Installation, Maintenance, Payment, and Feedback.*
> 
> *We implemented this with a Python Flask web application using native **`mysql-connector-python`**. Every operation on our UI executes parameterized SQL queries against our real MySQL Server with explicit transaction commits.*
> 
> *Let me demonstrate a live CRUD lifecycle:*
> 1. *First, here is our Customers page displaying current rows fetched directly via `SELECT * FROM Customer`.*
> 2. *Now, I register a customer: Rahul Sharma. Clicking Submit executes `INSERT INTO Customer`, and the record appears in our MySQL database with auto-increment ID.*
> 3. *Verifying in MySQL Workbench, the record is immediately visible.*
> 4. *Next, I delete this record. The modal triggers `DELETE FROM Customer WHERE CustomerID = ?` with transaction commit, instantly removing it from MySQL.*
> 5. *Finally, our SQL Lab demonstrates complex relational queries: 3-table INNER JOINs connecting installations to customers and technicians, and GROUP BY aggregations calculating maintenance costs and technician workloads.*
> 
> *Thank you, and I look forward to your questions."*

---

## 14. Viva Voce Questions & Answers

**Q1: Why did you choose MySQL instead of NoSQL like MongoDB for this system?**
> **Ans:** Solar installation and maintenance is inherently relational. An installation strictly depends on an existing customer and an assigned employee. MySQL provides ACID properties, foreign key constraints, and referential integrity that prevent orphaned or mismatched service records.

**Q2: What is the purpose of `ON DELETE CASCADE` and where is it used?**
> **Ans:** `ON DELETE CASCADE` automatically removes child records when the parent record is deleted. For example, if a Customer record is deleted, all their associated Installation, Payment, and Maintenance records are automatically deleted to maintain database consistency without orphaned foreign keys.

**Q3: Where is `ON DELETE RESTRICT` used and why?**
> **Ans:** In the `Installation` table, the foreign key to `Employee(EmpID)` uses `ON DELETE RESTRICT`. This prevents accidental deletion of an employee who is currently assigned to an active installation project.

**Q4: How does your Flask application prevent SQL Injection?**
> **Ans:** We use parameterized queries in `mysql-connector-python` with placeholder syntax (`%s`). User inputs are passed as parameters to `cursor.execute(sql, (param1, param2))` rather than string formatting, allowing the database engine to treat inputs strictly as literals.

**Q5: What is the difference between `fetchone()` and `fetchall()` in Python MySQL connector?**
> **Ans:** `fetchone()` retrieves the next single row from the query cursor (used for aggregate counts like `SELECT COUNT(*)` or fetching by Primary Key), while `fetchall()` retrieves all remaining rows of the result set as a list (used for displaying table rows).

**Q6: What is a transaction and why do you call `conn.commit()`?**
> **Ans:** A transaction is a sequence of database operations treated as a single atomic unit. For DML operations (`INSERT`, `UPDATE`, `DELETE`), MySQL InnoDB requires an explicit `commit()` to permanently save changes to disk. If an error occurs, `conn.rollback()` undoes any uncommitted changes.

---

## 15. Troubleshooting & Common Errors

### Error: `Access denied for user 'root'@'localhost'` (Code 1045)
* **Cause:** The password specified in `.env` does not match your MySQL Server root password.
* **Fix:** Open `.env` and set `MYSQL_PASSWORD=your_actual_password`. Restart `app.py`.

### Error: `Can't connect to MySQL server on 'localhost:3306'` (Code 2003)
* **Cause:** The MySQL Windows Service (`MySQL80`) is not running.
* **Fix:** Open PowerShell as Administrator and run:
  ```powershell
  Start-Service MySQL80
  ```
  Or press `Win + R`, type `services.msc`, locate `MySQL80`, and click **Start**.

### Error: `Cannot delete or update a parent row: a foreign key constraint fails` (Code 1451)
* **Cause:** You attempted to delete an Employee who has assigned projects in the `Installation` table (protected by `ON DELETE RESTRICT`).
* **Fix:** This is intended relational integrity! Reassign or delete the installation project before deleting the employee.

---
Developed for **DBMS Presentation-III**. Built with Python, Flask, MySQL, and Bootstrap.
