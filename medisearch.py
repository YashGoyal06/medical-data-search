import csv
import random
import webbrowser
import base64
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path
import threading


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
    except Exception:
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
#  PRESCRIPTION EXTRACTION - MULTIPLE OPTIONS
# ─────────────────────────────────────────────

# API OPTIONS with pros/cons
API_OPTIONS = {
    "tesseract_ocr": {
        "name": "Tesseract OCR (LOCAL - FREE)",
        "cost": "FREE",
        "description": "Runs entirely on your computer. No API key needed.",
        "setup": "pip install pytesseract pillow\n(Also install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki)",
    },
    "paddleocr": {
        "name": "PaddleOCR (LOCAL - FREE)",
        "cost": "FREE",
        "description": "Fast, accurate OCR. Works offline. No API key needed.",
        "setup": "pip install paddleocr pillow",
    },
    "easyocr": {
        "name": "EasyOCR (LOCAL - FREE)",
        "cost": "FREE",
        "description": "Multi-language support. Runs on your computer. No API key needed.",
        "setup": "pip install easyocr pillow torch",
    },
    "azure_free": {
        "name": "Azure Computer Vision (FREE TIER)",
        "cost": "FREE (up to 20 requests/min)",
        "description": "5000 free calls/month. Requires Azure account.",
        "setup": "Get free key from: portal.azure.com (create Cognitive Services resource)",
    },
    "aws_rekognition": {
        "name": "AWS Rekognition (FREE TIER)",
        "cost": "FREE (12 months, then $0.001/image)",
        "description": "Excellent accuracy. AWS free tier included.",
        "setup": "Create AWS account + install: pip install boto3",
    },
    "ibm_vision": {
        "name": "IBM Cloud Vision (FREE TIER)",
        "cost": "FREE (up to 250 requests/month)",
        "description": "Good for text extraction from documents.",
        "setup": "Get free key from: cloud.ibm.com",
    },
}


def extract_with_tesseract(image_path: str) -> list[str]:
    """Extract medicine names using Tesseract OCR (runs locally)."""
    try:
        from PIL import Image
        import pytesseract 
    except ImportError:
        raise RuntimeError(
            "Tesseract not installed.\n\n"
            "Install with:\n"
            "1. pip install pytesseract pillow\n"
            "2. Download Tesseract from:\n"
            "   https://github.com/UB-Mannheim/tesseract/wiki\n"
            "3. Run the installer"
        )
    
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        
        if not text.strip():
            return []
        
        # Extract medicine names (one per line, filter empty/short lines)
        medicines = [line.strip(" -•*1234567890.)") for line in text.splitlines()
                    if len(line.strip(" -•*1234567890.)")) > 2]
        return [m for m in medicines if m]
    except Exception as e:
        raise RuntimeError(f"Tesseract error:\n{str(e)}")


def extract_with_paddleocr(image_path: str) -> list[str]:
    """Extract medicine names using PaddleOCR (runs locally)."""
    try:
        from paddleocr import PaddleOCR
    except ImportError:
        raise RuntimeError(
            "PaddleOCR not installed.\n\n"
            "Install with:\n"
            "pip install paddleocr pillow\n\n"
            "First run will download ~500MB of models (one-time)."
        )
    
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, enable_mkldnn=False)
        result = ocr.predict(image_path, det=True, rec=True)
        
        if not result or not result[0]:
            return []
        
        # Extract text from results
        medicines = []
        for line in result:
            for word_info in line:
                text = word_info[1][0]
                text = text.strip(" -•*1234567890.)")
                if len(text) > 2:
                    medicines.append(text)
        
        return medicines
    except Exception as e:
        raise RuntimeError(f"PaddleOCR error:\n{str(e)}")


def extract_with_easyocr(image_path: str) -> list[str]:
    """Extract medicine names using EasyOCR (runs locally)."""
    try:
        import easyocr
    except ImportError:
        raise RuntimeError(
            "EasyOCR not installed.\n\n"
            "Install with:\n"
            "pip install easyocr pillow torch\n\n"
            "First run will download ~200MB of models (one-time)."
        )
    
    try:
        reader = easyocr.Reader(['en'])
        result = reader.readtext(image_path)
        
        if not result:
            return []
        
        medicines = []
        for detection in result:
            text = detection[1]
            confidence = detection[2]
            if confidence > 0.3:  # Filter low confidence
                text = text.strip(" -•*1234567890.)")
                if len(text) > 2:
                    medicines.append(text)
        
        return medicines
    except Exception as e:
        raise RuntimeError(f"EasyOCR error:\n{str(e)}")


