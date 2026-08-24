from tkinter import ttk
from db.models import PayrollItem, PayrollRun, PayPeriod

class MyPaystubsView(ttk.Frame):
    def __init__(self,master,db,employee_id):
        super().__init__(master); self.db=db; self.employee_id=employee_id; self._build(); self.refresh()
    def _build(self):
        ttk.Button(self,text="Refresh",command=self.refresh).pack(anchor="w",padx=8,pady=8)
        self.tree=ttk.Treeview(self,columns=("pay_date","period","reg","ot","gross","taxes","deductions","net"),show="headings",height=24)
        for c,l,w in [("pay_date","Pay Date",100),("period","Period",180),("reg","Reg",70),("ot","OT",70),("gross","Gross",90),("taxes","Taxes",90),("deductions","Deductions",100),("net","Net",90)]: self.tree.heading(c,text=l); self.tree.column(c,width=w,anchor="w")
        self.tree.pack(fill="both",expand=True,padx=8,pady=8)
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        if not self.employee_id: return
        rows=self.db.query(PayrollItem,PayrollRun,PayPeriod).join(PayrollRun,PayrollItem.payroll_run_id==PayrollRun.id).join(PayPeriod,PayrollRun.pay_period_id==PayPeriod.id).filter(PayrollItem.employee_id==self.employee_id).order_by(PayPeriod.pay_date.desc()).all()
        for i,r,p in rows: self.tree.insert("", "end", values=(p.pay_date,f"{p.start_date} → {p.end_date}",f"{i.hours_regular:.2f}",f"{i.hours_overtime:.2f}",f"{i.gross_pay:.2f}",f"{i.taxes:.2f}",f"{i.deductions:.2f}",f"{i.net_pay:.2f}"))
