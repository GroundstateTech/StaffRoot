import tkinter as tk
from tkinter import ttk, messagebox
from core.config import APP_NAME, APP_VERSION, ensure_local_config, save_local_config

class SettingsView(ttk.Frame):
    def __init__(self,master,db):
        super().__init__(master); self.db=db; c=ensure_local_config(); self.url=tk.StringVar(self,value=c.get("admin_center_base_url","")); self.key=tk.StringVar(self,value=c.get("admin_center_api_key","")); self.sync=tk.BooleanVar(self,value=bool(c.get("sync_enabled",False))); self._build()
    def _build(self):
        f=ttk.Labelframe(self,text="StaffRoot"); f.pack(fill="x",padx=10,pady=10)
        ttk.Label(f,text=f"{APP_NAME} v{APP_VERSION}").pack(anchor="w",padx=10,pady=6)
        g=ttk.Labelframe(self,text="Groundstate Admin Control Center"); g.pack(fill="x",padx=10,pady=10)
        for i,(lab,var) in enumerate([("Base URL",self.url),("API Key",self.key)]):
            ttk.Label(g,text=lab).grid(row=i,column=0,sticky="e",padx=5,pady=4); ttk.Entry(g,textvariable=var,width=48,show="*" if lab=="API Key" else "").grid(row=i,column=1,sticky="w")
        ttk.Checkbutton(g,text="Enable sync",variable=self.sync).grid(row=2,column=1,sticky="w")
        ttk.Button(g,text="Save",command=self.save).grid(row=3,column=1,sticky="w",pady=8)
    def save(self):
        save_local_config({"admin_center_base_url":self.url.get().strip(),"admin_center_api_key":self.key.get().strip(),"sync_enabled":self.sync.get()})
        messagebox.showinfo("Saved","Settings saved.")
