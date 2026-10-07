"""
Solar Installation and Maintenance Service Management System
Main Flask Application Controller
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import execute_query, test_db_connection, initialize_database, DB_NAME, DB_HOST, DB_PORT, DB_USER

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "solar-service-secret-key-2026")


@app.context_processor
def inject_global_data():
    """Injects current date and DB status for the header navbar."""
    connected, msg, db_exists = test_db_connection()
    return {
        "current_year": datetime.now().year,
        "db_connected": connected,
        "db_exists": db_exists,
        "db_name": DB_NAME,
        "db_status_msg": msg
    }


# =======================================================
# 1. MAIN DASHBOARD ROUTE
# =======================================================
@app.route("/")
def dashboard():
    """
    Renders the main dashboard with live KPI metrics from MySQL.
    Uses SELECT COUNT(*) and SELECT SUM(*) queries.
    """
    connected, msg, db_exists = test_db_connection()
    if not connected or not db_exists:
        return render_template(
            "index.html",
            metrics={
                "customers": 0, "employees": 0, "installations": 0,
                "equipment": 0, "maintenance": 0, "payments": 0,
                "feedback": 0, "total_revenue": 0.0, "total_collected": 0.0
            },
            recent_installations=[],
            recent_maintenance=[],
            db_error=msg
        )

    try:
        # Aggregated KPI Counts
        c_count = execute_query("SELECT COUNT(*) AS c FROM Customer;", fetch="one")["c"]
        e_count = execute_query("SELECT COUNT(*) AS c FROM Employee;", fetch="one")["c"]
        i_count = execute_query("SELECT COUNT(*) AS c FROM Installation;", fetch="one")["c"]
        eq_count = execute_query("SELECT COUNT(*) AS c FROM Equipment;", fetch="one")["c"]
        m_count = execute_query("SELECT COUNT(*) AS c FROM Maintenance;", fetch="one")["c"]
        p_count = execute_query("SELECT COUNT(*) AS c FROM Payment;", fetch="one")["c"]
        f_count = execute_query("SELECT COUNT(*) AS c FROM Feedback;", fetch="one")["c"]

        rev = execute_query("SELECT IFNULL(SUM(Cost), 0) AS total FROM Installation;", fetch="one")["total"]
        coll = execute_query("SELECT IFNULL(SUM(Amount), 0) AS total FROM Payment;", fetch="one")["total"]

        # Recent 5 Installations with JOIN
        recent_installations = execute_query("""
            SELECT i.InstallID, c.Name AS CustomerName, e.Name AS EmployeeName, 
                   i.InstallationDate, i.Capacity, i.Status, i.Cost
            FROM Installation i
            JOIN Customer c ON i.CustomerID = c.CustomerID
            JOIN Employee e ON i.EmpID = e.EmpID
            ORDER BY i.InstallID DESC LIMIT 5;
        """)

        # Recent 5 Maintenance Visits with JOIN
        recent_maintenance = execute_query("""
            SELECT m.MaintID, m.InstallID, c.Name AS CustomerName, 
                   m.VisitDate, m.WorkDescription, m.Cost
            FROM Maintenance m
            JOIN Installation i ON m.InstallID = i.InstallID
            JOIN Customer c ON i.CustomerID = c.CustomerID
            ORDER BY m.MaintID DESC LIMIT 5;
        """)

        metrics = {
            "customers": c_count,
            "employees": e_count,
            "installations": i_count,
            "equipment": eq_count,
            "maintenance": m_count,
            "payments": p_count,
            "feedback": f_count,
            "total_revenue": float(rev),
            "total_collected": float(coll)
        }

        return render_template(
            "index.html",
            metrics=metrics,
            recent_installations=recent_installations,
            recent_maintenance=recent_maintenance,
            db_error=None
        )
    except Exception as e:
        flash(f"Error querying database: {str(e)}", "danger")
        return render_template(
            "index.html",
            metrics={"customers": 0, "employees": 0, "installations": 0, "equipment": 0, "maintenance": 0, "payments": 0, "feedback": 0, "total_revenue": 0, "total_collected": 0},
            recent_installations=[],
            recent_maintenance=[],
            db_error=str(e)
        )


# =======================================================
# 2. CUSTOMER MODULE (CRUD)
# =======================================================
@app.route("/customers")
def customers_list():
    """Displays all customers with live MySQL SELECT."""
    search = request.args.get("search", "").strip()
    try:
        if search:
            query = "SELECT * FROM Customer WHERE Name LIKE %s OR Phone LIKE %s OR Email LIKE %s ORDER BY CustomerID DESC;"
            term = f"%{search}%"
            customers = execute_query(query, (term, term, term))
        else:
            customers = execute_query("SELECT * FROM Customer ORDER BY CustomerID DESC;")
        return render_template("customers.html", customers=customers, search=search)
    except Exception as e:
        flash(f"Error loading customers: {str(e)}", "danger")
        return render_template("customers.html", customers=[], search=search)


@app.route("/customers/add", methods=["GET", "POST"])
def customer_add():
    """Handles Customer creation (INSERT into Customer)."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()

        # Validation
        if not name or not phone or not email or not address:
            flash("All fields (Name, Phone, Email, Address) are required.", "warning")
            return render_template("customer_form.html", action="Add", customer=request.form)

        try:
            sql = "INSERT INTO Customer (Name, Phone, Email, Address) VALUES (%s, %s, %s, %s);"
            new_id = execute_query(sql, (name, phone, email, address), commit=True)
            flash(f"Customer '{name}' (ID: {new_id}) registered successfully in MySQL!", "success")
            return redirect(url_for("customers_list"))
        except Exception as e:
            flash(f"Failed to add customer: {str(e)}", "danger")
            return render_template("customer_form.html", action="Add", customer=request.form)

    return render_template("customer_form.html", action="Add", customer={})


