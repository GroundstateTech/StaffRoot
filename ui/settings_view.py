import tkinter as tk
from tkinter import ttk, messagebox
from core.config import APP_NAME, APP_VERSION, ensure_local_config, save_local_config


class SettingsView(ttk.Frame):
    def __init__(self, master, db):
        super().__init__(master)
        self.db = db
        config = ensure_local_config()
        self.provider = tk.StringVar(self, value=config.get("identity_provider_name", ""))
        self.url = tk.StringVar(self, value=config.get("identity_base_url", ""))
        self.token = tk.StringVar(self, value=config.get("identity_api_token", ""))
        self.enabled = tk.BooleanVar(self, value=bool(config.get("identity_sync_enabled", False)))
        self._build()

    def _build(self):
        app = ttk.Labelframe(self, text="StaffRoot")
        app.pack(fill="x", padx=10, pady=10)
        ttk.Label(app, text=f"{APP_NAME} v{APP_VERSION}").pack(anchor="w", padx=10, pady=6)
        ttk.Label(app, text="Local accounts and data work without any external service.").pack(anchor="w", padx=10, pady=(0, 8))

        identity = ttk.Labelframe(self, text="Optional Organization Identity")
        identity.pack(fill="x", padx=10, pady=10)
        fields = [("Provider name", self.provider, False), ("Base URL", self.url, False), ("API token", self.token, True)]
        for row, (label, variable, secret) in enumerate(fields):
            ttk.Label(identity, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=4)
            ttk.Entry(identity, textvariable=variable, width=48, show="*" if secret else "").grid(row=row, column=1, sticky="w")
        ttk.Checkbutton(identity, text="Enable optional directory sync", variable=self.enabled).grid(row=3, column=1, sticky="w")
        ttk.Label(identity, text="Leave disabled for normal standalone operation.").grid(row=4, column=1, sticky="w", pady=(2, 6))
        ttk.Button(identity, text="Save", command=self.save).grid(row=5, column=1, sticky="w", pady=8)

    def save(self):
        save_local_config({
            "identity_provider_name": self.provider.get().strip(),
            "identity_base_url": self.url.get().strip(),
            "identity_api_token": self.token.get().strip(),
            "identity_sync_enabled": self.enabled.get(),
        })
        messagebox.showinfo("Saved", "Settings saved. Standalone operation remains available.")
