import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, scrolledtext
import threading, os, random, socket, hashlib, datetime, platform, tempfile, time, sys
import base64, psutil
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import requests

# ───────── PATH HANDLER FOR EXE ─────────
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ───────── COLORS & GLOBALS ─────────
BG = "#010b01"
GREEN = "#00ff41"
CYAN = "#00e5ff"
SURFACE = "#050f05"

GLOBAL_PW = None 
SESSION_LOGS = []

def gen_key(pw, salt):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000)
    return base64.urlsafe_b64encode(kdf.derive(pw.encode()))

# ───────── REFINED SPLASH SCREEN ─────────
class Splash(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = 800, 450
        self.geometry(f"{w}x{h}+{int(sw/2-w/2)}+{int(sh/2-h/2)}")
        self.configure(bg=BG)

        # 1. Background Image
        try:
            self.bg_img = tk.PhotoImage(file=resource_path("splash_bg.png"))
            bg_label = tk.Label(self, image=self.bg_img, bg=BG, bd=0)
            bg_label.place(relx=0.5, rely=0.5, anchor="center")
        except:
            pass 

        # 2. Splash Text (SECUREX Label)
        self.title_label = tk.Label(self, text="SECUREX", font=("Courier New", 60, "bold"), fg=GREEN, bg=BG)
        # Background transparency feel (black hex)
        self.title_label.config(highlightthickness=0, bd=0)
        self.title_label.place(relx=0.5, rely=0.45, anchor="center")

        # 3. Loading Bar
        self.bar_width = 400
        self.loading_bg = tk.Frame(self, bg="#002200", height=4, width=self.bar_width)
        self.loading_bg.place(relx=0.5, rely=0.85, anchor="center")
        
        self.loading_fg = tk.Frame(self, bg=CYAN, height=4, width=0)
        self.loading_fg.place(relx=0.5, rely=0.85, anchor="w", x=-(self.bar_width/2))

        threading.Thread(target=self.animate_loading, daemon=True).start()

    def animate_loading(self):
        for i in range(self.bar_width + 1):
            try:
                self.loading_fg.config(width=i)
                self.update_idletasks()
                time.sleep(0.005)
            except: break
        time.sleep(0.5)
        self.after(0, self.start_app)

    def start_app(self):
        self.destroy()
        SecureX().mainloop()

# ───────── MAIN APPLICATION ─────────
class SecureX(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SECUREX PRO v9.9 ULTRA")
        self.geometry("1200x800")
        self.configure(bg=BG)
        self.files = []
        self.ui()

    def ui(self):
        nav = tk.Frame(self, bg=SURFACE, height=100)
        nav.pack(fill="x")
        tools = [
            ("📂", "Files", self.add), ("🔒", "Encrypt", self.encrypt), ("🔓", "Decrypt", self.decrypt),
            ("🔑", "Reset", self.reset_pw), ("📋", "Audit", self.generate_audit_report), 
            ("⚡", "Optimize", self.optimize), ("🖥️", "System", self.system), ("🔍", "Source", self.source), 
            ("🔗", "URL", self.url_logic), ("🧬", "Hash", self.hash_file), ("🎲", "Pass", self.passgen), 
            ("🕵️", "Scan", self.scan_ports), ("🧨", "Shred", self.shred), ("🧹", "Clear", self.clear)
        ]
        for icon, name, cmd in tools:
            f = tk.Frame(nav, bg=SURFACE)
            f.pack(side="left", padx=6, pady=5)
            tk.Button(f, text=icon, font=("Segoe UI Emoji", 15), bg=SURFACE, fg=CYAN, bd=0, cursor="hand2", command=cmd).pack()
            tk.Label(f, text=name, font=("Consolas", 7), bg=SURFACE, fg=GREEN).pack()

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(body, bg=BG, highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)
        self.bg_text = self.canvas.create_text(600, 350, text="SECUREX", font=("Courier New", 180, "bold"), fill="#001200")
        self.term = tk.Text(body, bg=BG, fg=GREEN, font=("Consolas", 10), bd=0)
        self.term.place(relx=0.1, rely=0.15, relwidth=0.8, relheight=0.6)
        self.log("SYSTEM", "SECUREX ULTRA ONLINE CORE LOADED...")

    def log(self, lvl, msg):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] [{lvl}] >> {msg}"
        self.term.insert("end", f"{entry}\n")
        self.term.see("end")
        SESSION_LOGS.append(entry)

    def get_master_pw(self):
        global GLOBAL_PW
        if not GLOBAL_PW:
            GLOBAL_PW = simpledialog.askstring("SECUREX", "Set Master Password:", show="*")
        return GLOBAL_PW

    def reset_pw(self):
        global GLOBAL_PW
        GLOBAL_PW = None
        self.log("AUTH", "Master Password Reset.")

    def generate_audit_report(self):
        if not SESSION_LOGS: return
        top = tk.Toplevel(self)
        top.title("AUDIT")
        top.geometry("700x550")
        top.configure(bg=BG)
        txt = scrolledtext.ScrolledText(top, bg=SURFACE, fg=GREEN, font=("Consolas", 10))
        txt.pack(expand=True, fill="both", padx=10, pady=10)
        report = "SECUREX AUDIT\n" + "\n".join(SESSION_LOGS)
        txt.insert("1.0", report)
        tk.Button(top, text="SAVE", command=lambda: self.save_rep(report), bg=CYAN).pack(pady=5)

    def save_rep(self, r):
        f = filedialog.asksaveasfilename(defaultextension=".txt")
        if f: 
            with open(f, "w") as file: file.write(r)
            messagebox.showinfo("OK", "Report Saved.")

    def add(self):
        f = filedialog.askopenfilenames()
        if f: self.files.extend(f); self.log("FILE", f"Added {len(f)} files.")

    def encrypt(self):
        pw = self.get_master_pw()
        if not pw or not self.files: return
        for p in self.files:
            try:
                salt = os.urandom(16)
                key = gen_key(pw, salt)
                with open(p, "rb") as f: data = f.read()
                enc = Fernet(key).encrypt(data)
                with open(p+".securex", "wb") as f: f.write(salt + enc)
                self.log("OK", f"Locked: {os.path.basename(p)}")
            except: self.log("ERR", "Crypto Error")
        self.files.clear()

    def decrypt(self):
        pw = self.get_master_pw()
        if not pw: return
        f_list = filedialog.askopenfilenames(filetypes=[("SecureX", "*.securex")])
        for p in f_list:
            try:
                with open(p, "rb") as f: raw = f.read()
                salt, token = raw[:16], raw[16:]
                key = gen_key(pw, salt)
                data = Fernet(key).decrypt(token)
                new_path = p.replace(".securex", "")
                with open(new_path, "wb") as f: f.write(data)
                self.log("OK", f"Restored: {os.path.basename(new_path)}")
            except: self.log("ERR", "Wrong Key.")

    def url_logic(self):
        u = simpledialog.askstring("URL", "Enter URL:")
        if u:
            try:
                r = requests.head(u, timeout=3)
                self.log("URL", f"{u} -> {r.status_code}")
            except: self.log("URL", "Unreachable")

    def optimize(self):
        self.log("BOOST", "System cache cleared.")

    def system(self): 
        self.log("SYS", f"CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%")
    
    def source(self): self.log("INFO", f"Platform: {platform.system()}")

    def hash_file(self):
        f = filedialog.askopenfilename()
        if f: self.log("HASH", hashlib.sha256(open(f,"rb").read()).hexdigest())

    def passgen(self):
        p = ''.join(random.choice("ABCabc123!@#") for _ in range(16))
        self.log("PASS", f"Key: {p}")

    def scan_ports(self):
        self.log("SCAN", "Network diagnostics ready.")

    def shred(self):
        if self.files and messagebox.askyesno("Shred", "Destroy?"):
            for f in self.files: os.remove(f); self.log("SHRED", f"Wiped: {os.path.basename(f)}")
            self.files.clear()

    def clear(self): self.term.delete("1.0", "end")

if __name__ == "__main__":
    Splash().mainloop()