@app.route("/customers/edit/<int:customer_id>", methods=["GET", "POST"])
def customer_edit(customer_id):
    """Handles updating customer details (UPDATE Customer)."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not phone or not email or not address:
            flash("All fields are required.", "warning")
            return render_template("customer_form.html", action="Edit", customer=request.form)

        try:
            sql = "UPDATE Customer SET Name = %s, Phone = %s, Email = %s, Address = %s WHERE CustomerID = %s;"
            execute_query(sql, (name, phone, email, address, customer_id), commit=True)
            flash(f"Customer ID {customer_id} updated successfully!", "success")
            return redirect(url_for("customers_list"))
        except Exception as e:
            flash(f"Failed to update customer: {str(e)}", "danger")
            return render_template("customer_form.html", action="Edit", customer=request.form)

    customer = execute_query("SELECT * FROM Customer WHERE CustomerID = %s;", (customer_id,), fetch="one")
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for("customers_list"))
    return render_template("customer_form.html", action="Edit", customer=customer)


@app.route("/customers/view/<int:customer_id>")
def customer_view(customer_id):
    """Displays detailed profile of a single customer with their projects and payments."""
    try:
        customer = execute_query("SELECT * FROM Customer WHERE CustomerID = %s;", (customer_id,), fetch="one")
        if not customer:
            flash("Customer not found.", "danger")
            return redirect(url_for("customers_list"))

        installations = execute_query("""
            SELECT i.*, e.Name AS EmployeeName 
            FROM Installation i 
            JOIN Employee e ON i.EmpID = e.EmpID 
            WHERE i.CustomerID = %s 
            ORDER BY i.InstallID DESC;
        """, (customer_id,))

        payments = execute_query("""
            SELECT * FROM Payment WHERE CustomerID = %s ORDER BY PaymentDate DESC;
        """, (customer_id,))

        return render_template("customer_view.html", customer=customer, installations=installations, payments=payments)
    except Exception as e:
        flash(f"Error fetching customer details: {str(e)}", "danger")
        return redirect(url_for("customers_list"))


@app.route("/customers/delete/<int:customer_id>", methods=["POST"])
def customer_delete(customer_id):
    """Handles customer deletion (DELETE FROM Customer)."""
    try:
        # Check if customer exists
        cust = execute_query("SELECT Name FROM Customer WHERE CustomerID = %s;", (customer_id,), fetch="one")
        name = cust["Name"] if cust else f"ID {customer_id}"

        sql = "DELETE FROM Customer WHERE CustomerID = %s;"
        execute_query(sql, (customer_id,), commit=True)
        flash(f"Customer '{name}' (ID: {customer_id}) deleted successfully from MySQL.", "success")
    except Exception as e:
        flash(f"Cannot delete customer: {str(e)}", "danger")
    return redirect(url_for("customers_list"))


# =======================================================
# 3. EMPLOYEE MODULE (CRUD)
# =======================================================
@app.route("/employees")
def employees_list():
    """Displays all employees."""
    try:
        employees = execute_query("SELECT * FROM Employee ORDER BY EmpID DESC;")
        return render_template("employees.html", employees=employees)
    except Exception as e:
        flash(f"Error loading employees: {str(e)}", "danger")
        return render_template("employees.html", employees=[])


@app.route("/employees/add", methods=["GET", "POST"])
def employee_add():
    """Handles adding an employee (INSERT INTO Employee)."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        role = request.form.get("role", "").strip()
        phone = request.form.get("phone", "").strip()
        salary = request.form.get("salary", "").strip()

        if not name or not role or not phone or not salary:
            flash("All fields are required.", "warning")
            return render_template("employee_form.html", action="Add", employee=request.form)

        try:
            sql = "INSERT INTO Employee (Name, Role, Phone, Salary) VALUES (%s, %s, %s, %s);"
            new_id = execute_query(sql, (name, role, phone, float(salary)), commit=True)
            flash(f"Employee '{name}' (ID: {new_id}) added successfully!", "success")
            return redirect(url_for("employees_list"))
        except Exception as e:
            flash(f"Failed to add employee: {str(e)}", "danger")
            return render_template("employee_form.html", action="Add", employee=request.form)

    return render_template("employee_form.html", action="Add", employee={})


