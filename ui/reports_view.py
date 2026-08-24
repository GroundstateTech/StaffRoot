import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from decimal import Decimal
from datetime import date
from db.models import Employee, JobDetail, PayPeriod, PayrollItem, PayrollRun

class ReportsView(ttk.Frame):
    def __init__(self,master,db):
        super().__init__(master); self.db=db; self.from_var=tk.StringVar(self); self.to_var=tk.StringVar(self); self.mode=tk.StringVar(self,value="DEPARTMENT"); self._build()
    def _build(self):
        bar=ttk.Frame(self); bar.pack(fill="x",padx=8,pady=8)
        for lab,var in [("From",self.from_var),("To",self.to_var)]: ttk.Label(bar,text=lab).pack(side="left"); ttk.Entry(bar,textvariable=var,width=12).pack(side="left",padx=4)
        ttk.Radiobutton(bar,text="Department",variable=self.mode,value="DEPARTMENT",command=self.refresh).pack(side="left",padx=6); ttk.Radiobutton(bar,text="Employee",variable=self.mode,value="EMPLOYEE",command=self.refresh).pack(side="left",padx=6)
        ttk.Button(bar,text="Run",command=self.refresh).pack(side="right"); ttk.Button(bar,text="Export CSV",command=self.export).pack(side="right",padx=4)
        self.tree=ttk.Treeview(self,show="headings",height=22); self.tree.pack(fill="both",expand=True,padx=8,pady=8); self._cols()
    def _date(self,s): return date.fromisoformat(s.strip()) if s.strip() else None
    def _cols(self):
        self.tree.delete(*self.tree.get_children())
        cols=("group","gross","net") if self.mode.get()=="DEPARTMENT" else ("employee","department","gross","net")
        self.tree["columns"]=cols
        for c in cols: self.tree.heading(c,text=c.title()); self.tree.column(c,width=180,anchor="w")
    def _rows(self):
        q=self.db.query(PayrollItem,PayrollRun,PayPeriod,Employee,JobDetail).join(PayrollRun,PayrollItem.payroll_run_id==PayrollRun.id).join(PayPeriod,PayrollRun.pay_period_id==PayPeriod.id).join(Employee,PayrollItem.employee_id==Employee.id).join(JobDetail,Employee.id==JobDetail.employee_id,isouter=True)
        try:
            d=self._date(self.from_var.get())
            if d: q=q.filter(PayPeriod.pay_date>=d)
            d=self._date(self.to_var.get())
            if d: q=q.filter(PayPeriod.pay_date<=d)
        except Exception: pass
        return q.all()
    def refresh(self):
        self._cols(); data={}
        for item,run,p,e,jd in self._rows():
            if self.mode.get()=="DEPARTMENT":
                key=jd.department if jd and jd.department else "Unassigned"; data.setdefault(key,[Decimal(0),Decimal(0)]); data[key][0]+=Decimal(item.gross_pay or 0); data[key][1]+=Decimal(item.net_pay or 0)
            else:
                key=e.id; dept=jd.department if jd and jd.department else "Unassigned"; data.setdefault(key,[f"{e.first_name} {e.last_name}",dept,Decimal(0),Decimal(0)]); data[key][2]+=Decimal(item.gross_pay or 0); data[key][3]+=Decimal(item.net_pay or 0)
        for k,v in data.items():
            vals=(k,f"{v[0]:.2f}",f"{v[1]:.2f}") if self.mode.get()=="DEPARTMENT" else (v[0],v[1],f"{v[2]:.2f}",f"{v[3]:.2f}")
            self.tree.insert("", "end", values=vals)
    def export(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if not path: return
        with open(path,"w",newline="",encoding="utf-8") as f:
            wr=csv.writer(f); wr.writerow(self.tree["columns"])
            for i in self.tree.get_children(): wr.writerow(self.tree.item(i,"values"))
        messagebox.showinfo("Exported",f"Saved:\n{path}")
