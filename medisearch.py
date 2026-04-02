import csv
import random
import webbrowser
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# --- NEW IMPORTS FOR AI OCR ---
from google import genai
import PIL.Image
import os
try:
    import config
    my_api_key = config.GEMINI_API_KEY
except ImportError:
    my_api_key = "MISSING_KEY"
client = genai.Client(api_key=my_api_key)
# ─────────────────────────────────────────────
#  DATA LOGIC
# ─────────────────────────────────────────────

def load_data(file_path):
    try:
        data = []
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        return None


def remove_duplicates(data):
    seen = set()
    unique = []
    for row in data:
        name = row.get('product_name', '').lower()
        if name not in seen:
            seen.add(name)
            unique.append(row)
    return unique


def search_medicine(data, query, max_results):
    results = []
    q = query.lower()
    for row in data:
        if (q in row.get('product_name', '').lower() or
                q in row.get('salt_composition', '').lower()):
            results.append(row)
        if len(results) >= max_results:
            break
    return results


# ─────────────────────────────────────────────
#  SHOPS
# ─────────────────────────────────────────────

SHOPS = [
    {"name": "Choudhary Medicals", "url": "https://www.google.com/maps/place/Indore+-+Bhopal+Rd,+Kothri,+Madhya+Pradesh+466114/@23.0851306,76.8084776,13z/data=!4m6!3m5!1s0x397ce9bf40443777:0xfcd3b7d0e5cda0c!8m2!3d23.0851308!4d76.8496815!16s%2Fg%2F11x33slpnp?entry=ttu&g_ep=EgoyMDI2MDMyMy4xIKXMDSoASAFQAw%3D%3D"},
    {"name": "Dwivedi Medicals",   "url": "https://www.google.com/maps/place/23%C2%B004'13.7%22N+76%C2%B050'52.0%22E/@23.0851306,76.8084776,13z/data=!4m4!3m3!8m2!3d23.070468!4d76.84777?entry=ttu&g_ep=EgoyMDI2MDMyMy4xIKXMDSoASAFQAw%3D%3D"},
    {"name": "Mathur Medicals",    "url": "https://www.google.com/maps/place/23%C2%B004'42.8%22N+76%C2%B051'51.6%22E/@23.0851306,76.8084776,13z/data=!4m4!3m3!8m2!3d23.078556!4d76.864324?entry=ttu&g_ep=EgoyMDI2MDMyMy4xIKXMDSoASAFQAw%3D%3D"},
    {"name": "Goyal Medicose",     "url": "https://www.google.com/maps/place/23%C2%B006'52.4%22N+76%C2%B051'22.9%22E/@23.0851306,76.8084776,13z/data=!4m4!3m3!8m2!3d23.114542!4d76.85635?entry=ttu&g_ep=EgoyMDI2MDMyMy4xIKXMDSoASAFQAw%3D%3D"},
    {"name": "Agrawal Medicos",    "url": "https://www.google.com/maps/place/23.076012,76.810279/@23.0851306,76.8084776,13z/data=!4m6!3m5!1s0x0:0x53f433f58a607f09!7e2!8m2!3d23.0760107!4d76.8102801?entry=ttu&g_ep=EgoyMDI2MDMyMy4xIKXMDSoASAFQAw%3D%3D"},
    {"name": "Raskar Medicose",    "url": "https://www.google.com/maps/place/23.030015,76.836254/@23.0908513,76.6987173,11.88z/data=!4m6!3m5!1s0x0:0xa7c5aa2031719a29!7e2!8m2!3d23.0300167!4d76.8362331?entry=ttu&g_ep=EgoyMDI2MDMyMy4xIKXMDSoASAFQAw%3D%3D"},
]


# ─────────────────────────────────────────────
#  COLOUR THEMES
# ─────────────────────────────────────────────