@app.route("/employees/edit/<int:emp_id>", methods=["GET", "POST"])
def employee_edit(emp_id):
    """Handles updating employee details."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        role = request.form.get("role", "").strip()
        phone = request.form.get("phone", "").strip()
        salary = request.form.get("salary", "").strip()

        try:
            sql = "UPDATE Employee SET Name = %s, Role = %s, Phone = %s, Salary = %s WHERE EmpID = %s;"
            execute_query(sql, (name, role, phone, float(salary), emp_id), commit=True)
            flash(f"Employee ID {emp_id} updated successfully!", "success")
            return redirect(url_for("employees_list"))
        except Exception as e:
            flash(f"Failed to update employee: {str(e)}", "danger")
            return render_template("employee_form.html", action="Edit", employee=request.form)

    employee = execute_query("SELECT * FROM Employee WHERE EmpID = %s;", (emp_id,), fetch="one")
    if not employee:
        flash("Employee not found.", "danger")
        return redirect(url_for("employees_list"))
    return render_template("employee_form.html", action="Edit", employee=employee)


@app.route("/employees/delete/<int:emp_id>", methods=["POST"])
def employee_delete(emp_id):
    """Handles employee deletion (DELETE FROM Employee)."""
    try:
        sql = "DELETE FROM Employee WHERE EmpID = %s;"
        execute_query(sql, (emp_id,), commit=True)
        flash(f"Employee ID {emp_id} deleted successfully from MySQL.", "success")
    except Exception as e:
        flash(f"Cannot delete employee: {str(e)}", "danger")
    return redirect(url_for("employees_list"))


# =======================================================
# 4. EQUIPMENT MODULE (CRUD)
# =======================================================
@app.route("/equipment")
def equipment_list():
    """Displays all equipment."""
    try:
        equipment = execute_query("SELECT * FROM Equipment ORDER BY EquipID DESC;")
        return render_template("equipment.html", equipment=equipment)
    except Exception as e:
        flash(f"Error loading equipment: {str(e)}", "danger")
        return render_template("equipment.html", equipment=[])


@app.route("/equipment/add", methods=["GET", "POST"])
def equipment_add():
    """Handles adding equipment (INSERT INTO Equipment)."""
    if request.method == "POST":
        equip_name = request.form.get("equip_name", "").strip()
        equip_type = request.form.get("type", "").strip()
        price = request.form.get("price", "").strip()

        if not equip_name or not equip_type or not price:
            flash("All fields are required.", "warning")
            return render_template("equipment_form.html", action="Add", equipment=request.form)

        try:
            sql = "INSERT INTO Equipment (EquipName, Type, Price) VALUES (%s, %s, %s);"
            new_id = execute_query(sql, (equip_name, equip_type, float(price)), commit=True)
            flash(f"Equipment '{equip_name}' (ID: {new_id}) added successfully!", "success")
            return redirect(url_for("equipment_list"))
        except Exception as e:
            flash(f"Failed to add equipment: {str(e)}", "danger")
            return render_template("equipment_form.html", action="Add", equipment=request.form)

    return render_template("equipment_form.html", action="Add", equipment={})


@app.route("/equipment/edit/<int:equip_id>", methods=["GET", "POST"])
def equipment_edit(equip_id):
    """Handles updating equipment details."""
    if request.method == "POST":
        equip_name = request.form.get("equip_name", "").strip()
        equip_type = request.form.get("type", "").strip()
        price = request.form.get("price", "").strip()

        try:
            sql = "UPDATE Equipment SET EquipName = %s, Type = %s, Price = %s WHERE EquipID = %s;"
            execute_query(sql, (equip_name, equip_type, float(price), equip_id), commit=True)
            flash(f"Equipment ID {equip_id} updated successfully!", "success")
            return redirect(url_for("equipment_list"))
        except Exception as e:
            flash(f"Failed to update equipment: {str(e)}", "danger")
            return render_template("equipment_form.html", action="Edit", equipment=request.form)

    equipment = execute_query("SELECT * FROM Equipment WHERE EquipID = %s;", (equip_id,), fetch="one")
    if not equipment:
        flash("Equipment item not found.", "danger")
        return redirect(url_for("equipment_list"))
    return render_template("equipment_form.html", action="Edit", equipment=equipment)


@app.route("/equipment/delete/<int:equip_id>", methods=["POST"])
def equipment_delete(equip_id):
    """Handles equipment deletion (DELETE FROM Equipment)."""
    try:
        sql = "DELETE FROM Equipment WHERE EquipID = %s;"
        execute_query(sql, (equip_id,), commit=True)
        flash(f"Equipment ID {equip_id} deleted successfully from MySQL.", "success")
    except Exception as e:
        flash(f"Cannot delete equipment: {str(e)}", "danger")
    return redirect(url_for("equipment_list"))


# =======================================================
# 5. INSTALLATION MODULE (CRUD + JOIN)
# =======================================================
@app.route("/installations")
def installations_list():
    """Displays all installations with Customer and Employee names via JOIN."""
    try:
        installations = execute_query("""
            SELECT i.InstallID, i.CustomerID, c.Name AS CustomerName, c.Phone AS CustomerPhone,
                   i.EmpID, e.Name AS EmployeeName, e.Role AS EmployeeRole,
                   i.InstallationDate, i.Capacity, i.Status, i.Cost
            FROM Installation i
            JOIN Customer c ON i.CustomerID = c.CustomerID
            JOIN Employee e ON i.EmpID = e.EmpID
            ORDER BY i.InstallID DESC;
        """)
        return render_template("installations.html", installations=installations)
    except Exception as e:
        flash(f"Error loading installations: {str(e)}", "danger")
        return render_template("installations.html", installations=[])


@app.route("/installations/add", methods=["GET", "POST"])
def installation_add():
    """Handles adding a new installation project."""
    try:
        customers = execute_query("SELECT CustomerID, Name FROM Customer ORDER BY Name;") or []
        employees = execute_query("SELECT EmpID, Name, Role FROM Employee ORDER BY Name;") or []
    except Exception as e:
        customers, employees = [], []
        flash(f"Database error loading dropdown choices: {str(e)}", "danger")

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        emp_id = request.form.get("emp_id")
        install_date = request.form.get("installation_date")
        capacity = request.form.get("capacity", "").strip()
        status = request.form.get("status", "").strip()
        cost = request.form.get("cost", "").strip()

        if not customer_id or not emp_id or not install_date or not capacity or not status or not cost:
            flash("All fields are required.", "warning")
            return render_template("installation_form.html", action="Add", installation=request.form, customers=customers, employees=employees)

        try:
            sql = """
                INSERT INTO Installation (CustomerID, EmpID, InstallationDate, Capacity, Status, Cost) 
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            new_id = execute_query(sql, (customer_id, emp_id, install_date, capacity, status, float(cost)), commit=True)
            flash(f"Installation project ID {new_id} created successfully!", "success")
            return redirect(url_for("installations_list"))
        except Exception as e:
            flash(f"Failed to add installation: {str(e)}", "danger")
            return render_template("installation_form.html", action="Add", installation=request.form, customers=customers, employees=employees)

    return render_template("installation_form.html", action="Add", installation={}, customers=customers, employees=employees)


