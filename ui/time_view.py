import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from db.models import Employee, TimeEntry
from core.validators import to_decimal

class TimeView(ttk.Frame):
    def __init__(self, master, db, current_user, restricted_employee_id=None):
        super().__init__(master)
        self.db=db; self.current_user=current_user; self.restricted_employee_id=restricted_employee_id
        self.is_hr=(current_user.role or "").upper() in ("ADMIN","HR")
        self.from_var=tk.StringVar(self); self.to_var=tk.StringVar(self); self.emp_var=tk.StringVar(self,value="(All)"); self.unapproved=tk.BooleanVar(self,value=False)
        self._build(); self.refresh()

    def _build(self):
        bar=ttk.Frame(self); bar.pack(fill="x",padx=8,pady=8)
        ttk.Label(bar,text="From").pack(side="left"); ttk.Entry(bar,textvariable=self.from_var,width=12).pack(side="left",padx=4)
        ttk.Label(bar,text="To").pack(side="left"); ttk.Entry(bar,textvariable=self.to_var,width=12).pack(side="left",padx=4)
        self.emp_combo=None
        if self.is_hr:
            ttk.Label(bar,text="Employee").pack(side="left"); self.emp_combo=ttk.Combobox(bar,textvariable=self.emp_var,state="readonly",width=28); self.emp_combo.pack(side="left",padx=4)
            ttk.Checkbutton(bar,text="Unapproved only",variable=self.unapproved,command=self.refresh).pack(side="left",padx=4)
        ttk.Button(bar,text="Refresh",command=self.refresh).pack(side="right")
        btn=ttk.Frame(self); btn.pack(fill="x",padx=8)
        ttk.Button(btn,text="Add",command=self._add).pack(side="left",padx=4)
        ttk.Button(btn,text="Edit",command=self._edit).pack(side="left",padx=4)
        ttk.Button(btn,text="Delete",command=self._delete).pack(side="left",padx=4)
        if self.is_hr: ttk.Button(btn,text="Approve selected",command=self._approve).pack(side="left",padx=4)
        cols=("id","date","employee","reg","ot","approved","notes")
        self.tree=ttk.Treeview(self,columns=cols,show="headings",height=22)
        for c,l,w in [("id","ID",50),("date","Date",100),("employee","Employee",190),("reg","Reg",70),("ot","OT",70),("approved","Approved",90),("notes","Notes",300)]: self.tree.heading(c,text=l); self.tree.column(c,width=w,anchor="w")
        self.tree.pack(fill="both",expand=True,padx=8,pady=8); self.tree.bind("<Double-1>",lambda e:self._edit())

    def _date(self,v):
        s=v.get().strip(); return date.fromisoformat(s) if s else None
    def _employees(self):
        return self.db.query(Employee).order_by(Employee.first_name,Employee.last_name).all()
    def refresh(self):
        emps=self._employees()
        if self.emp_combo: self.emp_combo["values"]=["(All)"]+[f"{e.first_name} {e.last_name} (ID {e.id})" for e in emps]
        q=self.db.query(TimeEntry).join(Employee)
        if self.restricted_employee_id: q=q.filter(TimeEntry.employee_id==self.restricted_employee_id)
        elif self.is_hr and self.emp_var.get()!="(All)":
            for e in emps:
                if self.emp_var.get()==f"{e.first_name} {e.last_name} (ID {e.id})": q=q.filter(TimeEntry.employee_id==e.id)
        try:
            d=self._date(self.from_var)
            if d: q=q.filter(TimeEntry.work_date>=d)
            d=self._date(self.to_var)
            if d: q=q.filter(TimeEntry.work_date<=d)
        except ValueError: pass
        if self.is_hr and self.unapproved.get(): q=q.filter(TimeEntry.approved==False)
        self.tree.delete(*self.tree.get_children())
        for t in q.order_by(TimeEntry.work_date.desc(),TimeEntry.id.desc()).all():
            emp=t.employee; name=f"{emp.first_name} {emp.last_name} (ID {emp.id})"
            self.tree.insert("", "end", values=(t.id,t.work_date.isoformat(),name,f"{t.hours_regular:.2f}",f"{t.hours_overtime:.2f}","Yes" if t.approved else "No",t.notes or ""))
    def _sel(self):
        s=self.tree.selection(); return int(self.tree.item(s[0],"values")[0]) if s else None
    def _add(self):
        d=TimeEntryDialog(self,self.db,None,self.is_hr,self.restricted_employee_id); self.wait_window(d); self.refresh()
    def _edit(self):
        tid=self._sel()
        if not tid: return
        t=self.db.get(TimeEntry,tid)
        if self.restricted_employee_id and t.employee_id!=self.restricted_employee_id: messagebox.showerror("Denied","Wrong employee."); return
        if not self.is_hr and t.approved: messagebox.showerror("Denied","Approved entries cannot be edited."); return
        d=TimeEntryDialog(self,self.db,tid,self.is_hr,self.restricted_employee_id); self.wait_window(d); self.refresh()
    def _delete(self):
        tid=self._sel()
        if not tid: return
        t=self.db.get(TimeEntry,tid)
        if not self.is_hr and t.approved: messagebox.showerror("Denied","Approved entries cannot be deleted."); return
        if messagebox.askyesno("Delete","Delete entry?"): self.db.delete(t); self.db.commit(); self.refresh()
    def _approve(self):
        for s in self.tree.selection():
            t=self.db.get(TimeEntry,int(self.tree.item(s,"values")[0])); t.approved=True
        self.db.commit(); self.refresh()

