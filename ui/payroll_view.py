import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal
from db.models import Employee, PayPeriod, PayrollItem, PayrollRun, TimeEntry

class PayrollView(ttk.Frame):
    def __init__(self,master,db):
        super().__init__(master); self.db=db
        self.start_var=tk.StringVar(self); self.end_var=tk.StringVar(self); self.pay_var=tk.StringVar(self,value=date.today().isoformat())
        self._build(); self.refresh()
    def _build(self):
        f=ttk.Labelframe(self,text="Generate payroll"); f.pack(fill="x",padx=8,pady=8)
        for i,(lab,var) in enumerate([("Start",self.start_var),("End",self.end_var),("Pay date",self.pay_var)]):
            ttk.Label(f,text=f"{lab} YYYY-MM-DD").grid(row=i,column=0,sticky="e",padx=5,pady=3); ttk.Entry(f,textvariable=var,width=14).grid(row=i,column=1,sticky="w")
        ttk.Button(f,text="Generate from approved time",command=self._generate).grid(row=0,column=2,rowspan=3,padx=10)
        cols=("id","period","pay_date","items","net"); self.runs=ttk.Treeview(self,columns=cols,show="headings",height=7)
        for c,l,w in [("id","Run ID",60),("period","Period",220),("pay_date","Pay Date",100),("items","Items",70),("net","Net Total",120)]: self.runs.heading(c,text=l); self.runs.column(c,width=w,anchor="w")
        self.runs.pack(fill="x",padx=8,pady=8); self.runs.bind("<<TreeviewSelect>>",lambda e:self._items())
        cols=("employee","reg","ot","gross","taxes","deductions","net"); self.items=ttk.Treeview(self,columns=cols,show="headings",height=14)
        for c,l,w in [("employee","Employee",220),("reg","Reg",70),("ot","OT",70),("gross","Gross",90),("taxes","Taxes",90),("deductions","Deductions",90),("net","Net",90)]: self.items.heading(c,text=l); self.items.column(c,width=w,anchor="w")
        self.items.pack(fill="both",expand=True,padx=8,pady=8)
    def _d(self,v): return date.fromisoformat(v.get().strip())
    def _generate(self):
        try: start=self._d(self.start_var); end=self._d(self.end_var); pay=self._d(self.pay_var)
        except Exception: messagebox.showerror("Error","Invalid date."); return
        period=PayPeriod(start_date=start,end_date=end,pay_date=pay,description=f"{start} → {end}"); self.db.add(period); self.db.flush()
        run=PayrollRun(pay_period=period,status="DRAFT"); self.db.add(run); self.db.flush()
        entries=self.db.query(TimeEntry).filter(TimeEntry.approved==True,TimeEntry.work_date>=start,TimeEntry.work_date<=end).all()
        buckets={}
        for e in entries:
            buckets.setdefault(e.employee_id,{"reg":Decimal("0"),"ot":Decimal("0")}); buckets[e.employee_id]["reg"]+=Decimal(e.hours_regular or 0); buckets[e.employee_id]["ot"]+=Decimal(e.hours_overtime or 0)
        for emp_id,h in buckets.items():
            emp=self.db.get(Employee,emp_id); jd=emp.job_detail; rate=Decimal(jd.base_rate or 0) if jd else Decimal("0")
            gross=(h["reg"]*rate)+(h["ot"]*rate*Decimal("1.5")); taxes=gross*Decimal("0.20"); ded=gross*Decimal("0.05"); net=gross-taxes-ded
            self.db.add(PayrollItem(run=run,employee=emp,hours_regular=h["reg"],hours_overtime=h["ot"],gross_pay=gross,net_pay=net,taxes=taxes,deductions=ded))
        self.db.commit(); self.refresh(); messagebox.showinfo("Created","Payroll run created.")
    def refresh(self):
        self.runs.delete(*self.runs.get_children()); self.items.delete(*self.items.get_children())
        for run in self.db.query(PayrollRun).order_by(PayrollRun.run_date.desc()).all():
            p=run.pay_period; net=sum(float(i.net_pay or 0) for i in run.items)
            self.runs.insert("", "end", values=(run.id,f"{p.start_date} → {p.end_date}",p.pay_date,len(run.items),f"{net:.2f}"))
    def _sel(self):
        s=self.runs.selection(); return int(self.runs.item(s[0],"values")[0]) if s else None
    def _items(self):
        rid=self._sel(); self.items.delete(*self.items.get_children())
        if not rid: return
        run=self.db.get(PayrollRun,rid)
        for i in run.items:
            e=i.employee; self.items.insert("", "end", values=(f"{e.first_name} {e.last_name}",f"{i.hours_regular:.2f}",f"{i.hours_overtime:.2f}",f"{i.gross_pay:.2f}",f"{i.taxes:.2f}",f"{i.deductions:.2f}",f"{i.net_pay:.2f}"))