def extract_with_azure(image_path: str, api_key: str) -> list[str]:
    """Extract medicine names using Azure Computer Vision (FREE tier)."""
    try:
        import urllib.request
        import urllib.error
        import json
    except ImportError:
        raise RuntimeError("Missing required modules")
    
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Azure endpoint (replace with your region if needed)
        endpoint = "https://YOUR_REGION.api.cognitive.microsoft.com/vision/v3.2/ocr"
        
        req = urllib.request.Request(
            endpoint + "?language=en",
            data=image_data,
            headers={
                "Ocp-Apim-Subscription-Key": api_key,
                "Content-Type": "application/octet-stream"
            },
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        
        medicines = []
        for region in result.get("regions", []):
            for line in region.get("lines", []):
                for word in line.get("words", []):
                    text = word.get("text", "").strip(" -•*1234567890.)")
                    if len(text) > 2:
                        medicines.append(text)
        
        return medicines
    except Exception as e:
        raise RuntimeError(f"Azure error:\n{str(e)}")


def extract_with_aws(image_path: str, aws_access_key: str, aws_secret_key: str) -> list[str]:
    """Extract medicine names using AWS Rekognition (FREE tier for 12 months)."""
    try:
        import boto3
    except ImportError:
        raise RuntimeError(
            "boto3 not installed.\n\n"
            "Install with:\n"
            "pip install boto3"
        )
    
    try:
        client = boto3.client(
            'rekognition',
            region_name='us-east-1',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        response = client.detect_text(Image={'Bytes': image_bytes})
        
        medicines = []
        for detection in response.get('TextDetections', []):
            if detection['Type'] == 'LINE':
                text = detection['DetectedText'].strip(" -•*1234567890.)")
                if len(text) > 2:
                    medicines.append(text)
        
        return medicines
    except Exception as e:
        raise RuntimeError(f"AWS error:\n{str(e)}")


def extract_medicines_from_image(image_path: str, method: str, api_key: str = None) -> list[str]:
    """Main extraction function that delegates to chosen method."""
    
    if method == "tesseract_ocr":
        return extract_with_tesseract(image_path)
    elif method == "paddleocr":
        return extract_with_paddleocr(image_path)
    elif method == "easyocr":
        return extract_with_easyocr(image_path)
    elif method == "azure_free":
        if not api_key:
            raise RuntimeError("Azure API key required")
        return extract_with_azure(image_path, api_key)
    elif method == "aws_rekognition":
        if not api_key:
            raise RuntimeError("AWS credentials required")
        return extract_with_aws(image_path, api_key, api_key)
    elif method == "ibm_vision":
        raise RuntimeError("IBM Vision support coming soon")
    else:
        raise RuntimeError(f"Unknown method: {method}")


# ─────────────────────────────────────────────
#  PRESCRIPTION DIALOG
# ─────────────────────────────────────────────

class PrescriptionDialog(tk.Toplevel):
    """
    Shows extracted medicine names as checkboxes.
    User selects which ones to search and clicks 'Search Selected'.
    """

    def __init__(self, parent, medicines: list[str], theme: dict,
                 on_search_callback):
        super().__init__(parent)
        self.title("📋  Prescription — Select Medicines to Search")
        self.configure(bg=theme["BG"])
        self.resizable(False, False)
        self._t = theme
        self._on_search = on_search_callback
        self._vars = []

        self.transient(parent)
        self.grab_set()

        self._build(medicines)

        # Center on parent
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")

    def _build(self, medicines):
        t = self._t

        # ── Header ──
        hdr = tk.Frame(self, bg=t["PANEL"], pady=14, padx=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📋  Prescription Scan Results",
                 bg=t["PANEL"], fg=t["ACCENT"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")
        tk.Label(hdr,
                 text="Select the medicines you want to look up:",
                 bg=t["PANEL"], fg=t["MUTED"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        tk.Frame(self, bg=t["BORDER"], height=1).pack(fill="x")

        # ── Scrollable checkbox area ──
        container = tk.Frame(self, bg=t["BG"])
        container.pack(fill="both", expand=True, padx=0, pady=0)

        canvas = tk.Canvas(container, bg=t["BG"],
                           highlightthickness=0, bd=0,
                           width=380, height=min(300, len(medicines) * 42 + 20))
        vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=t["BG"])
        win = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win, width=canvas.winfo_width())

        inner.bind("<Configure>", _resize)
        canvas.bind("<Configure>", _resize)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(
                            int(-1 * (e.delta / 120)), "units"))

        if not medicines:
            tk.Label(inner,
                     text="\n⚠️  No medicine names could be extracted.\n"
                          "Try a clearer image.",
                     bg=t["BG"], fg=t["DANGER"],
                     font=("Segoe UI", 11),
                     justify="center").pack(pady=20, padx=20)
        else:
            for i, name in enumerate(medicines):
                var = tk.BooleanVar(value=True)
                self._vars.append((var, name))
                row_bg = t["ROW_EVEN"] if i % 2 == 0 else t["ROW_ODD"]
                row = tk.Frame(inner, bg=row_bg, pady=6, padx=16)
                row.pack(fill="x")

                cb = tk.Checkbutton(
                    row, variable=var,
                    bg=row_bg,
                    activebackground=row_bg,
                    selectcolor=t["PANEL"],
                    fg=t["TEXT"],
                    activeforeground=t["TEXT"],
                    cursor="hand2",
                    highlightthickness=0,
                    bd=0,
                )
                cb.pack(side="left")

                tk.Label(row, text=name,
                         bg=row_bg, fg=t["TEXT"],
                         font=FONT_SMALL,
                         anchor="w").pack(side="left", padx=(4, 0))

        tk.Frame(self, bg=t["BORDER"], height=1).pack(fill="x")

        # ── Buttons ──
        btn_bar = tk.Frame(self, bg=t["BG"], pady=14, padx=20)
        btn_bar.pack(fill="x")

        # Select / Deselect all
        def _toggle_all():
            all_on = all(v.get() for v, _ in self._vars)
            for v, _ in self._vars:
                v.set(not all_on)

        ttk.Button(btn_bar, text="Toggle All",
                   style="Ghost.TButton",
                   command=_toggle_all).pack(side="left")

        ttk.Button(btn_bar, text="Cancel",
                   style="Ghost.TButton",
                   command=self.destroy).pack(side="right", padx=(8, 0))

        ttk.Button(btn_bar, text="  🔍  Search Selected",
                   style="Primary.TButton",
                   command=self._confirm).pack(side="right")

    def _confirm(self):
        selected = [name for var, name in self._vars if var.get()]
        self.destroy()
        if selected:
            self._on_search(selected)


# ─────────────────────────────────────────────
#  MAIN APPLICATION
# ─────────────────────────────────────────────

class MedicineApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MediSearch — Medicine Lookup")
        self.geometry("1200x760")
        self.minsize(950, 620)
        self.resizable(True, True)

        # Active theme
        self._theme_name = "Dark (Default)"
        self._t = THEMES[self._theme_name]

        self.configure(bg=self._t["BG"])

        # State
        self.data = []
        self.file_path   = tk.StringVar(value="No file loaded")
        self.query_var   = tk.StringVar()
        self.max_var     = tk.StringVar(value="10")
        self.status_var  = tk.StringVar(value="Load a CSV file to begin.")
        self._results    = []
        self._shop_assignments = {}
        self._ocr_method = None
        self._api_key    = None

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

        style.configure("Muted.TLabel",
                         background=t["BG"],
                         foreground=t["MUTED"],
                         font=FONT_SMALL)

        style.configure("Accent.TLabel",
                         background=t["BG"],
                         foreground=t["ACCENT"],
                         font=FONT_BOLD)

        style.configure("Title.TLabel",
                         background=t["BG"],
                         foreground=t["TEXT"],
                         font=FONT_TITLE)

        style.configure("Search.TEntry",
                         fieldbackground=t["PANEL"],
                         foreground=t["TEXT"],
                         insertcolor=t["TEXT"],
                         borderwidth=1,
                         relief="solid",
                         padding=(10, 7))
        style.map("Search.TEntry",
                   fieldbackground=[("focus", t["HEADER_BG"])],
                   bordercolor=[("focus", t["ACCENT"])])

        style.configure("Primary.TButton",
                         background=t["ACCENT"],
                         foreground="#ffffff",
                         font=FONT_BOLD,
                         padding=(16, 9),
                         relief="flat")
        style.map("Primary.TButton",
                   background=[("active", t["ACCENT"]), ("pressed", t["ACCENT"])])

        style.configure("Ghost.TButton",
                         background=t["PANEL"],
                         foreground=t["MUTED"],
                         font=FONT_SMALL,
                         padding=(10, 7),
                         relief="flat")
        style.map("Ghost.TButton",
                   background=[("active", t["BORDER"])],
                   foreground=[("active", t["TEXT"])])

        style.configure("Prescription.TButton",
                         background=t["TAG_BG"],
                         foreground=t["ACCENT2"],
                         font=("Segoe UI", 11, "bold"),
                         padding=(12, 8),
                         relief="flat")
        style.map("Prescription.TButton",
                   background=[("active", t["BORDER"])],
                   foreground=[("active", t["TEXT"])])

        style.configure("Theme.TButton",
                         background=t["TAG_BG"],
                         foreground=t["MUTED"],
                         font=("Segoe UI", 10),
                         padding=(10, 5),
                         relief="flat")
        style.map("Theme.TButton",
                   background=[("active", t["BORDER"])],
                   foreground=[("active", t["ACCENT"])])

        style.configure("ActiveTheme.TButton",
                         background=t["ACCENT"],
                         foreground="#ffffff",
                         font=("Segoe UI", 10, "bold"),
                         padding=(10, 5),
                         relief="flat")

        style.configure("Treeview",
                         background=t["ROW_EVEN"],
                         fieldbackground=t["ROW_EVEN"],
                         foreground=t["TEXT"],
                         font=FONT_SMALL,
                         rowheight=40,
                         borderwidth=0)
        style.configure("Treeview.Heading",
                         background=t["HEADER_BG"],
                         foreground=t["MUTED"],
                         font=("Segoe UI", 11, "bold"),
                         relief="flat",
                         padding=(8, 8))
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
                         width=10)
        style.configure("Horizontal.TScrollbar",
                         background=t["BORDER"],
                         troughcolor=t["BG"],
                         arrowcolor=t["MUTED"],
                         borderwidth=0,
                         width=10)

        style.configure("TSpinbox",
                         fieldbackground=t["PANEL"],
                         foreground=t["TEXT"],
                         insertcolor=t["TEXT"],
                         arrowcolor=t["MUTED"],
                         background=t["PANEL"],
                         borderwidth=1,
                         relief="solid",
                         padding=(8, 7))

        style.configure("TSeparator", background=t["BORDER"])

        style.configure("TNotebook",
                         background=t["PANEL"],
                         borderwidth=0,
                         tabmargins=[0, 0, 0, 0])
        style.configure("TNotebook.Tab",
                         background=t["PANEL"],
                         foreground=t["MUTED"],
                         font=FONT_SMALL,
                         padding=(14, 7))
        style.map("TNotebook.Tab",
                   background=[("selected", t["BG"])],
                   foreground=[("selected", t["ACCENT"])])

    # ── UI Layout ───────────────────────────
    def _build_ui(self):
        t = self._t

        # ── Header bar ──
        self._header = tk.Frame(self, bg=t["PANEL"], height=68)
        self._header.pack(fill="x", side="top")
        self._header.pack_propagate(False)

        tk.Label(self._header, text="💊", bg=t["PANEL"], fg=t["ACCENT"],
                 font=("Segoe UI Emoji", 22)).pack(side="left", padx=(20, 6), pady=12)
        tk.Label(self._header, text="MediSearch",
                 bg=t["PANEL"], fg=t["TEXT"], font=FONT_TITLE).pack(side="left", pady=12)
        tk.Label(self._header, text="  Medicine Lookup Tool",
                 bg=t["PANEL"], fg=t["MUTED"], font=("Segoe UI", 13)).pack(side="left", pady=16)

        tk.Label(self._header, text="v2.0", bg=t["TAG_BG"], fg=t["ACCENT"],
                 font=FONT_MONO, padx=8, pady=2).pack(side="right", padx=20, pady=18)

        # ── Theme switcher bar ──
        self._theme_bar = tk.Frame(self, bg=t["BG"], pady=8, padx=20)
        self._theme_bar.pack(fill="x")
        tk.Label(self._theme_bar, text="THEME:", bg=t["BG"], fg=t["MUTED"],
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        self._theme_buttons = {}
        for name in THEMES:
            s = "ActiveTheme.TButton" if name == self._theme_name else "Theme.TButton"
            btn = ttk.Button(self._theme_bar, text=name,
                             style=s,
                             command=lambda n=name: self._switch_theme(n))
            btn.pack(side="left", padx=3)
            self._theme_buttons[name] = btn

        # thin accent line
        self._accent_line = tk.Frame(self, bg=t["ACCENT"], height=2)
        self._accent_line.pack(fill="x")

        # ── Control bar ──
        self._ctrl = tk.Frame(self, bg=t["BG"], pady=16, padx=20)
        self._ctrl.pack(fill="x")

        # File picker
        file_group = tk.Frame(self._ctrl, bg=t["BG"])
        file_group.pack(side="left")
        tk.Label(file_group, text="CSV FILE", bg=t["BG"], fg=t["MUTED"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        file_row = tk.Frame(file_group, bg=t["BG"])
        file_row.pack()
        self._file_label = tk.Label(file_row,
                                     textvariable=self.file_path,
                                     bg=t["PANEL"], fg=t["MUTED"],
                                     font=FONT_MONO,
                                     padx=10, pady=7,
                                     width=30,
                                     anchor="w",
                                     relief="flat")
        self._file_label.pack(side="left")
        ttk.Button(file_row, text="Browse…",
                   style="Ghost.TButton",
                   command=self._browse_file).pack(side="left", padx=(4, 0))

        tk.Frame(self._ctrl, bg=t["BORDER"], width=1).pack(side="left", fill="y", padx=20)

        # Search
        search_group = tk.Frame(self._ctrl, bg=t["BG"])
        search_group.pack(side="left")
        tk.Label(search_group, text="SEARCH", bg=t["BG"], fg=t["MUTED"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        search_row = tk.Frame(search_group, bg=t["BG"])
        search_row.pack()
        self._search_entry = ttk.Entry(search_row,
                                        textvariable=self.query_var,
                                        style="Search.TEntry",
                                        width=28,
                                        font=FONT_LABEL)
        self._search_entry.pack(side="left")
        self._search_entry.bind("<Return>", lambda e: self._do_search())

        tk.Frame(self._ctrl, bg=t["BG"], width=8).pack(side="left")

        # Max results
        max_group = tk.Frame(self._ctrl, bg=t["BG"])
        max_group.pack(side="left")
        tk.Label(max_group, text="MAX RESULTS", bg=t["BG"], fg=t["MUTED"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ttk.Spinbox(max_group,
                    textvariable=self.max_var,
                    from_=1, to=500,
                    width=6,
                    font=FONT_LABEL).pack()

        tk.Frame(self._ctrl, bg=t["BG"], width=12).pack(side="left")

        # Search button
        btn_group = tk.Frame(self._ctrl, bg=t["BG"])
        btn_group.pack(side="left")
        tk.Label(btn_group, text=" ", bg=t["BG"], font=("Segoe UI", 9)).pack()
        ttk.Button(btn_group,
                   text="  🔍  Search",
                   style="Primary.TButton",
                   command=self._do_search).pack()

        # Clear button
        clear_group = tk.Frame(self._ctrl, bg=t["BG"])
        clear_group.pack(side="left", padx=(6, 0))
        tk.Label(clear_group, text=" ", bg=t["BG"], font=("Segoe UI", 9)).pack()
        ttk.Button(clear_group,
                   text="Clear",
                   style="Ghost.TButton",
                   command=self._clear).pack()

        # ── Prescription Upload button (right-aligned) ──
        rx_group = tk.Frame(self._ctrl, bg=t["BG"])
        rx_group.pack(side="right", padx=(0, 4))
        tk.Label(rx_group, text="PRESCRIPTION", bg=t["BG"], fg=t["MUTED"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="center")
        ttk.Button(rx_group,
                   text="  📋  Upload & Scan",
                   style="Prescription.TButton",
                   command=self._upload_prescription).pack()

        # Result count badge
        self._count_label = tk.Label(self._ctrl,
                                      text="",
                                      bg=t["BG"], fg=t["ACCENT2"],
                                      font=FONT_BOLD)
        self._count_label.pack(side="right", padx=10)

        # thin divider
        self._divider1 = tk.Frame(self, bg=t["BORDER"], height=1)
        self._divider1.pack(fill="x")

        # ── Main body ──
        self._body = tk.Frame(self, bg=t["BG"])
        self._body.pack(fill="both", expand=True)

        # Left: results table
        left = tk.Frame(self._body, bg=t["BG"])
        left.pack(side="left", fill="both", expand=True)

        cols_bar = tk.Frame(left, bg=t["BG"], pady=6, padx=14)
        cols_bar.pack(fill="x")
        tk.Label(cols_bar, text="RESULTS", bg=t["BG"], fg=t["MUTED"],
                 font=("Segoe UI", 9, "bold")).pack(side="left")

        tree_frame = tk.Frame(left, bg=t["BG"])
        tree_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        cols = ("name", "composition", "price", "manufacturer")
        self.tree = ttk.Treeview(tree_frame,
                                  columns=cols,
                                  show="headings",
                                  selectmode="browse")

        self.tree.heading("name",         text="Product Name")
        self.tree.heading("composition",  text="Composition")
        self.tree.heading("price",        text="Price")
        self.tree.heading("manufacturer", text="Manufacturer")

        self.tree.column("name",         width=220, anchor="w", stretch=True)
        self.tree.column("composition",  width=220, anchor="w", stretch=True)
        self.tree.column("price",        width=80,  anchor="center", stretch=False)
        self.tree.column("manufacturer", width=150, anchor="w", stretch=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree.tag_configure("odd",  background=t["ROW_ODD"])
        self.tree.tag_configure("even", background=t["ROW_EVEN"])
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Right: detail panel
        self._right_border = tk.Frame(self._body, bg=t["BORDER"], width=1)
        self._right_border.pack(side="left", fill="y")

        self._right = tk.Frame(self._body, bg=t["PANEL"], width=340)
        self._right.pack(side="left", fill="y")
        self._right.pack_propagate(False)

        self._build_detail_panel(self._right)

        # ── Status bar ──
        self._status_border = tk.Frame(self, bg=t["BORDER"], height=1)
        self._status_border.pack(fill="x")
        self._status_bar = tk.Frame(self, bg=t["STATUS_BG"], height=28)
        self._status_bar.pack(fill="x", side="bottom")
        self._status_bar.pack_propagate(False)
        tk.Label(self._status_bar, textvariable=self.status_var,
                 bg=t["STATUS_BG"], fg=t["MUTED"],
                 font=FONT_MONO,
                 anchor="w", padx=14).pack(fill="x", side="left")

    def _build_detail_panel(self, parent):
        t = self._t
        top = tk.Frame(parent, bg=t["PANEL"], pady=14, padx=16)
        top.pack(fill="x")
        tk.Label(top, text="DETAILS", bg=t["PANEL"], fg=t["MUTED"],
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")

        tk.Frame(parent, bg=t["BORDER"], height=1).pack(fill="x")

        canvas = tk.Canvas(parent, bg=t["PANEL"], highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._detail_inner = tk.Frame(canvas, bg=t["PANEL"])
        self._canvas_window = canvas.create_window(
            (0, 0), window=self._detail_inner, anchor="nw")

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
                 text="\n\n\n\nSelect a result\nto see details.",
                 bg=t["PANEL"], fg=t["MUTED"],
                 font=("Segoe UI", 12),
                 justify="center").pack(fill="both", expand=True, pady=40)

    def _show_detail(self, med, shop=None):
        t = self._t
        for w in self._detail_inner.winfo_children():
            w.destroy()

        pad = dict(padx=16, anchor="w")

        def section(label, value):
            tk.Label(self._detail_inner, text=label,
                     bg=t["PANEL"], fg=t["MUTED"],
                     font=("Segoe UI", 9, "bold"), **pad).pack(fill="x", pady=(12, 2))
            val = value.strip() if value else "—"
            tk.Label(self._detail_inner, text=val,
                     bg=t["PANEL"], fg=t["TEXT"],
                     font=FONT_SMALL,
                     wraplength=290,
                     justify="left", **pad).pack(fill="x")
            tk.Frame(self._detail_inner, bg=t["BORDER"], height=1).pack(
                fill="x", padx=16, pady=(10, 0))

        # Medicine name
        tk.Label(self._detail_inner,
                 text=med.get('product_name', '—'),
                 bg=t["PANEL"], fg=t["ACCENT"],
                 font=("Segoe UI", 13, "bold"),
                 wraplength=290,
                 justify="left",
                 padx=16, anchor="w").pack(fill="x", pady=(16, 4))

        # Price badge
        price = med.get('product_price', '—').strip()
        pk = tk.Frame(self._detail_inner, bg=t["PANEL"], padx=16)
        pk.pack(fill="x", pady=(0, 8))
        tk.Label(pk, text=f"Rs. {price}" if price else "Price N/A",
                 bg=t["TAG_BG"], fg=t["ACCENT2"],
                 font=FONT_BOLD,
                 padx=10, pady=3).pack(side="left")

        tk.Frame(self._detail_inner, bg=t["BORDER"], height=1).pack(fill="x", padx=16)

        section("SALT COMPOSITION",  med.get('salt_composition', ''))
        section("MANUFACTURER",      med.get('product_manufactured', ''))
        section("DESCRIPTION",       med.get('medicine_desc', ''))
        section("SIDE EFFECTS",      med.get('side_effects', ''))

        # ── Shop assignment ──
        tk.Label(self._detail_inner, text="AVAILABLE AT",
                 bg=t["PANEL"], fg=t["MUTED"],
                 font=("Segoe UI", 9, "bold"),
                 padx=16, anchor="w").pack(fill="x", pady=(12, 2))

        if shop:
            shop_frame = tk.Frame(self._detail_inner, bg=t["PANEL"], padx=16)
            shop_frame.pack(fill="x", pady=(2, 16))

            tk.Label(shop_frame,
                     text=f"🏪  {shop['name']}",
                     bg=t["PANEL"], fg=t["ACCENT"],
                     font=FONT_BOLD).pack(anchor="w")

            link = tk.Label(shop_frame,
                            text="📍 View on Google Maps",
                            bg=t["PANEL"], fg=t["ACCENT2"],
                            font=FONT_SMALL,
                            cursor="hand2")
            link.pack(anchor="w", pady=(6, 0))
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
        self._populate_tree(results, query)

    def _populate_tree(self, results, label=""):
        """Fill the results treeview with a list of medicine rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._show_empty_detail()

        if not results:
            self.status_var.set(f'No results found for "{label}"')
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
        self.status_var.set(
            f'Found {len(results):,} result(s)' +
            (f' for "{label}"' if label else ''))
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

    # ── Prescription Upload ──────────────────
    def _upload_prescription(self):
        """Open an image file, scan it with chosen OCR method."""
        if not self.data:
            messagebox.showwarning(
                "No CSV loaded",
                "Please load a medicine CSV file before scanning a prescription.")
            return

        # Default to PaddleOCR if not set
        if not self._ocr_method:
            self._ocr_method = "paddleocr"

        # Pick image
        path = filedialog.askopenfilename(
            title="Select prescription image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.webp *.gif"),
                ("All files", "*.*"),
            ])
        if not path:
            return

        # Check if this is first scan (need to download models)
        is_first_scan = self._check_first_scan(self._ocr_method)
        
        if is_first_scan and self._ocr_method in ["paddleocr", "easyocr"]:
            # Show progress dialog for model download
            self._show_download_progress(self._ocr_method, path)
        else:
            # Standard scan without model download
            self._perform_scan(path)

    def _check_first_scan(self, method):
        """Check if models are already downloaded for this method."""
        if method == "paddleocr":
            import os
            paddle_cache = os.path.expanduser("~/.paddleocr")
            return not os.path.exists(paddle_cache)
        elif method == "easyocr":
            import os
            easy_cache = os.path.expanduser("~/.EasyOCR")
            return not os.path.exists(easy_cache)
        return False

    def _show_download_progress(self, method, image_path):
        """Show progress dialog during first-time model download."""
        t = self._t
        
        progress_window = tk.Toplevel(self)
        progress_window.title("Downloading OCR Models")
        progress_window.geometry("400x200")
        progress_window.configure(bg=t["BG"])
        progress_window.resizable(False, False)
        
        progress_window.transient(self)
        progress_window.grab_set()
        
        # Header
        header = tk.Frame(progress_window, bg=t["PANEL"], pady=12, padx=20)
        header.pack(fill="x")
        tk.Label(header, text="⏳ First-Time Setup",
                 bg=t["PANEL"], fg=t["ACCENT"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(header, text=f"Downloading {method.upper()} models (~500MB)…",
                 bg=t["PANEL"], fg=t["MUTED"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))
        
        tk.Frame(progress_window, bg=t["BORDER"], height=1).pack(fill="x")
        
        # Progress info
        content = tk.Frame(progress_window, bg=t["BG"], pady=20, padx=20)
        content.pack(fill="both", expand=True)
        
        tk.Label(content, text="This happens only once per method.",
                 bg=t["BG"], fg=t["MUTED"],
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 16))
        
        # Progress bar
        tk.Label(content, text="Progress:",
                 bg=t["BG"], fg=t["TEXT"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 6))
        
        progress_frame = tk.Frame(content, bg=t["PANEL"], height=20, width=360)
        progress_frame.pack(fill="x", pady=(0, 12))
        progress_frame.pack_propagate(False)
        
        progress_fill = tk.Frame(progress_frame, bg=t["ACCENT"], height=20)
        progress_fill.pack(side="left", fill="y")
        
        progress_label = tk.Label(content, text="Initializing…",
                                   bg=t["BG"], fg=t["ACCENT2"],
                                   font=("Segoe UI", 10, "bold"))
        progress_label.pack(anchor="w")
        
        tk.Label(content, text="Connected to internet?\n"
                             "Do not close this window.",
                 bg=t["BG"], fg=t["MUTED"],
                 font=("Segoe UI", 9),
                 justify="left").pack(anchor="w", pady=(16, 0))
        
        progress_window.update_idletasks()
        
        # Simulate download with progress updates
        import threading
        
        def download_with_progress():
            try:
                # Stage 1: Initialize (20%)
                progress_fill.pack_propagate(False)
                progress_fill.configure(width=int(360 * 0.2))
                progress_label.config(text="20% - Initializing models…")
                progress_window.update()
                self.after(800)
                
                # Stage 2: Download (60%)
                progress_fill.configure(width=int(360 * 0.6))
                progress_label.config(text="60% - Downloading model files…")
                progress_window.update()
                self.after(1600)
                
                # Stage 3: Extracting (90%)
                progress_fill.configure(width=int(360 * 0.9))
                progress_label.config(text="90% - Extracting files…")
                progress_window.update()
                self.after(600)
                
                # Stage 4: Complete (100%)
                progress_fill.configure(width=360)
                progress_label.config(text="100% - Ready to scan!")
                progress_window.update()
                self.after(500)
                
                # Now perform the actual scan
                progress_window.destroy()
                self._perform_scan(image_path)
                
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror(
                    "Download Error",
                    f"Failed during model download:\n{e}")
                self.status_var.set("Download failed.")
        
        # Run download in thread to keep UI responsive
        thread = threading.Thread(target=download_with_progress, daemon=True)
        thread.start()

    def _perform_scan(self, image_path):
        """Perform the actual prescription scan."""
        t = self._t
        
        # Show scanning status
        self.status_var.set("🔍  Scanning prescription image…")
        self.update_idletasks()

        try:
            medicines = extract_medicines_from_image(image_path, self._ocr_method, self._api_key)
        except RuntimeError as e:
            messagebox.showerror(
                "Scan Failed",
                f"Could not extract medicines from the image.\n\nError:\n{e}")
            self.status_var.set("Prescription scan failed.")
            return

        img_name = Path(image_path).name
        count = len(medicines)
        self.status_var.set(
            f"✅  Found {count} medicine(s) in '{img_name}' — choose what to search.")

        # Open dialog; on confirm, do a batch search
        PrescriptionDialog(
            parent=self,
            medicines=medicines,
            theme=self._t,
            on_search_callback=self._search_from_prescription,
        )

    def _search_from_prescription(self, selected_names: list[str]):
        """
        Search the CSV for each selected medicine name and merge all results
        into one combined results list, de-duplicated by product_name.
        """
        try:
            max_r = int(self.max_var.get())
            if max_r <= 0:
                max_r = 10
        except ValueError:
            max_r = 10

        seen_names = set()
        combined = []

        for name in selected_names:
            hits = search_medicine(self.data, name, max_r)
            for med in hits:
                key = med.get('product_name', '').lower()
                if key not in seen_names:
                    seen_names.add(key)
                    combined.append(med)

        label = ", ".join(selected_names[:3])
        if len(selected_names) > 3:
            label += f" +{len(selected_names) - 3} more"

        self._populate_tree(combined, label)

        if combined:
            self.status_var.set(
                f"📋  Prescription search: {len(combined)} result(s) "
                f"for {len(selected_names)} medicine(s) — {label}")
        else:
            self.status_var.set(
                f"📋  No matches found in the database for the scanned medicines.")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = MedicineApp()
    app.mainloop()
