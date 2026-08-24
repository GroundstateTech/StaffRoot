import tkinter as tk
from tkinter import ttk, messagebox
from db.models import Employee, User
from core.security import hash_password

class UsersView(ttk.Frame):
    def __init__(self,master,db,current_user):
        super().__init__(master); self.db=db; self.current_user=current_user; self._build(); self.refresh()
    def _build(self):
        b=ttk.Frame(self); b.pack(fill="x",padx=8,pady=8)
        ttk.Button(b,text="Add",command=self.add).pack(side="left",padx=4); ttk.Button(b,text="Edit",command=self.edit).pack(side="left",padx=4); ttk.Button(b,text="Reset Password",command=self.reset).pack(side="left",padx=4); ttk.Button(b,text="Delete",command=self.delete).pack(side="left",padx=4)
        self.tree=ttk.Treeview(self,columns=("id","user","role","employee","active"),show="headings",height=22)
        for c,l,w in [("id","ID",50),("user","Username",180),("role","Role",90),("employee","Employee",220),("active","Active",80)]: self.tree.heading(c,text=l); self.tree.column(c,width=w,anchor="w")
        self.tree.pack(fill="both",expand=True,padx=8,pady=8)
    def sel(self):
        s=self.tree.selection(); return int(self.tree.item(s[0],"values")[0]) if s else None
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for u in self.db.query(User).order_by(User.username).all():
            emp=u.employee; self.tree.insert("", "end", values=(u.id,u.username,u.role,f"{emp.first_name} {emp.last_name}" if emp else "", "Yes" if u.is_active else "No"))
    def add(self): d=UserDialog(self,self.db,None); self.wait_window(d); self.refresh()
    def edit(self):
        uid=self.sel()
        if uid: d=UserDialog(self,self.db,uid); self.wait_window(d); self.refresh()
    def reset(self):
        uid=self.sel(); u=self.db.get(User,uid) if uid else None
        if u and messagebox.askyesno("Reset",f"Reset {u.username} password to changeme123?"): u.password_hash=hash_password("changeme123"); self.db.commit()
    def delete(self):
        uid=self.sel(); u=self.db.get(User,uid) if uid else None
        if not u or u.id==self.current_user.id: return
        if messagebox.askyesno("Delete",f"Delete {u.username}?"): self.db.delete(u); self.db.commit(); self.refresh()

class UserDialog(tk.Toplevel):
    def __init__(self,master,db,user_id):
        super().__init__(master); self.db=db; self.user_id=user_id; self.title("User"); self.transient(master); self.username=tk.StringVar(self); self.role=tk.StringVar(self,value="EMPLOYEE"); self.password=tk.StringVar(self); self.emp=tk.StringVar(self,value="(None)"); self.active=tk.BooleanVar(self,value=True); self.map={}; self._build(); self._load() if user_id else None; self.geometry("430x260+250+150")
    def _build(self):
        f=ttk.Frame(self,padding=10); f.pack(fill="both",expand=True)
        for i,(lab,var) in enumerate([("Username",self.username),("Role",self.role),("Password",self.password)]): ttk.Label(f,text=lab).grid(row=i,column=0,sticky="e",padx=5,pady=4); ttk.Entry(f,textvariable=var,width=28,show="*" if lab=="Password" else "").grid(row=i,column=1,sticky="w")
        emps=self.db.query(Employee).order_by(Employee.first_name,Employee.last_name).all(); self.map={f"{e.first_name} {e.last_name} (ID {e.id})":e.id for e in emps}
        ttk.Label(f,text="Employee").grid(row=3,column=0,sticky="e"); ttk.Combobox(f,textvariable=self.emp,values=["(None)"]+list(self.map.keys()),state="readonly",width=30).grid(row=3,column=1,sticky="w")
        ttk.Checkbutton(f,text="Active",variable=self.active).grid(row=4,column=1,sticky="w")
        ttk.Button(f,text="Save",command=self.save).grid(row=5,column=0,pady=10); ttk.Button(f,text="Cancel",command=self.destroy).grid(row=5,column=1,pady=10)
    def _load(self):
        u=self.db.get(User,self.user_id); self.username.set(u.username); self.role.set(u.role); self.active.set(bool(u.is_active))
        if u.employee: self.emp.set(f"{u.employee.first_name} {u.employee.last_name} (ID {u.employee.id})")
    def save(self):
        u=self.db.get(User,self.user_id) if self.user_id else User()
        if not self.user_id: self.db.add(u)
        u.username=self.username.get().strip(); u.role=self.role.get().strip().upper(); u.is_active=self.active.get()
        if self.password.get(): u.password_hash=hash_password(self.password.get())
        u.employee_id=self.map.get(self.emp.get())
        if not u.username or u.role not in ("ADMIN","HR","EMPLOYEE"): messagebox.showerror("Error","Invalid username/role."); return
        if not self.user_id and not self.password.get(): messagebox.showerror("Error","Password required for new user."); return
        self.db.commit(); self.destroy()
