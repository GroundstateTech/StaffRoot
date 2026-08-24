# Groundstate Control Center Integration Pattern

The Groundstate Admin Control Center is the master source of truth for:

- companies
- users
- employees
- roles
- departments
- app permissions
- audit routing

StaffRoot remains the HR/payroll module. It owns payroll-specific data:

- pay rates
- pay schedules
- time entries
- payroll runs
- paystubs
- deductions

## StaffRoot sync fields

StaffRoot stores external references:

- `Employee.admin_center_employee_id`
- `User.admin_center_user_id`
- `Employee.source_system`
- `Employee.last_synced_at`

## Standard app pattern for all Groundstate apps

Each app should include:

- `core/admin_center_client.py`
- local config file with Admin Center URL/API key
- sync tab or sync service
- standalone fallback mode
- app-local tables for app-specific data only

## Expected Admin Center employee payload

```json
[
  {
    "id": "emp_123",
    "first_name": "Ada",
    "last_name": "Lovelace",
    "email": "ada@example.com",
    "phone": "555-0000",
    "department": "Engineering",
    "position": "Analyst",
    "status": "Active",
    "date_of_birth": "1990-01-01",
    "address_line1": "123 Root St",
    "city": "Cleveland",
    "state": "OH",
    "postal_code": "44101",
    "country": "USA"
  }
]
```
