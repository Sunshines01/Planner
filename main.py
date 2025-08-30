import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
from datetime import datetime
from functools import partial
import os

# === Colors & Fonts ===
BG_COLOUR = "#BAD7E0"
ACCENT = "#369FC2"
HIGHLIGHT_COLOUR = "#29486E"
RED = "#e99090"
AMBER = "#f0c879"
GREEN = "#8ecaaa"
TEXT = "#4b4b4b"
FONT_NAME = "Segoe UI"
FONT = ("Segoe UI", 10)
TITLE_FONT = ("Segoe UI", 12, "bold")

tab_frames = {}

# --==-- Default Data --==--
DEFAULT_DATA = {
    "target_date": "2025-06-15",
    "priority": "Complete Python Assignment",
    "priority_rag": "🔴",
    "modules": {
        "Home": [],
        "CS101": [],
        "MATH202": [],
        "PROJECT": []
    },
    "timetable": {}
}

# Generate 24-hour timetable (4am → 3am)
for h in range(24):
    hour = (4 + h) % 24
    DEFAULT_DATA["timetable"][f"{hour:02d}:00"] = ""

# --==-- Load & Save --==--
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as data_file:
             data = json.load(data_file)
        for key, value in DEFAULT_DATA.items():
            if key not in data:
                data[key] = value
        return data
    except FileNotFoundError as exception:
        print("Error loading ", exception)
    return DEFAULT_DATA.copy()

def save_data():
    try:
        with open("data.json", "w", encoding="utf-8") as data_file:
            json.dump(data, data_file, indent=4, ensure_ascii=False)
            #ensure_ascii=False allows non-ascii characters to be written in output - needs utf-8 encoding
    except FileNotFoundError as exception:
        print("Error saving ", exception)

data = load_data()

# --==-- Main Window --==--
window = tk.Tk()
window.title("Planner")
window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}")
window.state("zoomed")
window.config(bg=BG_COLOUR)

# --==-- Style --==--
style = ttk.Style()
style.theme_use('default')
style.configure("TNotebook", background=BG_COLOUR, padding=10)
style.configure("TNotebook.Tab", background=ACCENT, foreground="white", padding=(15, 8), font=(FONT_NAME, 11))
style.map("TNotebook.Tab", background=[('selected', HIGHLIGHT_COLOUR)])

# --==-- Heading --==--
tk.Label(window, text="Planner", font=(FONT_NAME, 20, "bold"), bg=BG_COLOUR, fg=ACCENT).pack(pady=15)

# Frame
heading_frame = tk.Frame(window, bg=BG_COLOUR)
heading_frame.pack(pady=8)

# Date and time
time_label = tk.Label(
    heading_frame,
    font=TITLE_FONT,
    bg=BG_COLOUR,
    fg=ACCENT
)
time_label.pack()

# Subheading
subheading_label = tk.Label(
    heading_frame,
    text="Your Daily Command Center", # Add daily affirmation
    font=FONT,
    bg=BG_COLOUR,
    fg=TEXT
)
subheading_label.pack()

def update_clock():
    now = datetime.now()
    # UK format
    formatted = f"{now.day} {now.strftime('%B %Y, %H:%M')}"
    time_label.config(text=f"📅 {formatted}")
    window.after(60000, update_clock)  # Update every minute

update_clock()

# === Notebook with + Button ===
notebook_frame = tk.Frame(window, bg=BG_COLOUR)
notebook_frame.pack(fill="both", expand=True, padx=20, pady=10)

notebook = ttk.Notebook(notebook_frame)
notebook.pack(side="top", fill="both", expand=True)

# Place + button to the right of tabs
add_tab_button = tk.Label(notebook_frame, text="➕", font=(FONT_NAME, 14, "bold"), bg=ACCENT, fg="white", cursor="hand2", width=3)
add_tab_button.place(relx=1.0, y=10, anchor="ne", x=-10)

def add_new_module():
    name = simpledialog.askstring("New Module", "Enter module name:")
    if name and name.strip():
        name = name.strip()
        if name in data["modules"]:
            messagebox.showwarning("Exists", f"A module named '{name}' already exists!")
            return
        data["modules"][name] = []

        tab = tk.Frame(notebook, bg=BG_COLOUR)
        notebook.add(tab, text=name)
        tab_frames[name] = tab

        # === Add Delete Button ===
        button_frame = tk.Frame(tab, bg=BG_COLOUR)
        button_frame.pack(anchor="ne", padx=20, pady=10)

        delete_button = tk.Button(button_frame, text="🗑️ Delete This Module", command=make_delete_tab_func(name, tab),
                                  bg="lightcoral", fg="white", font=(FONT_NAME, 9, "bold"), relief="flat", width=20,
                                  height=1)
        delete_button.pack()

        create_task_list(tab, data["modules"][name])

        save_data()
        messagebox.showinfo("Success", f"Module '{name}' created!")

add_tab_button.bind("<Button-1>", lambda e: add_new_module())

