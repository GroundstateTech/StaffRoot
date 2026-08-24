import os
import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import Session

from core.config import APP_ICON, APP_NAME, ensure_local_config
from core.security import hash_password, verify_password
from db.models import AppMeta, User
from db.session import Base, SessionLocal, engine
from ui.main_window import MainWindow

SCHEMA_VERSION = "0.9.7"

def init_db():
    ensure_local_config()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        meta = db.get(AppMeta, "schema_version")
        if not meta:
            db.add(AppMeta(key="schema_version", value=SCHEMA_VERSION))
        elif meta.value != SCHEMA_VERSION:
            meta.value = SCHEMA_VERSION

        if not db.query(User).count():
            db.add(User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="ADMIN",
                is_active=True,
            ))
        db.commit()
    finally:
        db.close()

class LoginFrame(ttk.Frame):
    def __init__(self, master, db_session_factory):
        super().__init__(master)
        self.db_session_factory = db_session_factory
        self.username_var = tk.StringVar(self, value="")
        self.password_var = tk.StringVar(self, value="")
        self._build_ui()

    def _build_ui(self):
        self.pack(fill="both", expand=True)
        container = ttk.Frame(self, padding=24)
        container.place(relx=0.5, rely=0.5, anchor="center")
        ttk.Label(container, text=f"{APP_NAME} — Login", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 14))
        ttk.Label(container, text="Username:").grid(row=1, column=0, sticky="e", padx=5, pady=4)
        user_entry = ttk.Entry(container, textvariable=self.username_var, width=30)
        user_entry.grid(row=1, column=1, pady=4)
        user_entry.focus_set()
        ttk.Label(container, text="Password:").grid(row=2, column=0, sticky="e", padx=5, pady=4)
        pw_entry = ttk.Entry(container, textvariable=self.password_var, width=30, show="*")
        pw_entry.grid(row=2, column=1, pady=4)
        pw_entry.bind("<Return>", lambda e: self._login())
        ttk.Button(container, text="Login", command=self._login).grid(row=3, column=0, columnspan=2, pady=(12, 0))
        ttk.Label(container, text="Default: admin / admin123").grid(row=4, column=0, columnspan=2, pady=(12, 0))

    def reset(self):
        self.username_var.set("")
        self.password_var.set("")

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        db: Session = self.db_session_factory()
        try:
            user = db.query(User).filter(User.username == username, User.is_active == True).first()
            if not user or not verify_password(password, user.password_hash):
                messagebox.showerror("Error", "Invalid username or password.")
                return
        finally:
            db.close()
        self.event_generate("<<LoginSuccess>>", when="tail")

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.db = SessionLocal()
        self.main_window = None
        self.login_frame = LoginFrame(root, SessionLocal)
        self.login_frame.bind("<<LoginSuccess>>", self._handle_login_success)

    def _handle_login_success(self, event=None):
        username = self.login_frame.username_var.get().strip()
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            messagebox.showerror("Error", "User disappeared. Try again.")
            self.login_frame.reset()
            return
        self.login_frame.pack_forget()
        self.root.withdraw()
        self.main_window = MainWindow(self.root, self.db, user, on_logout=self._handle_logout)

    def _handle_logout(self):
        if self.main_window:
            self.main_window.destroy()
            self.main_window = None
        self.login_frame.reset()
        self.login_frame.pack(fill="both", expand=True)
        self.root.deiconify()

def main():
    init_db()
    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("960x640")
    root.configure(bg="#0B0F12")
    try:
        if APP_ICON.exists():
            root.iconbitmap(str(APP_ICON))
    except Exception:
        pass
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
