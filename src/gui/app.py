from __future__ import annotations
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from ..runner import run_review

class App:
    def __init__(self, master: tk.Tk):
        self.master = master
        self.vendor = tk.StringVar(value="Cisco IOS/NX-OS")
        self.out_path = tk.StringVar(value=os.path.abspath("switch_cis_report.pdf"))
        self.status = tk.StringVar(value="Ready.")
        self.files = []
        self._build_ui()

    def _build_ui(self):
        frm = ttk.Frame(self.master, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Vendor profile:").grid(row=0, column=0, sticky="w")
        cb = ttk.Combobox(frm, textvariable=self.vendor, state="readonly",
                          values=["Cisco IOS/NX-OS", "Juniper Junos"])
        cb.grid(row=0, column=1, sticky="we", padx=6)

        ttk.Label(frm, text="Config files:").grid(row=1, column=0, sticky="w", pady=(8,0))
        self.files_lbl = ttk.Label(frm, text="No files selected")
        self.files_lbl.grid(row=1, column=1, sticky="w", padx=6, pady=(8,0))
        ttk.Button(frm, text="Browse", command=self.pick_files).grid(row=1, column=2, sticky="e", pady=(8,0))

        ttk.Label(frm, text="Output PDF:").grid(row=2, column=0, sticky="w", pady=(8,0))
        ttk.Entry(frm, textvariable=self.out_path, width=70).grid(row=2, column=1, sticky="we", padx=6, pady=(8,0))
        ttk.Button(frm, text="Choose", command=self.pick_out).grid(row=2, column=2, sticky="e", pady=(8,0))

        self.progress = ttk.Progressbar(frm, mode="indeterminate")
        self.progress.grid(row=3, column=0, columnspan=3, sticky="we", pady=(10,0))

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10,0))
        ttk.Button(btns, text="Run Review", command=self.run_clicked).pack(side="left")
        ttk.Button(btns, text="Open PDF Location", command=self.open_pdf_location).pack(side="left", padx=8)

        ttk.Label(frm, textvariable=self.status).grid(row=5, column=0, columnspan=3, sticky="w", pady=(8,0))

        self.tree = ttk.Treeview(frm, columns=("id","name","status","fix"), show="headings", height=10)
        for col, width in [("id",130), ("name",560), ("status",90), ("fix",90)]:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=width, anchor="w")
        self.tree.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=(10,0))

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(6, weight=1)

    def pick_files(self):
        types = [("Config files", "*.txt *.cfg *.conf *.config *.set *.*"), ("All files", "*.*")]
        paths = filedialog.askopenfilenames(title="Select config file(s)", filetypes=types)
        if paths:
            self.files = list(paths)
            self.files_lbl.config(text=f"{len(self.files)} file(s) selected")

    def pick_out(self):
        path = filedialog.asksaveasfilename(
            title="Save PDF report as",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        if path:
            self.out_path.set(path)

    def open_pdf_location(self):
        out_pdf = self.out_path.get().strip()
        if not out_pdf:
            messagebox.showwarning("No output path", "Set an output PDF path first.")
            return
        folder = os.path.dirname(os.path.abspath(out_pdf)) or os.getcwd()
        try:
            if os.name == "nt":
                os.startfile(folder)  # type: ignore[attr-defined]
            else:
                import subprocess, sys
                if sys.platform.startswith("darwin"):
                    subprocess.Popen(["open", folder])
                else:
                    subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("Open folder failed", str(e))

    def run_clicked(self):
        if not self.files:
            messagebox.showerror("No config files", "Please select one or more config files to review.")
            return

        vendor = self.vendor.get().strip()
        out_pdf = self.out_path.get().strip()
        if not out_pdf.lower().endswith(".pdf"):
            out_pdf += ".pdf"
            self.out_path.set(out_pdf)

        rules_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "rules",
            "cisco_ios.yml" if vendor.lower().startswith("cisco") else "juniper_junos.yml"
        ))

        self.status.set("Running checks...")
        self.progress.start(10)

        def worker():
            try:
                findings = run_review(vendor, self.files, out_pdf, rules_path)
                def ui():
                    self.tree.delete(*self.tree.get_children())
                    for f in findings:
                        self.tree.insert("", "end", values=(f.issue_id, f.issue_name, f.status, f.fix_type))
                    self.status.set(f"Done. Findings: {len(findings)}. Report: {out_pdf}")
                    messagebox.showinfo("Complete", f"Report generated:\n{out_pdf}")
                self.master.after(0, ui)
            except Exception as e:
                self.master.after(0, lambda: messagebox.showerror("Run failed", str(e)))
                self.master.after(0, lambda: self.status.set("Failed."))
            finally:
                self.master.after(0, lambda: self.progress.stop())

        threading.Thread(target=worker, daemon=True).start()
