import tkinter as tk
from tkinter import ttk
from db.models import Employee, TimeEntry, PayrollItem

class DashboardView(ttk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        self.total_emp_var = tk.StringVar(self, value="0")
        self.active_emp_var = tk.StringVar(self, value="0")
        self.pending_time_var = tk.StringVar(self, value="0")
        self.net_total_var = tk.StringVar(self, value="0.00")
        self._build_ui()
        self.refresh()

    def _card(self, row, col, title, var):
        frame = ttk.Labelframe(self, text=title)
        frame.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        ttk.Label(frame, textvariable=var, font=("Segoe UI", 18, "bold")).pack(padx=24, pady=24)

    def _build_ui(self):
        for i in range(2):
            self.columnconfigure(i, weight=1)
        self._card(0, 0, "Total employees", self.total_emp_var)
        self._card(0, 1, "Active employees", self.active_emp_var)
        self._card(1, 0, "Unapproved time", self.pending_time_var)
        self._card(1, 1, "All-time net payroll", self.net_total_var)
        ttk.Button(self, text="Refresh", command=self.refresh).grid(row=2, column=0, columnspan=2, pady=10)

    def refresh(self):
        self.total_emp_var.set(str(self.db.query(Employee).count()))
        self.active_emp_var.set(str(self.db.query(Employee).filter(Employee.status == "Active").count()))
        self.pending_time_var.set(str(self.db.query(TimeEntry).filter(TimeEntry.approved == False).count()))
        total = sum(float(x.net_pay or 0) for x in self.db.query(PayrollItem).all())
        self.net_total_var.set(f"{total:.2f}")