class TimeEntryDialog(tk.Toplevel):
    def __init__(self,master,db,entry_id,is_hr,restricted_employee_id):
        super().__init__(master); self.db=db; self.entry_id=entry_id; self.is_hr=is_hr; self.restricted_employee_id=restricted_employee_id
        self.title("Time Entry"); self.transient(master); self.date_var=tk.StringVar(self,value=date.today().isoformat()); self.reg_var=tk.StringVar(self,value="0.00"); self.ot_var=tk.StringVar(self,value="0.00"); self.notes_var=tk.StringVar(self); self.approved_var=tk.BooleanVar(self); self.emp_var=tk.StringVar(self); self.emp_map={}
        self._build()
        if entry_id: self._load()
        self.geometry("430x280+240+160")
    def _build(self):
        f=ttk.Frame(self,padding=10); f.pack(fill="both",expand=True); r=0
        if self.is_hr and not self.restricted_employee_id:
            emps=self.db.query(Employee).order_by(Employee.first_name,Employee.last_name).all(); self.emp_map={f"{e.first_name} {e.last_name} (ID {e.id})":e.id for e in emps}
            ttk.Label(f,text="Employee").grid(row=r,column=0,sticky="e"); ttk.Combobox(f,textvariable=self.emp_var,values=list(self.emp_map.keys()),state="readonly",width=30).grid(row=r,column=1,pady=3); r+=1
        for lab,var in [("Date YYYY-MM-DD",self.date_var),("Regular hours",self.reg_var),("Overtime hours",self.ot_var),("Notes",self.notes_var)]:
            ttk.Label(f,text=lab).grid(row=r,column=0,sticky="e",padx=5,pady=3); ttk.Entry(f,textvariable=var,width=28).grid(row=r,column=1,sticky="w",pady=3); r+=1
        if self.is_hr: ttk.Checkbutton(f,text="Approved",variable=self.approved_var).grid(row=r,column=1,sticky="w"); r+=1
        ttk.Button(f,text="Save",command=self._save).grid(row=r,column=0,pady=8); ttk.Button(f,text="Cancel",command=self.destroy).grid(row=r,column=1,pady=8)
    def _load(self):
        t=self.db.get(TimeEntry,self.entry_id); self.date_var.set(t.work_date.isoformat()); self.reg_var.set(f"{t.hours_regular:.2f}"); self.ot_var.set(f"{t.hours_overtime:.2f}"); self.notes_var.set(t.notes or ""); self.approved_var.set(bool(t.approved))
        if self.is_hr and not self.restricted_employee_id and t.employee: self.emp_var.set(f"{t.employee.first_name} {t.employee.last_name} (ID {t.employee.id})")
    def _save(self):
        emp_id=self.restricted_employee_id or self.emp_map.get(self.emp_var.get())
        if not emp_id: messagebox.showerror("Error","Select employee."); return
        try: d=date.fromisoformat(self.date_var.get().strip()); reg=to_decimal(self.reg_var.get(),minimum=0); ot=to_decimal(self.ot_var.get(),minimum=0)
        except Exception as e: messagebox.showerror("Error",str(e)); return
        t=self.db.get(TimeEntry,self.entry_id) if self.entry_id else TimeEntry()
        if not self.entry_id: self.db.add(t)
        t.employee_id=emp_id; t.work_date=d; t.hours_regular=reg; t.hours_overtime=ot; t.notes=self.notes_var.get().strip() or None
        if self.is_hr: t.approved=self.approved_var.get()
        self.db.commit(); self.destroy()
