import os
import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session

from core.config import APP_ICON, APP_NAME, APP_VERSION
from core.theme import APP_TAGLINE, BLUE, CYAN, CYAN_DEEP, DIVIDER, FONT_HEADER, FONT_SUBHEADER, FONT_UI, MIDNIGHT, PANEL, PANEL_ALT, SURFACE, SURFACE_2, TEXT, TEXT_MUTED
from db.models import Employee, User
from ui.admin_sync_view import AdminSyncView
from ui.audit_view import AuditLogView
from ui.backup_view import BackupView
from ui.dashboard_view import DashboardView
from ui.employees_view import EmployeesView
from ui.my_paystubs_view import MyPaystubsView
from ui.my_profile_view import MyProfileView
from ui.payroll_view import PayrollView
from ui.reports_view import ReportsView
from ui.settings_view import SettingsView
from ui.time_view import TimeView
from ui.users_view import UsersView


class MainWindow(tk.Toplevel):
    def __init__(self, master, db: Session, current_user: User, on_logout=None):
        super().__init__(master)
        self.db = db
        self.current_user = current_user
        self.on_logout = on_logout
        self.nav_buttons = {}
        self.pages = {}
        self.active_page = None

        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1180x760")
        self.minsize(1050, 680)

        try:
            if APP_ICON.exists():
                self.iconbitmap(str(APP_ICON))
        except Exception:
            pass

        self._configure_style()
        self._build_shell()
        self._register_pages()
        self._select_first_page()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.deiconify()
        self.focus_set()

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.configure(bg=MIDNIGHT)
        style.configure(".", font=FONT_UI, background=MIDNIGHT, foreground=TEXT)
        style.configure("TFrame", background=MIDNIGHT)
        style.configure("Shell.TFrame", background=MIDNIGHT)
        style.configure("Topbar.TFrame", background=SURFACE)
        style.configure("Sidebar.TFrame", background=SURFACE)
        style.configure("Content.TFrame", background=MIDNIGHT)
        style.configure("Panel.TFrame", background=SURFACE_2)
        style.configure("TLabel", background=MIDNIGHT, foreground=TEXT)
        style.configure("Muted.TLabel", background=SURFACE, foreground=TEXT_MUTED)
        style.configure("Header.TLabel", background=SURFACE, foreground=TEXT, font=FONT_HEADER)
        style.configure("SubHeader.TLabel", background=MIDNIGHT, foreground=CYAN, font=FONT_SUBHEADER)
        style.configure("Node.TLabel", background=SURFACE, foreground=CYAN)
        style.configure("TButton", padding=(8, 5), background=PANEL, foreground=TEXT, borderwidth=1, focusthickness=1, focuscolor=CYAN)
        style.map("TButton", background=[("active", PANEL_ALT), ("pressed", CYAN_DEEP)], foreground=[("active", TEXT), ("pressed", TEXT)])
        style.configure("Nav.TButton", anchor="w", padding=(14, 10), background=SURFACE, foreground=TEXT_MUTED, borderwidth=0, relief="flat")
        style.map("Nav.TButton", background=[("active", SURFACE_2), ("pressed", PANEL)], foreground=[("active", CYAN), ("pressed", CYAN)])
        style.configure("ActiveNav.TButton", anchor="w", padding=(14, 10), background=PANEL, foreground=CYAN, borderwidth=0, relief="flat")
        style.configure("Treeview", background="#10161A", foreground=TEXT, fieldbackground="#10161A", bordercolor=DIVIDER, rowheight=26)
        style.configure("Treeview.Heading", background=PANEL, foreground=CYAN, relief="flat", font=FONT_SUBHEADER)
        style.map("Treeview", background=[("selected", BLUE)], foreground=[("selected", "#FFFFFF")])
        style.configure("TLabelframe", background=MIDNIGHT, foreground=CYAN, bordercolor=DIVIDER)
        style.configure("TLabelframe.Label", background=MIDNIGHT, foreground=CYAN, font=FONT_SUBHEADER)
        style.configure("TEntry", fieldbackground="#0F1519", foreground=TEXT)
        style.configure("TCombobox", fieldbackground="#0F1519", foreground=TEXT)

    def _build_shell(self):
        self.shell = ttk.Frame(self, style="Shell.TFrame")
        self.shell.pack(fill="both", expand=True)
        self.topbar = ttk.Frame(self.shell, style="Topbar.TFrame", height=64)
        self.topbar.pack(fill="x", side="top")
        self.topbar.pack_propagate(False)

        brand = ttk.Frame(self.topbar, style="Topbar.TFrame")
        brand.pack(side="left", padx=16, pady=8)
        ttk.Label(brand, text=APP_NAME, style="Header.TLabel").pack(anchor="w")
        ttk.Label(brand, text=f"{APP_TAGLINE}  //  v{APP_VERSION}", style="Muted.TLabel").pack(anchor="w")

        right = ttk.Frame(self.topbar, style="Topbar.TFrame")
        right.pack(side="right", padx=16, pady=8)
        ttk.Label(right, text=f"USER: {self.current_user.username}", style="Node.TLabel").pack(anchor="e")
        ttk.Label(right, text=f"ROLE: {self.current_user.role}", style="Muted.TLabel").pack(anchor="e")
        ttk.Button(right, text="Sign out", command=self._sign_out).pack(anchor="e", pady=(4, 0))

        body = ttk.Frame(self.shell, style="Shell.TFrame")
        body.pack(fill="both", expand=True)
        self.sidebar = ttk.Frame(body, style="Sidebar.TFrame", width=230)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)

        nav_header = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        nav_header.pack(fill="x", padx=10, pady=(14, 8))
        ttk.Label(nav_header, text="MODULES", style="Node.TLabel").pack(anchor="w")
        ttk.Label(nav_header, text="Control Center-linked navigation", style="Muted.TLabel").pack(anchor="w", pady=(2, 0))

        self.nav_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        self.nav_frame.pack(fill="both", expand=True, padx=8, pady=8)
        status_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        status_frame.pack(fill="x", side="bottom", padx=10, pady=12)
        ttk.Label(status_frame, text="SYNC MODE", style="Node.TLabel").pack(anchor="w")
        ttk.Label(status_frame, text="Standalone-ready / Control-ready", style="Muted.TLabel", wraplength=190).pack(anchor="w", pady=(2, 0))

        self.content_wrap = ttk.Frame(body, style="Content.TFrame")
        self.content_wrap.pack(fill="both", expand=True, side="left")
        self.page_header = ttk.Frame(self.content_wrap, style="Content.TFrame", height=52)
        self.page_header.pack(fill="x", padx=16, pady=(12, 0))
        self.page_header.pack_propagate(False)
        self.page_title_var = tk.StringVar(self, value="")
        self.page_subtitle_var = tk.StringVar(self, value="")
        ttk.Label(self.page_header, textvariable=self.page_title_var, style="SubHeader.TLabel").pack(anchor="w")
        ttk.Label(self.page_header, textvariable=self.page_subtitle_var, foreground=TEXT_MUTED, background=MIDNIGHT).pack(anchor="w")
        self.content = ttk.Frame(self.content_wrap, style="Content.TFrame")
        self.content.pack(fill="both", expand=True, padx=16, pady=(8, 16))

    def _add_page(self, key, title, subtitle, factory):
        btn = ttk.Button(self.nav_frame, text=f"  {title}", style="Nav.TButton", command=lambda k=key: self.show_page(k))
        btn.pack(fill="x", pady=2)
        self.nav_buttons[key] = btn
        frame = ttk.Frame(self.content, style="Content.TFrame")
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        child = factory(frame)
        child.pack(fill="both", expand=True)
        self.pages[key] = {"title": title, "subtitle": subtitle, "frame": frame, "child": child}

    def _register_pages(self):
        role = (self.current_user.role or "").upper()
        if role in ("ADMIN", "HR"):
            self._add_page("dashboard", "Dashboard", "System overview and workforce signals.", lambda p: DashboardView(p, self.db))
            self._add_page("sync", "Admin Center Sync", "Connect StaffRoot to Groundstate Admin Control Center.", lambda p: AdminSyncView(p, self.db, self.current_user))
            self._add_page("employees", "Employees", "Local HR records linked to master identities.", lambda p: EmployeesView(p, self.db))
            self._add_page("time", "Time & Attendance", "Hours, call-offs, approvals, and timecard review.", lambda p: TimeView(p, self.db, current_user=self.current_user))
            self._add_page("payroll", "Payroll", "Generate payroll runs from approved time.", lambda p: PayrollView(p, self.db))
            self._add_page("reports", "Reports", "Payroll summaries by department and employee.", lambda p: ReportsView(p, self.db))
            self._add_page("settings", "Settings", "StaffRoot configuration and Control Center endpoint.", lambda p: SettingsView(p, self.db))
            self._add_page("users", "Users & Access", "Local users, roles, and employee account linking.", lambda p: UsersView(p, self.db, self.current_user))
            self._add_page("audit", "Audit Log", "Operational activity trail.", lambda p: AuditLogView(p, self.db))
            if role == "ADMIN":
                self._add_page("backup", "Backup & Restore", "Local database protection and rollback.", lambda p: BackupView(p, self.db))
        elif role == "EMPLOYEE":
            emp = self._get_employee_for_user()
            if not emp:
                messagebox.showwarning("Not linked", "This account is not linked to an employee record yet.")
            emp_id = emp.id if emp else None
            self._add_page("profile", "My Profile", "Your StaffRoot employee profile.", lambda p: MyProfileView(p, self.db, emp_id))
            self._add_page("mytime", "My Time", "Your time entries and approval status.", lambda p: TimeView(p, self.db, current_user=self.current_user, restricted_employee_id=emp_id))
            self._add_page("paystubs", "My Paystubs", "Your payroll history.", lambda p: MyPaystubsView(p, self.db, emp_id))

    def _select_first_page(self):
        if self.pages:
            self.show_page(next(iter(self.pages.keys())))

    def show_page(self, key):
        if key not in self.pages:
            return
        for nav_key, btn in self.nav_buttons.items():
            btn.configure(style="ActiveNav.TButton" if nav_key == key else "Nav.TButton")
        page = self.pages[key]
        page["frame"].lift()
        self.page_title_var.set(page["title"].upper())
        self.page_subtitle_var.set(page["subtitle"])
        self.active_page = key
        child = page.get("child")
        if hasattr(child, "refresh"):
            try:
                child.refresh()
            except Exception:
                pass

    def _get_employee_for_user(self):
        if self.current_user.employee_id:
            emp = self.db.get(Employee, self.current_user.employee_id)
            if emp:
                return emp
        if self.current_user.username:
            return self.db.query(Employee).filter(Employee.email == self.current_user.username).first()
        return None

    def _sign_out(self):
        if self.on_logout:
            self.on_logout()
        else:
            self.destroy()

    def _on_close(self):
        try:
            self.master.destroy()
        except Exception:
            self.destroy()
