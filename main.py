import tkinter as tk
from tkinter import messagebox, simpledialog
import datetime
import json
import os

# --==-- CONSTANTS --==--
GREEN = "#9bdeac"
PINK = "#e2979c"
RED = "#e7305b"
YELLOW = "#f7f5dd"
DARK_GRAY = "#222222"
LIGHT_GRAY = "#333333"
FONT_NAME = "Helvetica"
DATA_FILE = "data.json"

# --==-- LOAD & SAVE DATA --==--
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            d = json.load(f)
        defaults = {
            "target_date": "2025-06-15",
            "todos": [],
            "wake_time": "09:00"
        }
        for k, v in defaults.items():
            if k not in d:
                d[k] = v
        return d
    return defaults

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

data = load_data()


# --==-- CENTER WINDOW ON SCREEN --==--
def center_window(window, width, height):
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')


# --==-- DAYS UNTIL COUNTER --==--
def days_until(target_str):
    try:
        target = datetime.datetime.strptime(target_str, "%Y-%m-%d")
        today = datetime.datetime.now()
        delta = target - today
        return delta.days
    except Exception:
        return "???"

def update_counter():
    days = days_until(data["target_date"])
    header.config(text=f" {days} days until {data['target_date']}")


# --==-- DAILY SCHEDULE GENERATOR --==--
def generate_schedule(wake_time_str, sleep_hours=7.5):
    try:
        hrs, mins = map(int, wake_time_str.split(":"))
        cwt_min = hrs * 60 + mins
        hour_days = 24 - sleep_hours

        actions = {
            "Wake up": 0,
            "Cold Shower + 50mg Caffeine": 1.5,
            "Meal 1": 2,
            "50mg Caffeine": 5,
            "Meal 2": 8,
            "Breakpoint -> AAR -> Snack": 12,
            "Meal 3 -> Stretch": hour_days - 1.5,
            "Bed time": hour_days - 0.25,
            "Sleep": hour_days + 0.25,
        }

        schedule = []
        for activity, delay_h in actions.items():
            total_min = cwt_min + int(delay_h * 60)
            hour = (total_min // 60) % 24
            minute = total_min % 60
            time_str = f"{hour:02d}:{minute:02d}"
            schedule.append(f"{delay_h:4.1f}h | {time_str} | {activity}")
        return schedule
    except Exception:
        return ["Invalid time format"]

def update_schedule():
    for widget in schedule_frame.winfo_children():
        widget.destroy()
    schedule = generate_schedule(data["wake_time"])
    for line in schedule:
        color = "white"
        if "Wake" in line: color = GREEN
        elif "Sleep" in line: color = RED
        elif "Caffeine" in line: color = PINK
        tk.Label(
            schedule_frame,
            text=line,
            font=("Courier", 10),
            fg=color,
            bg=LIGHT_GRAY,
            anchor="w"
        ).pack(fill="x", padx=10, pady=2)


# --==-- SAVE WAKE TIME --==--
def save_wake_time():
    val = wake_var.get().strip()
    try:
        hrs, mins = map(int, val.split(":"))
        if 0 <= hrs < 24 and 0 <= mins < 60:
            data["wake_time"] = val
            save_data()
            update_schedule()
        else:
            raise ValueError
    except:
        messagebox.showerror("Invalid Time", "Use HH:MM (e.g., 09:00)")


# --==-- TO-DO LIST --==--
def add_todo():
    # Fixed: Make dialog appear on top
    dialog = simpledialog._QueryDialog(
        "Add Task", "New task:",
        parent=root,
        title="Add Task"
    )
    dialog.transient(root)  # Stay on top of root
    dialog.grab_set()       # Block input to root
    dialog.wait_window()    # Wait for user
    result = dialog.getresult()
    if result and result.strip():
        data["todos"].append(result.strip())
        save_data()
        refresh_todos()

def delete_todo(i):
    del data["todos"][i]
    save_data()
    refresh_todos()

def refresh_todos():
    for widget in todo_frame.winfo_children():
        widget.destroy()
    for idx, todo in enumerate(data["todos"]):
        row = tk.Frame(todo_frame, bg="white")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=todo, anchor="w", bg="white", font=(FONT_NAME, 10)).pack(side="left", padx=4)
        btn = tk.Button(row, text="✓", command=lambda i=idx: delete_todo(i), bg=GREEN, fg="white", width=2, relief="flat")
        btn.pack(side="right", padx=4)


