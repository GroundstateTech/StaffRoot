import os, shutil
from datetime import datetime
from tkinter import ttk, messagebox
from db.session import engine

class BackupView(ttk.Frame):
    def __init__(self,master,db):
        super().__init__(master); self.db=db; self.db_file=os.path.abspath(engine.url.database); self.backup_dir=os.path.join(os.path.dirname(self.db_file),"backups"); os.makedirs(self.backup_dir,exist_ok=True); self._build(); self.refresh()
    def _build(self):
        ttk.Label(self,text=f"Database: {self.db_file}").pack(anchor="w",padx=8,pady=4); ttk.Label(self,text=f"Backups: {self.backup_dir}").pack(anchor="w",padx=8,pady=4)
        b=ttk.Frame(self); b.pack(fill="x",padx=8,pady=8); ttk.Button(b,text="Create Backup",command=self.create).pack(side="left",padx=4); ttk.Button(b,text="Restore Selected",command=self.restore).pack(side="left",padx=4); ttk.Button(b,text="Refresh",command=self.refresh).pack(side="left",padx=4)
        self.tree=ttk.Treeview(self,columns=("file","modified","size"),show="headings",height=20)
        for c,l,w in [("file","File",320),("modified","Modified",180),("size","KB",80)]: self.tree.heading(c,text=l); self.tree.column(c,width=w,anchor="w")
        self.tree.pack(fill="both",expand=True,padx=8,pady=8)
    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for name in sorted(os.listdir(self.backup_dir),reverse=True):
            p=os.path.join(self.backup_dir,name)
            if os.path.isfile(p): self.tree.insert("", "end", values=(name,datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S"),f"{os.path.getsize(p)/1024:.1f}"))
    def create(self):
        if not os.path.exists(self.db_file): messagebox.showerror("Error","Database not found."); return
        dest=os.path.join(self.backup_dir,f"staffroot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"); shutil.copy2(self.db_file,dest); self.refresh(); messagebox.showinfo("Backup",f"Created:\n{dest}")
    def restore(self):
        s=self.tree.selection()
        if not s: return
        src=os.path.join(self.backup_dir,self.tree.item(s[0],"values")[0])
        if messagebox.askyesno("Restore","Overwrite current database? Restart app afterward."): shutil.copy2(src,self.db_file); messagebox.showinfo("Restored","Backup restored. Restart StaffRoot.")
