import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from sqlalchemy.orm import Session

from core.admin_center_client import AdminCenterClient, AdminCenterError
from core.audit import log_event
from core.config import ensure_local_config, save_local_config
from db.models import Employee, JobDetail, User


def _parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except Exception:
        return None


class AdminSyncView(ttk.Frame):
    def __init__(self, master, db: Session, current_user: User):
        super().__init__(master)
        self.db = db
        self.current_user = current_user
        self.config = ensure_local_config()
        self.base_url_var = tk.StringVar(self, value=self.config.get("admin_center_base_url", ""))
        self.api_key_var = tk.StringVar(self, value=self.config.get("admin_center_api_key", ""))
        self.sync_enabled_var = tk.BooleanVar(self, value=bool(self.config.get("sync_enabled", False)))
        self.status_var = tk.StringVar(self, value="Ready.")
        self._build_ui()

    def _build_ui(self):
        frame = ttk.Labelframe(self, text="Groundstate Admin Control Center")
        frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(frame, text="Base URL:").grid(row=0, column=0, sticky="e", padx=5, pady=4)
        ttk.Entry(frame, textvariable=self.base_url_var, width=48).grid(row=0, column=1, sticky="w", padx=5, pady=4)
        ttk.Label(frame, text="API key/token:").grid(row=1, column=0, sticky="e", padx=5, pady=4)
        ttk.Entry(frame, textvariable=self.api_key_var, width=48, show="*").grid(row=1, column=1, sticky="w", padx=5, pady=4)
        ttk.Checkbutton(frame, text="Enable sync mode", variable=self.sync_enabled_var).grid(row=2, column=1, sticky="w", padx=5, pady=4)
        ttk.Button(frame, text="Save Config", command=self._save_config).grid(row=3, column=0, padx=5, pady=8)
        ttk.Button(frame, text="Test Connection", command=self._test_connection).grid(row=3, column=1, sticky="w", padx=5, pady=8)
        ttk.Button(frame, text="Pull Employees", command=self._pull_employees).grid(row=3, column=1, sticky="e", padx=5, pady=8)
        ttk.Label(self, textvariable=self.status_var).pack(anchor="w", padx=12, pady=(0, 8))

        columns = ("admin_id", "name", "email", "department", "status", "result")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=18)
        for c, label, width in [
            ("admin_id", "Admin Center ID", 150),
            ("name", "Name", 180),
            ("email", "Email", 180),
            ("department", "Department", 140),
            ("status", "Status", 80),
            ("result", "Sync result", 180),
        ]:
            self.tree.heading(c, text=label)
            self.tree.column(c, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=8)

    def _client(self):
        return AdminCenterClient(self.base_url_var.get().strip(), self.api_key_var.get().strip())

    def _save_config(self):
        data = {
            "admin_center_base_url": self.base_url_var.get().strip(),
            "admin_center_api_key": self.api_key_var.get().strip(),
            "sync_enabled": self.sync_enabled_var.get(),
        }
        save_local_config(data)
        self.status_var.set("Config saved.")
        log_event(self.db, self.current_user, "ADMIN_CENTER_CONFIG_SAVE", data["admin_center_base_url"])

    def _test_connection(self):
        try:
            result = self._client().health()
            self.status_var.set(f"Connection OK: {result}")
        except AdminCenterError as e:
            messagebox.showerror("Connection failed", str(e))
            self.status_var.set("Connection failed.")

    def _pull_employees(self):
        self.tree.delete(*self.tree.get_children())
        try:
            employees = self._client().get_employees()
        except AdminCenterError as e:
            messagebox.showerror("Sync failed", str(e))
            self.status_var.set("Sync failed.")
            return

        created = 0
        updated = 0
        for payload in employees:
            admin_id = str(payload.get("id") or payload.get("employee_id") or "").strip()
            first = (payload.get("first_name") or "").strip()
            last = (payload.get("last_name") or "").strip()
            email = (payload.get("email") or "").strip() or None
            if not admin_id and not email:
                continue
            emp = None
            if admin_id:
                emp = self.db.query(Employee).filter(Employee.admin_center_employee_id == admin_id).first()
            if not emp and email:
                emp = self.db.query(Employee).filter(Employee.email == email).first()
            result = "Updated"
            if not emp:
                emp = Employee(first_name=first or "Unknown", last_name=last or "Employee")
                self.db.add(emp)
                created += 1
                result = "Created"
            else:
                updated += 1

            emp.admin_center_employee_id = admin_id or emp.admin_center_employee_id
            emp.source_system = "groundstate_admin_center"
            emp.last_synced_at = datetime.utcnow()
            emp.first_name = first or emp.first_name
            emp.last_name = last or emp.last_name
            emp.email = email or emp.email
            emp.phone = payload.get("phone") or emp.phone
            emp.status = payload.get("status") or emp.status or "Active"
            emp.date_of_birth = _parse_date(payload.get("date_of_birth")) or emp.date_of_birth
            emp.address_line1 = payload.get("address_line1") or emp.address_line1
            emp.address_line2 = payload.get("address_line2") or emp.address_line2
            emp.city = payload.get("city") or emp.city
            emp.state = payload.get("state") or emp.state
            emp.postal_code = payload.get("postal_code") or emp.postal_code
            emp.country = payload.get("country") or emp.country

            if not emp.job_detail:
                self.db.add(JobDetail(employee=emp))
                self.db.flush()
            emp.job_detail.department = payload.get("department") or emp.job_detail.department
            emp.job_detail.position_title = payload.get("position") or payload.get("position_title") or emp.job_detail.position_title

            self.tree.insert("", "end", values=(
                emp.admin_center_employee_id or "",
                f"{emp.first_name} {emp.last_name}",
                emp.email or "",
                emp.job_detail.department if emp.job_detail else "",
                emp.status or "",
                result,
            ))

        self.db.commit()
        log_event(self.db, self.current_user, "ADMIN_CENTER_PULL_EMPLOYEES", f"created={created}, updated={updated}")
        self.status_var.set(f"Sync complete. Created {created}; updated {updated}.")
