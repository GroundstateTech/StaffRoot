from tkinter import ttk
from db.models import AuditLog, User

class AuditLogView(ttk.Frame):
    def __init__(self,master,db):
        super().__init__(master); self.db=db; self._build(); self.refresh()
    def _build(self):
        ttk.Button(self,text="Refresh",command=self.refresh).pack(anchor="w",padx=8,pady=8)
        self.tree=ttk.Treeview(self,columns=("id","time","user","action","details"),show="headings",height=24)
        for c,l,w in [("id","ID",50),("time","Time",160),("user","User",140),("action","Action",180),("details","Details",420)]: self.tree.heading(c,text=l); self.tree.column(c,width=w,anchor="w")
        self.tree.pack(fill="both",expand=True,padx=8,pady=8)
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        rows=self.db.query(AuditLog,User).outerjoin(User,AuditLog.user_id==User.id).order_by(AuditLog.timestamp.desc()).limit(500).all()
        for log,user in rows: self.tree.insert("", "end", values=(log.id,log.timestamp.isoformat(sep=" ",timespec="seconds"),user.username if user else "",log.action,log.details or ""))