@app.route("/installations/edit/<int:install_id>", methods=["GET", "POST"])
def installation_edit(install_id):
    """Handles updating installation details."""
    try:
        customers = execute_query("SELECT CustomerID, Name FROM Customer ORDER BY Name;") or []
        employees = execute_query("SELECT EmpID, Name, Role FROM Employee ORDER BY Name;") or []
    except Exception as e:
        customers, employees = [], []
        flash(f"Database error loading dropdown choices: {str(e)}", "danger")

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        emp_id = request.form.get("emp_id")
        install_date = request.form.get("installation_date")
        capacity = request.form.get("capacity", "").strip()
        status = request.form.get("status", "").strip()
        cost = request.form.get("cost", "").strip()

        try:
            sql = """
                UPDATE Installation 
                SET CustomerID = %s, EmpID = %s, InstallationDate = %s, Capacity = %s, Status = %s, Cost = %s 
                WHERE InstallID = %s;
            """
            execute_query(sql, (customer_id, emp_id, install_date, capacity, status, float(cost), install_id), commit=True)
            flash(f"Installation ID {install_id} updated successfully!", "success")
            return redirect(url_for("installations_list"))
        except Exception as e:
            flash(f"Failed to update installation: {str(e)}", "danger")
            return render_template("installation_form.html", action="Edit", installation=request.form, customers=customers, employees=employees)

    installation = execute_query("SELECT * FROM Installation WHERE InstallID = %s;", (install_id,), fetch="one")
    if not installation:
        flash("Installation not found.", "danger")
        return redirect(url_for("installations_list"))
    return render_template("installation_form.html", action="Edit", installation=installation, customers=customers, employees=employees)


@app.route("/installations/view/<int:install_id>")
def installation_view(install_id):
    """Displays detailed installation view with its maintenance visits and feedback."""
    try:
        installation = execute_query("""
            SELECT i.*, c.Name AS CustomerName, c.Phone AS CustomerPhone, c.Email AS CustomerEmail, c.Address,
                   e.Name AS EmployeeName, e.Role AS EmployeeRole, e.Phone AS EmployeePhone
            FROM Installation i
            JOIN Customer c ON i.CustomerID = c.CustomerID
            JOIN Employee e ON i.EmpID = e.EmpID
            WHERE i.InstallID = %s;
        """, (install_id,), fetch="one")

        if not installation:
            flash("Installation record not found.", "danger")
            return redirect(url_for("installations_list"))

        maintenance = execute_query("SELECT * FROM Maintenance WHERE InstallID = %s ORDER BY VisitDate DESC;", (install_id,))
        feedback = execute_query("SELECT * FROM Feedback WHERE InstallID = %s ORDER BY FeedbackID DESC;", (install_id,))

        return render_template("installation_view.html", installation=installation, maintenance=maintenance, feedback=feedback)
    except Exception as e:
        flash(f"Error loading installation details: {str(e)}", "danger")
        return redirect(url_for("installations_list"))


@app.route("/installations/delete/<int:install_id>", methods=["POST"])
def installation_delete(install_id):
    """Handles installation deletion (DELETE FROM Installation)."""
    try:
        sql = "DELETE FROM Installation WHERE InstallID = %s;"
        execute_query(sql, (install_id,), commit=True)
        flash(f"Installation record ID {install_id} deleted successfully from MySQL.", "success")
    except Exception as e:
        flash(f"Cannot delete installation: {str(e)}", "danger")
    return redirect(url_for("installations_list"))