# --==-- SCROLLABLE FRAME CLASS --==--
class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, bg=DARK_GRAY, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=DARK_GRAY)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_frame = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _adjust_frame_width(event):
            canvas.itemconfig(canvas_frame, width=container.winfo_width()-20)

        canvas.bind("<Configure>", _adjust_frame_width)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas = canvas

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)  # Windows
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux up
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux down

        # Remove scroll binding when dialog opens
        def _on_dialog_open():
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
        def _on_dialog_close():
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
            canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        self.on_dialog_open = _on_dialog_open
        self.on_dialog_close = _on_dialog_close


# --==-- MAIN WINDOW SETUP --==--
root = tk.Tk()
root.title("Uni Organiser")
root.config(bg=DARK_GRAY)
root.resizable(False, False)
center_window(root, 500, 700)

# --==-- SCROLLABLE CONTAINER --==--
container = ScrollableFrame(root)
container.pack(fill="both", expand=True, padx=10, pady=10)

content = container.scrollable_frame

# Header
header = tk.Label(
    content,
    text="",
    font=(FONT_NAME, 16, "bold"),
    fg=GREEN,
    bg=DARK_GRAY
)
header.pack(pady=10)
update_counter()

# Wake Time
wake_frame = tk.Frame(content, bg=DARK_GRAY)
wake_frame.pack(pady=5)
tk.Label(wake_frame, text="Wake Time:", fg="white", bg=DARK_GRAY, font=(FONT_NAME, 10)).pack(side="left")
wake_var = tk.StringVar(value=data["wake_time"])
wake_entry = tk.Entry(wake_frame, textvariable=wake_var, width=8, font=(FONT_NAME, 10), justify="center", bg="white")
wake_entry.pack(side="left", padx=5)
tk.Button(
    wake_frame,
    text="Save",
    command=save_wake_time,
    bg=GREEN,
    fg="white",
    font=(FONT_NAME, 9, "bold"),
    relief="flat",
    padx=10,
    pady=2
).pack(side="left", padx=5)

# Daily Schedule
tk.Label(content, text="📅 Daily Routine", fg=YELLOW, bg=DARK_GRAY, font=(FONT_NAME, 12, "bold")).pack()
schedule_frame = tk.Frame(content, bg=LIGHT_GRAY, bd=2, relief="flat")
schedule_frame.pack(pady=5, fill="both", expand=True, padx=20)
update_schedule()

# To-Do List
tk.Label(content, text="To-Do List", fg="lightblue", bg=DARK_GRAY, font=(FONT_NAME, 12, "bold")).pack(pady=(10, 0))
todo_frame = tk.Frame(content, bg="white", bd=2, relief="sunken", height=100)
todo_frame.pack(pady=5, fill="both", expand=True, padx=20)
todo_frame.pack_propagate(False)
refresh_todos()

tk.Button(
    content,
    text="Add Task",
    command=add_todo,
    bg="lightblue",
    fg="black",
    font=(FONT_NAME, 10, "bold"),
    relief="flat",
    height=2
).pack(pady=5, padx=20, fill="x")

# --==-- POMODORO TIMER --==--
try:
    from pomodoro import PomodoroTimer
    pomodoro_widget = PomodoroTimer(content)
except Exception as e:
    tk.Label(
        content,
        text="Timer failed to load",
        fg="red",
        bg="black",
        font=("Helvetica", 10)
    ).pack(pady=10)

# Change Deadline
def change_date():
    dialog = simpledialog._QueryDialog(
        "Change Deadline", "Enter date (YYYY-MM-DD):",
        parent=root,
        title="Target Date",
        initialvalue=data["target_date"]
    )
    dialog.transient(root)
    dialog.grab_set()
    dialog.wait_window()
    result = dialog.getresult()
    if result:
        try:
            datetime.datetime.strptime(result, "%Y-%m-%d")
            data["target_date"] = result
            save_data()
            update_counter()
        except:
            messagebox.showerror("Error", "Invalid format. Use YYYY-MM-DD")

tk.Button(
    content,
    text="Change Deadline",
    command=change_date,
    bg="lightyellow",
    fg="black",
    font=(FONT_NAME, 10),
    relief="flat"
).pack(pady=5)

root.attributes("-topmost", True)

root.mainloop()