# --==-- RAG Color Helper --==--
def set_rag_color(label, status):
    if status == "🔴": label.config(fg=RED)
    elif status == "🟡": label.config(fg=AMBER)
    elif status == "🟢": label.config(fg=GREEN)
    else: label.config(fg="gray")

# --==-- Scrollable frame - scrolls when mouse is over it --==--
def create_scrollable_frame(mouse):
    frame = tk.Frame(mouse, bg="white", bd=1, relief="solid")
    frame.pack(pady=10, fill="both", expand=True, padx=25)

    canvas = tk.Canvas(frame, bg="white")
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="white")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_frame_configure)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Scroll only when mouse is over this canvas
    def _on_enter(event):
        canvas.focus_set()

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind("<Enter>", _on_enter)
    canvas.bind("<MouseWheel>", _on_mousewheel)  # For windows

    def _on_destroy(event):
        canvas.unbind("<MouseWheel>")

    canvas.bind("<Destroy>", _on_destroy)

    return scrollable_frame, canvas

# --==-- Timetable Frame --==--
def create_timetable_frame(parent):
    scrollable_frame, canvas = create_scrollable_frame(parent)
    entries = {}

    for h in range(24):
        hour = (4 + h) % 24
        am_pm = "AM" if hour < 12 else "PM"
        if hour == 0: am_pm = "AM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0: display_hour = 12
        time_label = f"{display_hour:02d}:00 {am_pm}"

        row = tk.Frame(scrollable_frame, bg="white")
        row.pack(fill="x", pady=1, padx=5)

        tk.Label(row, text=time_label, width=15, anchor="w", bg="white", font=("Courier", 11, "bold"), fg=ACCENT).pack(side="left")

        saved = data["timetable"].get(f"{hour:02d}:00", "")
        var = tk.StringVar(value=saved)
        entries[f"{hour:02d}:00"] = var

        entry = tk.Entry(row, textvariable=var, font=(FONT_NAME, 11), width=50)
        entry.pack(side="left", padx=10, fill="x", expand=True)

    # Update scroll region after all entries
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    def save_timetable():
        for time_key, var in entries.items():
            data["timetable"][time_key] = var.get().strip()
        save_data()
        messagebox.showinfo("Saved", "Timetable saved! 🌟")

    tk.Button(parent, text="💾 Save All Entries", command=save_timetable, bg=ACCENT, fg="white", font=TITLE_FONT, height=2).pack(pady=15)
    return entries

# --==-- Task List --==--
def create_task_list(parent, task_list):
    scrollable_frame, canvas = create_scrollable_frame(parent)

    def refresh_tasks():
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        for idx, (task, status) in enumerate(task_list):
            row = tk.Frame(scrollable_frame, bg="white")
            row.pack(fill="x", pady=2, padx=10)

            delete_button = tk.Button(row,text="❌",command=partial(delete_task, idx),bg="lightcoral",fg="white",
                                      width=2,font=(FONT_NAME, 8))
            delete_button.pack(side="left", padx=2)

            tk.Label(row, text=task, bg="white", font=(FONT_NAME, 10), anchor="w").pack(side="left", padx=6, fill="x", expand=True)

            rag_label = tk.Label(row, text=status, width=3, font=TITLE_FONT)
            rag_label.pack(side="right", padx=6)
            set_rag_color(rag_label, status)

            def make_click_handler(task_idx):
                def click_handler(event):
                    cycle_rag(task_idx)

                return click_handler

            rag_label.bind("<Button-1>", make_click_handler(idx))

        scrollable_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def delete_task(idx):
        if 0 <= idx < len(task_list):
            del task_list[idx]
            save_data()
            refresh_tasks()

    def cycle_rag(task_idx):
        if 0 <= task_idx < len(task_list):
            task, current_status = task_list[task_idx]
            statuses = ["🔴", "🟡", "🟢", "🔘"]
            if current_status in statuses:
                status_idx = statuses.index(current_status)
                next_idx = (status_idx + 1) % 4
                new_status = statuses[next_idx]
            else:
                new_status = "🔴"
            task_list[task_idx] = (task, new_status)
            save_data()
            refresh_tasks()

    refresh_tasks()

    # --==-- ADD TASK BOX --==--
    input_frame = tk.Frame(parent, bg=BG_COLOUR)
    input_frame.pack(pady=8, padx=25, fill="x")

    tk.Label(input_frame, text="➕ Add New Task", font=TITLE_FONT, bg=BG_COLOUR, fg=TEXT).pack(anchor="w")

    entry = tk.Entry(input_frame, font=(FONT_NAME, 11), relief="solid", bd=2)
    entry.pack(fill="x", pady=4)

    def add_task(event=None):
        text = entry.get().strip()
        if text:
            task_list.append((text, "🔴"))
            entry.delete(0, "end")
            save_data()
            refresh_tasks()
        else:
            messagebox.showwarning("Empty Task", "Please enter a task!")

    entry.bind("<Return>", add_task)

    tk.Button(input_frame, text="➕ Add", command=add_task, bg=ACCENT, fg="white", font=(FONT_NAME, 9, "bold"), width=10
    ).pack(pady=4)

    return refresh_tasks

