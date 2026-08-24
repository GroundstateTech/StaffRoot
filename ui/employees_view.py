import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from db.models import Employee, JobDetail
from core.validators import validate_email, ssn_last4_valid, to_decimal

class EmployeesView(ttk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        bar = ttk.Frame(self); bar.pack(fill="x", padx=8, pady=8)
        ttk.Button(bar, text="Add", command=self._add).pack(side="left", padx=4)
        ttk.Button(bar, text="Edit", command=self._edit).pack(side="left", padx=4)
        ttk.Button(bar, text="Delete", command=self._delete).pack(side="left", padx=4)
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(side="right", padx=4)
        cols = ("id", "admin_id", "name", "email", "dept", "position", "status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=22)
        for c, l, w in [("id","ID",50),("admin_id","Admin ID",120),("name","Name",180),("email","Email",180),("dept","Dept",120),("position","Position",140),("status","Status",90)]:
            self.tree.heading(c, text=l); self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree.bind("<Double-1>", lambda e: self._edit())

    def _selected_id(self):
        sel = self.tree.selection()
        return int(self.tree.item(sel[0], "values")[0]) if sel else None

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for emp in self.db.query(Employee).order_by(Employee.last_name, Employee.first_name).all():
            jd = emp.job_detail
            self.tree.insert("", "end", values=(emp.id, emp.admin_center_employee_id or "", f"{emp.first_name} {emp.last_name}", emp.email or "", jd.department if jd else "", jd.position_title if jd else "", emp.status or ""))

    def _add(self):
        d = EmployeeDialog(self, self.db, None); self.wait_window(d); self.refresh()

    def _edit(self):
        eid = self._selected_id()
        if eid:
            d = EmployeeDialog(self, self.db, eid); self.wait_window(d); self.refresh()

    def _delete(self):
        eid = self._selected_id()
        if not eid: return
        emp = self.db.get(Employee, eid)
        if emp and messagebox.askyesno("Delete", f"Delete {emp.first_name} {emp.last_name}?"):
            self.db.delete(emp); self.db.commit(); self.refresh()

class EmployeeDialog(tk.Toplevel):
    def __init__(self, master, db, employee_id):
        super().__init__(master)
        self.db = db; self.employee_id = employee_id
        self.title("Edit Employee" if employee_id else "Add Employee")
        self.transient(master); self.resizable(False, False)
        self.vars = {k: tk.StringVar(self, value="") for k in ["first","last","email","phone","dob","hire","status","ssn","addr1","addr2","city","state","postal","country","emer_name","emer_phone","dept","position","emp_type","pay_type","rate","schedule"]}
        self.vars["status"].set("Active"); self.vars["hire"].set(date.today().isoformat()); self.vars["emp_type"].set("Full-time"); self.vars["pay_type"].set("HOURLY"); self.vars["rate"].set("0.00"); self.vars["schedule"].set("Bi-weekly")
        self._build()
        if employee_id: self._load()
        self.geometry("650x560+200+120"); self.focus_set()

    def _row(self, parent, row, label, key):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=3)
        ttk.Entry(parent, textvariable=self.vars[key], width=32).grid(row=row, column=1, sticky="w", padx=5, pady=3)

    def _build(self):
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=10, pady=10)
        tabs = {name: ttk.Frame(nb, padding=10) for name in ["Core", "HR Details", "Job / Pay"]}
        for name, frame in tabs.items(): nb.add(frame, text=name)
        for i, (lab, key) in enumerate([("First name","first"),("Last name","last"),("Email","email"),("Phone","phone"),("Status","status"),("Hire date YYYY-MM-DD","hire")]): self._row(tabs["Core"], i, lab, key)
        for i, (lab, key) in enumerate([("Date of birth YYYY-MM-DD","dob"),("SSN last 4","ssn"),("Address 1","addr1"),("Address 2","addr2"),("City","city"),("State","state"),("Postal","postal"),("Country","country"),("Emergency contact","emer_name"),("Emergency phone","emer_phone")]): self._row(tabs["HR Details"], i, lab, key)
        for i, (lab, key) in enumerate([("Department","dept"),("Position","position"),("Employment type","emp_type"),("Pay type","pay_type"),("Base rate","rate"),("Pay schedule","schedule")]): self._row(tabs["Job / Pay"], i, lab, key)
        btn = ttk.Frame(self); btn.pack(fill="x", pady=8)
        ttk.Button(btn, text="Save", command=self._save).pack(side="right", padx=6)
        ttk.Button(btn, text="Cancel", command=self.destroy).pack(side="right", padx=6)

    def _load(self):
        emp = self.db.get(Employee, self.employee_id); jd = emp.job_detail if emp else None
        if not emp: return
        self.vars["first"].set(emp.first_name); self.vars["last"].set(emp.last_name)
        for attr, key in [("email","email"),("phone","phone"),("status","status"),("ssn_last4","ssn"),("address_line1","addr1"),("address_line2","addr2"),("city","city"),("state","state"),("postal_code","postal"),("country","country"),("emergency_contact_name","emer_name"),("emergency_contact_phone","emer_phone")]:
            self.vars[key].set(getattr(emp, attr) or "")
        self.vars["dob"].set(emp.date_of_birth.isoformat() if emp.date_of_birth else "")
        self.vars["hire"].set(emp.hire_date.isoformat() if emp.hire_date else "")
        if jd:
            for attr, key in [("department","dept"),("position_title","position"),("employment_type","emp_type"),("pay_type","pay_type"),("pay_schedule","schedule")]: self.vars[key].set(getattr(jd, attr) or "")
            self.vars["rate"].set(f"{jd.base_rate:.2f}" if jd.base_rate is not None else "0.00")

    def _date(self, key):
        raw = self.vars[key].get().strip()
        return date.fromisoformat(raw) if raw else None

    def _save(self):
        first = self.vars["first"].get().strip(); last = self.vars["last"].get().strip()
        if not first or not last: messagebox.showerror("Error", "First and last name required."); return
        email = self.vars["email"].get().strip()
        if email and not validate_email(email): messagebox.showerror("Error", "Invalid email."); return
        ssn = self.vars["ssn"].get().strip()
        if ssn and not ssn_last4_valid(ssn): messagebox.showerror("Error", "SSN last 4 must be 4 digits."); return
        emp = self.db.get(Employee, self.employee_id) if self.employee_id else Employee(first_name=first, last_name=last)
        if not self.employee_id: self.db.add(emp)
        emp.first_name = first; emp.last_name = last; emp.email = email or None; emp.phone = self.vars["phone"].get().strip() or None
        emp.status = self.vars["status"].get().strip() or "Active"; emp.ssn_last4 = ssn or None
        try: emp.date_of_birth = self._date("dob"); emp.hire_date = self._date("hire")
        except ValueError: messagebox.showerror("Error", "Invalid date format."); return
        for attr, key in [("address_line1","addr1"),("address_line2","addr2"),("city","city"),("state","state"),("postal_code","postal"),("country","country"),("emergency_contact_name","emer_name"),("emergency_contact_phone","emer_phone")]: setattr(emp, attr, self.vars[key].get().strip() or None)
        jd = emp.job_detail
        if not jd: jd = JobDetail(employee=emp); self.db.add(jd)
        jd.department = self.vars["dept"].get().strip() or None; jd.position_title = self.vars["position"].get().strip() or None
        jd.employment_type = self.vars["emp_type"].get().strip() or "Full-time"; jd.pay_type = self.vars["pay_type"].get().strip() or "HOURLY"
        try: jd.base_rate = to_decimal(self.vars["rate"].get(), minimum=0)
        except ValueError as e: messagebox.showerror("Error", str(e)); return
        jd.pay_schedule = self.vars["schedule"].get().strip() or "Bi-weekly"
        self.db.commit(); self.destroy()