# =======================================================
# 6. MAINTENANCE MODULE (CRUD + JOIN)
# =======================================================
@app.route("/maintenance")
def maintenance_list():
    """Displays all maintenance visits with Installation and Customer names."""
    try:
        visits = execute_query("""
            SELECT m.MaintID, m.InstallID, c.Name AS CustomerName, i.Capacity, 
                   m.VisitDate, m.WorkDescription, m.Cost
            FROM Maintenance m
            JOIN Installation i ON m.InstallID = i.InstallID
            JOIN Customer c ON i.CustomerID = c.CustomerID
            ORDER BY m.MaintID DESC;
        """)
        return render_template("maintenance.html", visits=visits)
    except Exception as e:
        flash(f"Error loading maintenance records: {str(e)}", "danger")
        return render_template("maintenance.html", visits=[])


@app.route("/maintenance/add", methods=["GET", "POST"])
def maintenance_add():
    """Handles adding a maintenance record."""
    try:
        installations = execute_query("""
            SELECT i.InstallID, c.Name AS CustomerName, i.Capacity 
            FROM Installation i 
            JOIN Customer c ON i.CustomerID = c.CustomerID 
            ORDER BY i.InstallID DESC;
        """) or []
    except Exception as e:
        installations = []
        flash(f"Database error loading installations: {str(e)}", "danger")

    if request.method == "POST":
        install_id = request.form.get("install_id")
        visit_date = request.form.get("visit_date")
        work_desc = request.form.get("work_description", "").strip()
        cost = request.form.get("cost", "").strip()

        if not install_id or not visit_date or not work_desc or not cost:
            flash("All fields are required.", "warning")
            return render_template("maintenance_form.html", action="Add", visit=request.form, installations=installations)

        try:
            sql = "INSERT INTO Maintenance (InstallID, VisitDate, WorkDescription, Cost) VALUES (%s, %s, %s, %s);"
            new_id = execute_query(sql, (install_id, visit_date, work_desc, float(cost)), commit=True)
            flash(f"Maintenance visit ID {new_id} recorded successfully!", "success")
            return redirect(url_for("maintenance_list"))
        except Exception as e:
            flash(f"Failed to record maintenance: {str(e)}", "danger")
            return render_template("maintenance_form.html", action="Add", visit=request.form, installations=installations)

    return render_template("maintenance_form.html", action="Add", visit={}, installations=installations)


@app.route("/maintenance/edit/<int:maint_id>", methods=["GET", "POST"])
def maintenance_edit(maint_id):
    """Handles updating a maintenance record."""
    try:
        installations = execute_query("""
            SELECT i.InstallID, c.Name AS CustomerName, i.Capacity 
            FROM Installation i 
            JOIN Customer c ON i.CustomerID = c.CustomerID 
            ORDER BY i.InstallID DESC;
        """) or []
    except Exception as e:
        installations = []
        flash(f"Database error loading installations: {str(e)}", "danger")

    if request.method == "POST":
        install_id = request.form.get("install_id")
        visit_date = request.form.get("visit_date")
        work_desc = request.form.get("work_description", "").strip()
        cost = request.form.get("cost", "").strip()

        try:
            sql = "UPDATE Maintenance SET InstallID = %s, VisitDate = %s, WorkDescription = %s, Cost = %s WHERE MaintID = %s;"
            execute_query(sql, (install_id, visit_date, work_desc, float(cost), maint_id), commit=True)
            flash(f"Maintenance record ID {maint_id} updated successfully!", "success")
            return redirect(url_for("maintenance_list"))
        except Exception as e:
            flash(f"Failed to update maintenance: {str(e)}", "danger")
            return render_template("maintenance_form.html", action="Edit", visit=request.form, installations=installations)

    visit = execute_query("SELECT * FROM Maintenance WHERE MaintID = %s;", (maint_id,), fetch="one")
    if not visit:
        flash("Maintenance record not found.", "danger")
        return redirect(url_for("maintenance_list"))
    return render_template("maintenance_form.html", action="Edit", visit=visit, installations=installations)


@app.route("/maintenance/delete/<int:maint_id>", methods=["POST"])
def maintenance_delete(maint_id):
    """Handles deleting a maintenance record."""
    try:
        sql = "DELETE FROM Maintenance WHERE MaintID = %s;"
        execute_query(sql, (maint_id,), commit=True)
        flash(f"Maintenance record ID {maint_id} deleted successfully from MySQL.", "success")
    except Exception as e:
        flash(f"Cannot delete maintenance record: {str(e)}", "danger")
    return redirect(url_for("maintenance_list"))


# =======================================================
# 7. PAYMENT MODULE (CRUD + JOIN)
# =======================================================
@app.route("/payments")
def payments_list():
    """Displays all payments with customer details and total collected sum."""
    try:
        payments = execute_query("""
            SELECT p.PaymentID, p.CustomerID, c.Name AS CustomerName, c.Phone AS CustomerPhone,
                   p.Amount, p.PaymentDate, p.Mode
            FROM Payment p
            JOIN Customer c ON p.CustomerID = c.CustomerID
            ORDER BY p.PaymentID DESC;
        """) or []
        total_sum = sum([float(p["Amount"]) for p in payments]) if payments else 0.0
        return render_template("payments.html", payments=payments, total_sum=total_sum)
    except Exception as e:
        flash(f"Error loading payments: {str(e)}", "danger")
        return render_template("payments.html", payments=[], total_sum=0.0)