# --==-- HOME TAB --==--
home_tab = tk.Frame(notebook, bg=BG_COLOUR)
notebook.add(home_tab, text="🏠 Home")
tab_frames["Home"] = home_tab

# Left (Tasks) | Right (Timetable)
split_frame = tk.Frame(home_tab, bg=BG_COLOUR)
split_frame.pack(fill="both", expand=True, padx=15, pady=10)

left_frame = tk.Frame(split_frame, bg=BG_COLOUR, width=500)
left_frame.pack(side="left", fill="both", expand=True)
left_frame.pack_propagate(False)

right_frame = tk.Frame(split_frame, bg=BG_COLOUR, width=500)
right_frame.pack(side="right", fill="both", expand=True)
right_frame.pack_propagate(False)

# --==-- Priority Task --==--
tk.Label(left_frame, text="🎯 Priority Task", font=TITLE_FONT, bg=BG_COLOUR, fg=TEXT).pack(anchor="w", padx=25, pady=(15, 8))

# RAG button on same line
priority_frame = tk.Frame(left_frame, bg=BG_COLOUR)
priority_frame.pack(padx=25, pady=6, fill="x")

priority_var = tk.StringVar(value=data.get("priority", "No priority set"))
priority_entry = tk.Entry(priority_frame, textvariable=priority_var, font=(FONT_NAME, 11), bd=2, relief="solid")
priority_entry.pack(side="left", fill="x", expand=True, ipady=4)

# RAG Status Button
priority_rag = data.get("priority_rag", "🔴")  # Load saved RAG


def cycle_priority_rag(event=None):
    global priority_rag
    statuses = ["🔴", "🟡", "🟢", "🔘"]
    if priority_rag in statuses:
        current_index = statuses.index(priority_rag)
    else:
        current_index = 0
    next_index = (current_index + 1) % 4
    priority_rag = statuses[next_index]
    rag_button.config(text=priority_rag)
    set_rag_color(rag_button, priority_rag)

rag_button = tk.Label(priority_frame, text=priority_rag, font=(FONT_NAME, 14, "bold"), width=3, cursor="hand2", bg="white")
rag_button.pack(side="right", padx=(10, 0))
set_rag_color(rag_button, priority_rag)
rag_button.bind("<Button-1>", cycle_priority_rag)

# --==-- To-Do List --==--
tk.Label(left_frame, text="✅ Today's To-Do List", font=TITLE_FONT, bg=BG_COLOUR, fg=TEXT).pack(anchor="w", padx=25, pady=(10, 8))
create_task_list(left_frame, data["modules"]["Home"])

# --==-- Timetable --==--
tk.Label(right_frame, text="📅 Today's Timetable", font=(FONT_NAME, 14, "bold"), bg=BG_COLOUR, fg=TEXT).pack(anchor="w", padx=25, pady=(10, 10))
create_timetable_frame(right_frame)

# === Load ALL Modules from data.json + Add Delete Button ===
def make_delete_tab_func(tab_name, tab_widget):
    def delete_tab():
        confirm = messagebox.askyesno(
            "Delete Module",
            f"Are you sure you want to delete '{tab_name}'?\n\n"
            "All tasks in this module will be permanently lost.",
            icon="warning"
        )
        if not confirm:
            return

        # Remove from data
        if tab_name in data["modules"]:
            del data["modules"][tab_name]
        save_data()

        # Remove from UI
        notebook.forget(tab_widget)
        del tab_frames[tab_name]

        # Optional: Show hint
        messagebox.showinfo("Deleted", f"Module '{tab_name}' has been deleted.")

    return delete_tab

for name in list(data["modules"].keys()):  # Use list() to avoid modification during iteration
    if name == "Home":
        continue
    if name not in tab_frames:
        tab = tk.Frame(notebook, bg=BG_COLOUR)
        notebook.add(tab, text=name)
        tab_frames[name] = tab

        # --==-- Add Delete Button at Top of Tab --==--
        button_frame = tk.Frame(tab, bg=BG_COLOUR)
        button_frame.pack(anchor="ne", padx=20, pady=10)

        delete_btn = tk.Button(button_frame, text="🗑️ Delete This Module", command=make_delete_tab_func(name, tab), bg="lightcoral",
            fg="white", font=(FONT_NAME, 9, "bold"), relief="flat", width=20, height=1)
        delete_btn.pack()

        # --==-- Task List Below --==--
        create_task_list(tab, data["modules"][name])

# --==-- Auto-Save on Close --==--
def on_closing():
    data["priority"] = priority_var.get().strip()
    data["priority_rag"] = priority_rag
    save_data()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)

try:
    window.mainloop()
except Exception as exception:
    messagebox.showerror("Error", f"App crashed: {exception}")
