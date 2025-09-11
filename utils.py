from tkinter import Canvas, Frame, Scrollbar
from datetime import datetime

# === Colors & Fonts ===
BG_COLOUR = "#BAD7E0"
ACCENT = "#369FC2"
HIGHLIGHT_COLOUR = "#29486E"
RED = "#e99090"
AMBER = "#f0c879"
GREEN = "#8ecaaa"
TEXT = "#4b4b4b"
FONT_NAME = "Segoe UI"
FONT = (FONT_NAME, 10)
TITLE_FONT = (FONT_NAME, 12, "bold")

def create_scrollable_frame(parent):
    frame = Frame(parent, bg="white", bd=1, relief="solid")
    frame.pack(pady=10, fill="both", expand=True, padx=25)

    canvas = Canvas(frame, bg="white")
    scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas, bg="white")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_frame_configure)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _on_enter(event):
        canvas.focus_set()

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind("<Enter>", _on_enter)
    canvas.bind("<MouseWheel>", _on_mousewheel)
    canvas.bind("<Destroy>", lambda e: canvas.unbind("<MouseWheel>"))

    return scrollable_frame, canvas

def set_rag_color(label, status):
    colors = {"🔴": RED, "🟡": AMBER, "🟢": GREEN}
    label.config(fg=colors.get(status, "gray"))

def get_current_time_str():
    now = datetime.now()
    return f"{now.day} {now.strftime('%B %Y, %H:%M')}"