@app.route("/payments/add", methods=["GET", "POST"])
def payment_add():
    """Handles recording a new customer payment."""
    try:
        customers = execute_query("SELECT CustomerID, Name FROM Customer ORDER BY Name;") or []
    except Exception as e:
        customers = []
        flash(f"Database error loading customers: {str(e)}", "danger")

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        amount = request.form.get("amount", "").strip()
        payment_date = request.form.get("payment_date")
        mode = request.form.get("mode", "").strip()

        if not customer_id or not amount or not payment_date or not mode:
            flash("All fields are required.", "warning")
            return render_template("payment_form.html", action="Add", payment=request.form, customers=customers)

        try:
            sql = "INSERT INTO Payment (CustomerID, Amount, PaymentDate, Mode) VALUES (%s, %s, %s, %s);"
            new_id = execute_query(sql, (customer_id, float(amount), payment_date, mode), commit=True)
            flash(f"Payment ID {new_id} of ₹{float(amount):,.2f} recorded successfully!", "success")
            return redirect(url_for("payments_list"))
        except Exception as e:
            flash(f"Failed to record payment: {str(e)}", "danger")
            return render_template("payment_form.html", action="Add", payment=request.form, customers=customers)

    return render_template("payment_form.html", action="Add", payment={}, customers=customers)


@app.route("/payments/edit/<int:payment_id>", methods=["GET", "POST"])
def payment_edit(payment_id):
    """Handles editing payment records."""
    try:
        customers = execute_query("SELECT CustomerID, Name FROM Customer ORDER BY Name;") or []
    except Exception as e:
        customers = []
        flash(f"Database error loading customers: {str(e)}", "danger")

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        amount = request.form.get("amount", "").strip()
        payment_date = request.form.get("payment_date")
        mode = request.form.get("mode", "").strip()

        try:
            sql = "UPDATE Payment SET CustomerID = %s, Amount = %s, PaymentDate = %s, Mode = %s WHERE PaymentID = %s;"
            execute_query(sql, (customer_id, float(amount), payment_date, mode, payment_id), commit=True)
            flash(f"Payment record ID {payment_id} updated successfully!", "success")
            return redirect(url_for("payments_list"))
        except Exception as e:
            flash(f"Failed to update payment: {str(e)}", "danger")
            return render_template("payment_form.html", action="Edit", payment=request.form, customers=customers)

    payment = execute_query("SELECT * FROM Payment WHERE PaymentID = %s;", (payment_id,), fetch="one")
    if not payment:
        flash("Payment not found.", "danger")
        return redirect(url_for("payments_list"))
    return render_template("payment_form.html", action="Edit", payment=payment, customers=customers)


@app.route("/payments/delete/<int:payment_id>", methods=["POST"])
def payment_delete(payment_id):
    """Handles deleting a payment record."""
    try:
        sql = "DELETE FROM Payment WHERE PaymentID = %s;"
        execute_query(sql, (payment_id,), commit=True)
        flash(f"Payment record ID {payment_id} deleted successfully from MySQL.", "success")
    except Exception as e:
        flash(f"Cannot delete payment: {str(e)}", "danger")
    return redirect(url_for("payments_list"))


# =======================================================
# 8. FEEDBACK MODULE (CRUD + JOIN)
# =======================================================
@app.route("/feedback")
def feedback_list():
    """Displays all feedback entries with project details."""
    try:
        feedback = execute_query("""
            SELECT f.FeedbackID, f.InstallID, c.Name AS CustomerName, i.Capacity,
                   f.Rating, f.Comments, f.CreatedAt
            FROM Feedback f
            JOIN Installation i ON f.InstallID = i.InstallID
            JOIN Customer c ON i.CustomerID = c.CustomerID
            ORDER BY f.FeedbackID DESC;
        """) or []
        return render_template("feedback.html", feedback=feedback)
    except Exception as e:
        flash(f"Error loading feedback: {str(e)}", "danger")
        return render_template("feedback.html", feedback=[])


@app.route("/feedback/add", methods=["GET", "POST"])
def feedback_add():
    """Handles adding a new customer feedback review."""
    try:
        installations = execute_query("""
            SELECT i.InstallID, c.Name AS CustomerName, i.Capacity 
            FROM Installation i 
            JOIN Customer c ON i.CustomerID = c.CustomerID 
            ORDER BY i.InstallID DESC;
        """) or []
    except Exception as e:
        installations = []
        flash(f"Database error loading installations: {str(e)}", "danger")

    if request.method == "POST":
        install_id = request.form.get("install_id")
        rating = request.form.get("rating")
        comments = request.form.get("comments", "").strip()

        if not install_id or not rating:
            flash("Installation and Rating are required.", "warning")
            return render_template("feedback_form.html", action="Add", feedback=request.form, installations=installations)

        try:
            sql = "INSERT INTO Feedback (InstallID, Rating, Comments) VALUES (%s, %s, %s);"
            new_id = execute_query(sql, (install_id, int(rating), comments), commit=True)
            flash(f"Feedback ID {new_id} submitted successfully!", "success")
            return redirect(url_for("feedback_list"))
        except Exception as e:
            flash(f"Failed to record feedback: {str(e)}", "danger")
            return render_template("feedback_form.html", action="Add", feedback=request.form, installations=installations)

    return render_template("feedback_form.html", action="Add", feedback={}, installations=installations)