THEMES = {
    "Dark (Default)": {
        "BG":         "#0d1117",
        "PANEL":      "#161b22",
        "BORDER":     "#30363d",
        "ACCENT":     "#58a6ff",
        "ACCENT2":    "#3fb950",
        "TEXT":       "#e6edf3",
        "MUTED":      "#8b949e",
        "DANGER":     "#f85149",
        "TAG_BG":     "#1f2937",
        "ROW_EVEN":   "#161b22",
        "ROW_ODD":    "#0d1117",
        "ROW_SEL":    "#1c3050",
        "HEADER_BG":  "#1c2128",
        "STATUS_BG":  "#0a0e13",
    },
    "Sunset": {
        "BG":         "#1a0a00",
        "PANEL":      "#2a1200",
        "BORDER":     "#5c2e00",
        "ACCENT":     "#ff8c42",
        "ACCENT2":    "#ffcc00",
        "TEXT":       "#fdf0e0",
        "MUTED":      "#b07040",
        "DANGER":     "#ff4444",
        "TAG_BG":     "#3d1f00",
        "ROW_EVEN":   "#2a1200",
        "ROW_ODD":    "#1a0a00",
        "ROW_SEL":    "#5c2e00",
        "HEADER_BG":  "#3d1f00",
        "STATUS_BG":  "#110700",
    },
    "Forest": {
        "BG":         "#071a0e",
        "PANEL":      "#0d2b17",
        "BORDER":     "#1e5c30",
        "ACCENT":     "#4caf78",
        "ACCENT2":    "#a8d8a8",
        "TEXT":       "#e8f5e9",
        "MUTED":      "#6a9c76",
        "DANGER":     "#e57373",
        "TAG_BG":     "#143d20",
        "ROW_EVEN":   "#0d2b17",
        "ROW_ODD":    "#071a0e",
        "ROW_SEL":    "#1e5c30",
        "HEADER_BG":  "#143d20",
        "STATUS_BG":  "#040f08",
    },
    "Ember": {
        "BG":         "#000000",
        "PANEL":      "#0f0f0f",
        "BORDER":     "#CF0A0A",
        "ACCENT":     "#DC5F00",
        "ACCENT2":    "#CF0A0A",
        "TEXT":       "#EEEEEE",
        "MUTED":      "#888888",
        "DANGER":     "#CF0A0A",
        "TAG_BG":     "#1a0000",
        "ROW_EVEN":   "#0f0f0f",
        "ROW_ODD":    "#000000",
        "ROW_SEL":    "#3a0a00",
        "HEADER_BG":  "#1a0000",
        "STATUS_BG":  "#000000",
    },
}

# ─────────────────────────────────────────────
#  FONTS
# ─────────────────────────────────────────────

FONT_TITLE  = ("Segoe UI", 24, "bold")
FONT_LABEL  = ("Segoe UI", 12)
FONT_BOLD   = ("Segoe UI", 12, "bold")
FONT_SMALL  = ("Segoe UI", 11)
FONT_MONO   = ("Consolas", 11)


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────

class MedicineApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediSearch — Medicine Lookup")
        self.geometry("1280x800")
        self.minsize(1000, 650)
        self.resizable(True, True)

        # Active theme
        self._theme_name = "Dark (Default)"
        self._t = THEMES[self._theme_name]

        self.configure(bg=self._t["BG"])

        # State
        self.data = []
        self.file_path = tk.StringVar(value="No file loaded")
        self.query_var = tk.StringVar()
        self.max_var = tk.StringVar(value="10")
        self.status_var = tk.StringVar(value="Ready. Load a CSV file to begin.")
        self._results = []
        self._shop_assignments = {}   # medicine name -> assigned shop (session memory)

        self._build_styles()
        self._build_ui()

    # ── Helpers ─────────────────────────────
    def _c(self, key):
        return self._t[key]

    # ── Styles ──────────────────────────────
    def _build_styles(self):
        t = self._t
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(".",
                         background=t["BG"],
                         foreground=t["TEXT"],
                         font=FONT_LABEL,
                         borderwidth=0,
                         relief="flat")

        style.configure("TFrame", background=t["BG"])
        style.configure("Panel.TFrame", background=t["PANEL"])

        style.configure("TLabel",
                         background=t["BG"],
                         foreground=t["TEXT"],
                         font=FONT_LABEL)

        style.configure("Search.TEntry",
                         fieldbackground=t["BG"],
                         foreground=t["TEXT"],
                         insertcolor=t["TEXT"],
                         borderwidth=1,
                         relief="solid",
                         padding=(10, 8))
        style.map("Search.TEntry",
                   fieldbackground=[("focus", t["HEADER_BG"])],
                   bordercolor=[("focus", t["ACCENT"])])

        style.configure("Primary.TButton",
                         background=t["ACCENT"],
                         foreground="#ffffff",
                         font=FONT_BOLD,
                         padding=(10, 10),
                         relief="flat")
        style.map("Primary.TButton",
                   background=[("active", t["ACCENT"]), ("pressed", t["ACCENT"])])

        style.configure("Ghost.TButton",
                         background=t["BG"],
                         foreground=t["MUTED"],
                         font=FONT_SMALL,
                         padding=(10, 8),
                         relief="flat")
        style.map("Ghost.TButton",
                   background=[("active", t["BORDER"])],
                   foreground=[("active", t["TEXT"])])

        style.configure("Theme.TButton",
                         background=t["TAG_BG"],
                         foreground=t["MUTED"],
                         font=("Segoe UI", 10),
                         padding=(10, 6),
                         relief="flat")
        style.map("Theme.TButton",
                   background=[("active", t["BORDER"])],
                   foreground=[("active", t["ACCENT"])])

        style.configure("ActiveTheme.TButton",
                         background=t["ACCENT"],
                         foreground="#ffffff",
                         font=("Segoe UI", 10, "bold"),
                         padding=(10, 6),
                         relief="flat")

        style.configure("Treeview",
                         background=t["ROW_EVEN"],
                         fieldbackground=t["ROW_EVEN"],
                         foreground=t["TEXT"],
                         font=FONT_SMALL,
                         rowheight=45,
                         borderwidth=0)
        style.configure("Treeview.Heading",
                         background=t["HEADER_BG"],
                         foreground=t["MUTED"],
                         font=("Segoe UI", 11, "bold"),
                         relief="flat",
                         padding=(10, 12))
        style.map("Treeview",
                   background=[("selected", t["ROW_SEL"])],
                   foreground=[("selected", t["TEXT"])])
        style.map("Treeview.Heading",
                   background=[("active", t["BORDER"])])

        style.configure("Vertical.TScrollbar",
                         background=t["BORDER"],
                         troughcolor=t["BG"],
                         arrowcolor=t["MUTED"],
                         borderwidth=0,
                         width=12)
        style.configure("Horizontal.TScrollbar",
                         background=t["BORDER"],
                         troughcolor=t["BG"],
                         arrowcolor=t["MUTED"],
                         borderwidth=0,
                         width=12)

        style.configure("TSpinbox",
                         fieldbackground=t["BG"],
                         foreground=t["TEXT"],
                         insertcolor=t["TEXT"],
                         arrowcolor=t["MUTED"],
                         background=t["BG"],
                         borderwidth=1,
                         relief="solid",
                         padding=(8, 8))

    # ── UI Layout (COMPLETELY REDESIGNED TO SIDEBAR) ───────────────────────────
    def _build_ui(self):
        t = self._t

        # ── SIDEBAR (Left Panel) ──
        self._sidebar = tk.Frame(self, bg=t["PANEL"], width=300)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False) # Keep width fixed

        # Header in Sidebar
        header_frame = tk.Frame(self._sidebar, bg=t["PANEL"])
        header_frame.pack(fill="x", pady=(30, 20), padx=20)
        tk.Label(header_frame, text="💊 MediSearch", bg=t["PANEL"], fg=t["ACCENT"], font=FONT_TITLE).pack(anchor="w")
        tk.Label(header_frame, text="Medicine Lookup Tool v1.0", bg=t["PANEL"], fg=t["MUTED"], font=FONT_SMALL).pack(anchor="w", pady=(2, 0))

        tk.Frame(self._sidebar, bg=t["BORDER"], height=1).pack(fill="x", padx=20, pady=10)

        # File Section
        file_frame = tk.Frame(self._sidebar, bg=t["PANEL"])
        file_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(file_frame, text="1. DATABASE", bg=t["PANEL"], fg=t["TEXT"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        self._file_label = tk.Label(file_frame, textvariable=self.file_path, bg=t["BG"], fg=t["MUTED"], font=FONT_MONO, wraplength=250, anchor="w", justify="left", padx=10, pady=8)
        self._file_label.pack(fill="x", pady=(0, 8))
        
        ttk.Button(file_frame, text="📁 Browse CSV...", style="Ghost.TButton", command=self._browse_file).pack(fill="x")

        tk.Frame(self._sidebar, bg=t["BORDER"], height=1).pack(fill="x", padx=20, pady=15)

        # Search Section
        search_frame = tk.Frame(self._sidebar, bg=t["PANEL"])
        search_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(search_frame, text="2. SEARCH MEDICINE", bg=t["PANEL"], fg=t["TEXT"], font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))

        self._search_entry = ttk.Entry(search_frame, textvariable=self.query_var, style="Search.TEntry", font=FONT_LABEL)
        self._search_entry.pack(fill="x", pady=(0, 8))
        self._search_entry.bind("<Return>", lambda e: self._do_search())

        self._scan_btn = ttk.Button(search_frame, text="📸 Scan Prescription", style="Ghost.TButton", command=self._scan_prescription)
        self._scan_btn.pack(fill="x", pady=(0, 15))

        # Settings Section inside Search
        max_frame = tk.Frame(search_frame, bg=t["PANEL"])
        max_frame.pack(fill="x", pady=(0, 15))
        tk.Label(max_frame, text="Max Results:", bg=t["PANEL"], fg=t["MUTED"], font=FONT_SMALL).pack(side="left")
        ttk.Spinbox(max_frame, textvariable=self.max_var, from_=1, to=500, width=8, font=FONT_LABEL).pack(side="right")

        # Action Buttons
        ttk.Button(search_frame, text="🔍 Search", style="Primary.TButton", command=self._do_search).pack(fill="x", pady=(0, 8))
        ttk.Button(search_frame, text="✖ Clear", style="Ghost.TButton", command=self._clear).pack(fill="x")

        # Theme Switcher (Bottom of Sidebar)
        theme_frame = tk.Frame(self._sidebar, bg=t["PANEL"])
        theme_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        tk.Label(theme_frame, text="THEME", bg=t["PANEL"], fg=t["MUTED"], font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        
        self._theme_buttons = {}
        for name in THEMES:
            s = "ActiveTheme.TButton" if name == self._theme_name else "Theme.TButton"
            btn = ttk.Button(theme_frame, text=name, style=s, command=lambda n=name: self._switch_theme(n))
            btn.pack(fill="x", pady=2)
            self._theme_buttons[name] = btn

        # Divider between Sidebar and Main Content
        tk.Frame(self, bg=t["BORDER"], width=1).pack(side="left", fill="y")

        # ── MAIN CONTENT AREA (Right Panel) ──
        self._main_area = tk.Frame(self, bg=t["BG"])
        self._main_area.pack(side="left", fill="both", expand=True)

        # Top Info Bar
        top_bar = tk.Frame(self._main_area, bg=t["HEADER_BG"], height=50)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        
        tk.Label(top_bar, textvariable=self.status_var, bg=t["HEADER_BG"], fg=t["TEXT"], font=FONT_SMALL).pack(side="left", padx=20)
        self._count_label = tk.Label(top_bar, text="", bg=t["HEADER_BG"], fg=t["ACCENT2"], font=FONT_BOLD)
        self._count_label.pack(side="right", padx=20)

        tk.Frame(self._main_area, bg=t["BORDER"], height=1).pack(fill="x")

        # Body Split (Treeview & Details)
        body_split = tk.Frame(self._main_area, bg=t["BG"])
        body_split.pack(fill="both", expand=True)

        # Details Panel (Right side of Main Area)
        self._right = tk.Frame(body_split, bg=t["PANEL"], width=350)
        self._right.pack(side="right", fill="y")
        self._right.pack_propagate(False)
        tk.Frame(body_split, bg=t["BORDER"], width=1).pack(side="right", fill="y")
        self._build_detail_panel(self._right)

        # Treeview Section (Left side of Main Area)
        tree_container = tk.Frame(body_split, bg=t["BG"])
        tree_container.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        cols = ("name", "composition", "price", "manufacturer")
        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("name",         text="Product Name")
        self.tree.heading("composition",  text="Composition")
        self.tree.heading("price",        text="Price")
        self.tree.heading("manufacturer", text="Manufacturer")

        self.tree.column("name",         width=250, anchor="w", stretch=True)
        self.tree.column("composition",  width=250, anchor="w", stretch=True)
        self.tree.column("price",        width=100, anchor="center", stretch=False)
        self.tree.column("manufacturer", width=180, anchor="w", stretch=True)

        vsb = ttk.Scrollbar(tree_container, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)

        self.tree.tag_configure("odd",  background=t["ROW_ODD"])
        self.tree.tag_configure("even", background=t["ROW_EVEN"])
        self.tree.bind("<<TreeviewSelect>>", self._on_select)


    def _build_detail_panel(self, parent):
        t = self._t
        top = tk.Frame(parent, bg=t["PANEL"], pady=18, padx=20)
        top.pack(fill="x")
        tk.Label(top, text="MEDICINE DETAILS", bg=t["PANEL"], fg=t["TEXT"], font=("Segoe UI", 11, "bold")).pack(anchor="w")

        tk.Frame(parent, bg=t["BORDER"], height=1).pack(fill="x")

        canvas = tk.Canvas(parent, bg=t["PANEL"], highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._detail_inner = tk.Frame(canvas, bg=t["PANEL"])
        self._canvas_window = canvas.create_window((0, 0), window=self._detail_inner, anchor="nw")

        def on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(self._canvas_window, width=canvas.winfo_width())

        self._detail_inner.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", on_configure)

        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1 * (e.delta / 120)), "units"))

        self._show_empty_detail()

    def _show_empty_detail(self):
        t = self._t
        for w in self._detail_inner.winfo_children():
            w.destroy()
        tk.Label(self._detail_inner,
                 text="\n\n\n\n\n🔍\n\nSelect a medicine from the\nlist to view its details.",
                 bg=t["PANEL"], fg=t["MUTED"],
                 font=("Segoe UI", 12),
                 justify="center").pack(fill="both", expand=True, pady=40)

    def _show_detail(self, med, shop=None):
        t = self._t
        for w in self._detail_inner.winfo_children():
            w.destroy()

        pad = dict(padx=20, anchor="w")

        def section(label, value):
            tk.Label(self._detail_inner, text=label,
                     bg=t["PANEL"], fg=t["MUTED"],
                     font=("Segoe UI", 9, "bold"), **pad).pack(fill="x", pady=(15, 4))
            val = value.strip() if value else "—"
            tk.Label(self._detail_inner, text=val,
                     bg=t["PANEL"], fg=t["TEXT"],
                     font=FONT_SMALL,
                     wraplength=290,
                     justify="left", **pad).pack(fill="x")
            tk.Frame(self._detail_inner, bg=t["BORDER"], height=1).pack(
                fill="x", padx=20, pady=(12, 0))

        # Medicine name
        tk.Label(self._detail_inner,
                 text=med.get('product_name', '—'),
                 bg=t["PANEL"], fg=t["ACCENT"],
                 font=("Segoe UI", 16, "bold"),
                 wraplength=290,
                 justify="left",
                 padx=20, anchor="w").pack(fill="x", pady=(20, 8))

        # Price badge
        price = med.get('product_price', '—').strip()
        pk = tk.Frame(self._detail_inner, bg=t["PANEL"], padx=20)
        pk.pack(fill="x", pady=(0, 12))
        tk.Label(pk, text=f"Rs. {price}" if price else "Price N/A",
                 bg=t["TAG_BG"], fg=t["ACCENT2"],
                 font=FONT_BOLD,
                 padx=12, pady=6).pack(side="left")

        tk.Frame(self._detail_inner, bg=t["BORDER"], height=1).pack(fill="x", padx=20)

        section("SALT COMPOSITION",  med.get('salt_composition', ''))
        section("MANUFACTURER",      med.get('product_manufactured', ''))
        section("DESCRIPTION",       med.get('medicine_desc', ''))
        section("SIDE EFFECTS",      med.get('side_effects', ''))

        # ── Shop assignment ──
        tk.Label(self._detail_inner, text="AVAILABLE AT",
                 bg=t["PANEL"], fg=t["MUTED"],
                 font=("Segoe UI", 9, "bold"),
                 padx=20, anchor="w").pack(fill="x", pady=(15, 4))

        if shop:
            shop_frame = tk.Frame(self._detail_inner, bg=t["PANEL"], padx=20)
            shop_frame.pack(fill="x", pady=(2, 20))

            tk.Label(shop_frame,
                     text=f"🏪  {shop['name']}",
                     bg=t["PANEL"], fg=t["TEXT"],
                     font=FONT_BOLD).pack(anchor="w")

            link = tk.Label(shop_frame,
                            text="📍 View on Google Maps",
                            bg=t["PANEL"], fg=t["ACCENT"],
                            font=FONT_SMALL,
                            cursor="hand2")
            link.pack(anchor="w", pady=(8, 0))
            link.bind("<Button-1>", lambda e, url=shop['url']: webbrowser.open(url))

    # ── Theme Switching ──────────────────────
    def _switch_theme(self, name):
        if name == self._theme_name:
            return
        self._theme_name = name
        self._t = THEMES[name]
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(bg=self._t["BG"])
        self._build_styles()
        self._build_ui()
        self.status_var.set("Theme changed to: " + name)

    # ── Actions ─────────────────────────────
    
    # --- NEW MULTI-THREADED SCANNER ---
    def _scan_prescription(self):
        # FIXED: Mac-compatible filetypes format
        path = filedialog.askopenfilename(
            title="Select Prescription Image",
            filetypes=[
                ("PNG Images", "*.png"),
                ("JPEG Images", "*.jpg"),
                ("JPEG Images", "*.jpeg"),
                ("All files", "*.*")
            ]
        )
        if not path:
            return

        # Update UI to show we are working
        self.status_var.set("Scanning prescription with AI... Please wait.")
        self._scan_btn.config(state="disabled") # Prevent double-clicking
        self.update_idletasks()

        # Start a background thread to prevent Tkinter from freezing
        threading.Thread(target=self._process_scan_thread, args=(path,), daemon=True).start()

    def _process_scan_thread(self, path):
        """This runs in the background so the UI doesn't freeze"""
        try:
            img = PIL.Image.open(path)
            prompt = "Read this handwritten prescription. Extract ONLY the name of the primary medicine. Do not include dosages, instructions, or any extra text. Just the medicine name."
            
            # Using the new Google GenAI SDK syntax
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt, img]
            )
            med_name = response.text.strip()
            
            # Use 'self.after' to safely send the result back to the main UI thread
            self.after(0, self._on_scan_complete, med_name, None)

        except Exception as e:
            # Send error back to main thread
            self.after(0, self._on_scan_complete, None, str(e))

    def _on_scan_complete(self, med_name, error_msg):
        """This runs back on the main UI thread to update the screen"""
        self._scan_btn.config(state="normal") # Re-enable the button
        
        if error_msg:
            messagebox.showerror("OCR Error", f"An error occurred:\n{error_msg}")
            self.status_var.set("OCR Error.")
            return

        if med_name:
            self.query_var.set(med_name)
            self.status_var.set(f"Extracted from image: {med_name}")
            self._do_search()
        else:
            messagebox.showinfo("OCR Result", "Could not confidently detect a medicine name.")
            self.status_var.set("OCR failed to find medicine.")

    def _browse_file(self):
        path = filedialog.askopenfilename(
            title="Select medicine CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not path:
            return

        data = load_data(path)
        if data is None:
            messagebox.showerror("Error", f"Could not load file:\n{path}")
            return

        data = remove_duplicates(data)
        self.data = data
        short = Path(path).name
        self.file_path.set(short)
        self._file_label.config(fg=self._t["ACCENT2"])
        self.status_var.set(
            f"Loaded {len(self.data):,} unique records from {short}")
        self._count_label.config(text="")

    def _do_search(self):
        if not self.data:
            messagebox.showwarning("No data", "Please load a CSV file first.")
            return

        query = self.query_var.get().strip()
        if not query:
            messagebox.showwarning("Empty query",
                                   "Please enter a medicine name or composition.")
            return

        try:
            max_r = int(self.max_var.get())
            if max_r <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid input",
                                   "Max results must be a positive integer.")
            return

        results = search_medicine(self.data, query, max_r)

        for item in self.tree.get_children():
            self.tree.delete(item)

        self._show_empty_detail()

        if not results:
            self.status_var.set(f'No results found for "{query}"')
            self._count_label.config(text="0 results")
            return

        for i, med in enumerate(results):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end",
                              iid=str(i),
                              tags=(tag,),
                              values=(
                                  med.get('product_name', '—'),
                                  med.get('salt_composition', '—'),
                                  med.get('product_price', '—'),
                                  med.get('product_manufactured', '—'),
                              ))

        self._results = results
        self.status_var.set(f'Found {len(results):,} result(s) for "{query}"')
        self._count_label.config(text=f"{len(results)} result(s)")

    def _clear(self):
        self.query_var.set("")
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._show_empty_detail()
        self._count_label.config(text="")
        self.status_var.set("Search cleared.")
        self._search_entry.focus()

    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        med = self._results[idx]

        # Assign a random shop once per session per medicine name
        med_key = med.get('product_name', str(idx))
        if med_key not in self._shop_assignments:
            self._shop_assignments[med_key] = random.choice(SHOPS)

        self._show_detail(med, self._shop_assignments[med_key])


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = MedicineApp()
    app.mainloop()
