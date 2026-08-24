import tkinter as tk
from tkinter import ttk
from db.models import Employee

class MyProfileView(ttk.Frame):
    def __init__(self,master,db,employee_id):
        super().__init__(master); self.db=db; self.employee_id=employee_id; self.vars={k:tk.StringVar(self,value="—") for k in ["name","email","phone","status","dob","hire","ssn","addr","emergency","job"]}; self._build(); self.refresh()
    def _build(self):
        f=ttk.Labelframe(self,text="My Profile"); f.pack(fill="x",padx=10,pady=10)
        for i,(lab,key) in enumerate([("Name","name"),("Email","email"),("Phone","phone"),("Status","status"),("DOB","dob"),("Hire Date","hire"),("SSN","ssn"),("Address","addr"),("Emergency","emergency"),("Job","job")]): ttk.Label(f,text=lab+":").grid(row=i,column=0,sticky="e",padx=5,pady=3); ttk.Label(f,textvariable=self.vars[key]).grid(row=i,column=1,sticky="w",padx=5,pady=3)
    def refresh(self):
        if not self.employee_id: return
        e=self.db.get(Employee,self.employee_id)
        if not e: return
        self.vars["name"].set(f"{e.first_name} {e.last_name}"); self.vars["email"].set(e.email or "—"); self.vars["phone"].set(e.phone or "—"); self.vars["status"].set(e.status or "—"); self.vars["dob"].set(e.date_of_birth.isoformat() if e.date_of_birth else "—"); self.vars["hire"].set(e.hire_date.isoformat() if e.hire_date else "—"); self.vars["ssn"].set(f"***-**-{e.ssn_last4}" if e.ssn_last4 else "—"); self.vars["addr"].set(", ".join([x for x in [e.address_line1,e.city,e.state,e.postal_code] if x]) or "—"); self.vars["emergency"].set(f"{e.emergency_contact_name or '—'} / {e.emergency_contact_phone or '—'}"); jd=e.job_detail; self.vars["job"].set(f"{jd.department or ''} — {jd.position_title or ''}" if jd else "—")