@app.route("/feedback/delete/<int:feedback_id>", methods=["POST"])
def feedback_delete(feedback_id):
    """Handles feedback deletion."""
    try:
        sql = "DELETE FROM Feedback WHERE FeedbackID = %s;"
        execute_query(sql, (feedback_id,), commit=True)
        flash(f"Feedback entry ID {feedback_id} deleted successfully from MySQL.", "success")
    except Exception as e:
        flash(f"Cannot delete feedback: {str(e)}", "danger")
    return redirect(url_for("feedback_list"))


# =======================================================
# 9. PRESENTATION SQL LAB / REPORTS ROUTE
# =======================================================
@app.route("/reports")
def reports_page():
    """
    Interactive DBMS Presentation Lab:
    Executes and demonstrates real SQL operations (JOIN, GROUP BY, SUM, COUNT) live
    with query strings and tabular output side-by-side for examiners.
    """
    reports = {
        "join_installations": {
            "title": "1. Multi-Table Relational JOIN (Installation + Customer + Employee)",
            "query": """SELECT i.InstallID, c.Name AS CustomerName, c.Phone, e.Name AS Engineer, i.Capacity, i.Status, i.Cost
FROM Installation i
JOIN Customer c ON i.CustomerID = c.CustomerID
JOIN Employee e ON i.EmpID = e.EmpID
ORDER BY i.InstallID DESC;""",
            "data": []
        },
        "maint_cost": {
            "title": "2. Maintenance Cost Analysis (GROUP BY InstallID, SUM(Cost), COUNT)",
            "query": """SELECT InstallID, COUNT(MaintID) AS TotalVisits, SUM(Cost) AS TotalMaintenanceCost
FROM Maintenance
GROUP BY InstallID
ORDER BY TotalMaintenanceCost DESC;""",
            "data": []
        },
        "tech_workload": {
            "title": "3. Technician Workload Distribution (LEFT JOIN & COUNT)",
            "query": """SELECT e.EmpID, e.Name AS EmployeeName, e.Role, COUNT(i.InstallID) AS TotalProjects
FROM Employee e
LEFT JOIN Installation i ON e.EmpID = i.EmpID
GROUP BY e.EmpID, e.Name, e.Role
ORDER BY TotalProjects DESC;""",
            "data": []
        },
        "revenue_mode": {
            "title": "4. Revenue Breakdown by Payment Mode (GROUP BY Mode, SUM(Amount))",
            "query": """SELECT Mode, COUNT(PaymentID) AS Transactions, SUM(Amount) AS TotalCollected
FROM Payment
GROUP BY Mode
ORDER BY TotalCollected DESC;""",
            "data": []
        }
    }

    try:
        reports["join_installations"]["data"] = execute_query("""
            SELECT i.InstallID, c.Name AS CustomerName, c.Phone, e.Name AS Engineer, i.Capacity, i.Status, i.Cost
            FROM Installation i
            JOIN Customer c ON i.CustomerID = c.CustomerID
            JOIN Employee e ON i.EmpID = e.EmpID
            ORDER BY i.InstallID DESC;
        """) or []

        reports["maint_cost"]["data"] = execute_query("""
            SELECT InstallID, COUNT(MaintID) AS TotalVisits, SUM(Cost) AS TotalMaintenanceCost
            FROM Maintenance
            GROUP BY InstallID
            ORDER BY TotalMaintenanceCost DESC;
        """) or []

        reports["tech_workload"]["data"] = execute_query("""
            SELECT e.EmpID, e.Name AS EmployeeName, e.Role, COUNT(i.InstallID) AS TotalProjects
            FROM Employee e
            LEFT JOIN Installation i ON e.EmpID = i.EmpID
            GROUP BY e.EmpID, e.Name, e.Role
            ORDER BY TotalProjects DESC;
        """) or []

        reports["revenue_mode"]["data"] = execute_query("""
            SELECT Mode, COUNT(PaymentID) AS Transactions, SUM(Amount) AS TotalCollected
            FROM Payment
            GROUP BY Mode
            ORDER BY TotalCollected DESC;
        """) or []

    except Exception as e:
        flash(f"Database notice: {str(e)}", "danger")

    return render_template("reports.html", reports=reports)


# =======================================================
# 10. DATABASE INITIALIZATION / STATUS ROUTE
# =======================================================
@app.route("/db-setup", methods=["GET", "POST"])
def db_setup():
    """Provides a web-based setup and reset tool for presentation rehearsals."""
    status, msg, db_exists = test_db_connection()
    table_counts = {}

    if status and db_exists:
        tables = ["Customer", "Employee", "Equipment", "Installation", "Maintenance", "Payment", "Feedback"]
        for t in tables:
            try:
                res = execute_query(f"SELECT COUNT(*) AS c FROM {t};", fetch="one")
                table_counts[t] = res["c"] if res else 0
            except Exception:
                table_counts[t] = "Not Created"

    if request.method == "POST":
        action = request.form.get("action")
        if action == "init":
            try:
                initialize_database("schema.sql", "seed.sql")
                flash("Database successfully initialized with schema and seed data!", "success")
                return redirect(url_for("db_setup"))
            except Exception as e:
                flash(f"Failed to initialize database: {str(e)}", "danger")

    return render_template("db_setup.html", status=status, msg=msg, db_exists=db_exists, table_counts=table_counts, host=DB_HOST, port=DB_PORT, user=DB_USER, db_name=DB_NAME)


# =======================================================
# 11. RANDOM SQL DATA GENERATOR & DEMONSTRATION ROUTE
# =======================================================
@app.route("/random-data", methods=["GET", "POST"])
@app.route("/random-sql-data", methods=["GET", "POST"])
def random_data_page():
    """
    Generates and showcases dynamic random SQL datasets with real-time SQL statements.
    Allows examiners and students to generate fresh random solar data and execute it against MySQL.
    """
    import random
    first_names = ["Karthik", "Ananya", "Rohit", "Meera", "Sanjay", "Pooja", "Arjun", "Sneha", "Vikram", "Divya"]
    last_names = ["Subramanian", "Deshmukh", "Verma", "Kulkarni", "Rao", "Chawla", "Nair", "Reddy", "Sharma", "Patel"]
    cities = ["Hyderabad", "Chennai", "Bengaluru", "Pune", "Noida", "Mumbai", "Ahmedabad", "Kolkata", "Delhi"]
    localities = ["Banjara Hills", "T. Nagar", "Koramangala", "Shivaji Nagar", "Sector 62", "Salt Lake", "Jubilee Hills", "Indiranagar"]
    capacities = ["3 kW On-Grid Rooftop", "5 kW Hybrid Energy System", "8 kW Residential Solar", "10 kW Commercial Array", "15 kW Off-Grid Project"]
    statuses = ["Pending", "In Progress", "Completed", "Scheduled"]
    costs = [165000, 245000, 380000, 490000, 720000]
    payment_modes = ["UPI", "Bank Transfer", "Card", "Cash"]
    
    sample_customers = []
    for _ in range(4):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        city = random.choice(cities)
        loc = random.choice(localities)
        name = f"{fn} {ln}"
        phone = f"98{random.randint(10000000, 99999999)}"
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@gmail.com"
        addr = f"Plot {random.randint(12, 180)}, {loc}, {city}"
        sample_customers.append({
            "name": name,
            "phone": phone,
            "email": email,
            "address": addr
        })

    sample_installations = [
        {
            "customer_name": sample_customers[0]["name"],
            "capacity": random.choice(capacities),
            "status": random.choice(statuses),
            "cost": random.choice(costs),
            "date": "2026-04-12"
        },
        {
            "customer_name": sample_customers[1]["name"],
            "capacity": random.choice(capacities),
            "status": random.choice(statuses),
            "cost": random.choice(costs),
            "date": "2026-04-18"
        }
    ]

    sample_payments = [
        {
            "customer_name": sample_customers[0]["name"],
            "amount": float(random.choice([75000, 100000, 150000])),
            "date": "2026-04-10",
            "mode": random.choice(payment_modes)
        },
        {
            "customer_name": sample_customers[1]["name"],
            "amount": float(random.choice([50000, 90000, 120000])),
            "date": "2026-04-15",
            "mode": random.choice(payment_modes)
        }
    ]

    # Build SQL script text
    sql_script_lines = [
        "-- ========================================================",
        "-- Generated Random SQL Batch for Solar Service DBMS",
        "-- ========================================================",
        "USE solar_service_db;",
        ""
    ]
    for c in sample_customers:
        sql_script_lines.append(f"INSERT INTO Customer (Name, Phone, Email, Address) VALUES ('{c['name']}', '{c['phone']}', '{c['email']}', '{c['address']}');")
    
    sql_script = "\n".join(sql_script_lines)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "insert_random":
            try:
                inserted_count = 0
                for c in sample_customers:
                    sql = "INSERT INTO Customer (Name, Phone, Email, Address) VALUES (%s, %s, %s, %s);"
                    execute_query(sql, (c["name"], c["phone"], c["email"], c["address"]), commit=True)
                    inserted_count += 1
                
                flash(f"Successfully executed SQL and inserted {inserted_count} random customer records directly into MySQL!", "success")
                return redirect(url_for("customers_list"))
            except Exception as e:
                flash(f"Failed to insert into MySQL: {str(e)}", "danger")

    return render_template(
        "random_data.html",
        customers=sample_customers,
        installations=sample_installations,
        payments=sample_payments,
        sql_script=sql_script
    )


if __name__ == "__main__":
    print(f"Starting Solar Service DBMS on http://127.0.0.1:5000 ...")
    app.run(debug=True, host="127.0.0.1", port=5000)
