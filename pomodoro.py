import tkinter as tk
import math

class PomodoroTimer:
    PINK = "#e2979c"
    RED = "#e7305b"
    GREEN = "#9bdeac"
    YELLOW = "#f7f5dd"
    FONT_NAME = "Courier"
    DEFAULT_WORK_MIN = 25
    DEFAULT_SHORT_BREAK_MIN = 5
    DEFAULT_LONG_BREAK_MIN = 15

    def __init__(self, parent):
        self.parent = parent
        self.reps = 0
        self.timer = None
        self.is_running = False

        self.work_min = self.DEFAULT_WORK_MIN
        self.short_break_min = self.DEFAULT_SHORT_BREAK_MIN
        self.long_break_min = self.DEFAULT_LONG_BREAK_MIN

        self.setup_window()

    def setup_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Pomodoro Timer")
        self.window.config(padx=40, pady=40, bg="black")
        self.window.resizable(False, False)
        self.window.grab_set()  # Makes it modal (optional)
        self.window.focus_force()

        config_frame = tk.Frame(self.window, bg="black")
        config_frame.pack(pady=10)

        tk.Label(config_frame, text="Work (min):", fg=self.GREEN, bg="black", font=("Helvetica", 10)).grid(row=0, column=0, padx=5)
        self.work_entry = tk.Entry(config_frame, width=5, font=("Helvetica", 10), justify="center")
        self.work_entry.insert(0, str(self.DEFAULT_WORK_MIN))
        self.work_entry.grid(row=0, column=1, padx=5)

        tk.Label(config_frame, text="Short Break:", fg=self.PINK, bg="black", font=("Helvetica", 10)).grid(row=0, column=2, padx=5)
        self.short_break_entry = tk.Entry(config_frame, width=5, font=("Helvetica", 10), justify="center")
        self.short_break_entry.insert(0, str(self.DEFAULT_SHORT_BREAK_MIN))
        self.short_break_entry.grid(row=0, column=3, padx=5)

        tk.Label(config_frame, text="Long Break:", fg=self.RED, bg="black", font=("Helvetica", 10)).grid(row=0, column=4, padx=5)
        self.long_break_entry = tk.Entry(config_frame, width=5, font=("Helvetica", 10), justify="center")
        self.long_break_entry.insert(0, str(self.DEFAULT_LONG_BREAK_MIN))
        self.long_break_entry.grid(row=0, column=5, padx=5)

        apply_btn = tk.Button(
            config_frame,
            text="Apply",
            command=self.apply_settings,
            bg=self.GREEN,
            fg="white",
            font=("Helvetica", 9, "bold"),
            relief="flat"
        )
        apply_btn.grid(row=0, column=6, padx=10)

        # === Main Timer UI ===
        self.title_label = tk.Label(
            self.window,
            text="Pomodoro",
            fg=self.GREEN,
            bg="black",
            font=("Helvetica", 16, "bold")
        )
        self.title_label.pack(pady=(10, 5))

        self.canvas = tk.Canvas(self.window, width=200, height=224, bg="black", highlightthickness=0)
        try:
            self.tomato_img = tk.PhotoImage(file="tomato.png")
            self.canvas.create_image(100, 112, image=self.tomato_img)
        except tk.TclError:
            # Fallback: draw red circle if image not found
            self.canvas.create_oval(30, 30, 170, 170, fill=self.RED, outline="", width=2)
        self.timer_text = self.canvas.create_text(
            100, 130,
            text="00:00",
            fill="white",
            font=(self.FONT_NAME, 30, "bold")
        )
        self.canvas.pack(pady=10)

        btn_frame = tk.Frame(self.window, bg="black")
        btn_frame.pack()

        self.start_button = tk.Button(
            btn_frame,
            text="▶ Start",
            command=self.start_timer,
            bg=self.GREEN,
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            padx=12
        )
        self.start_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(
            btn_frame,
            text="⏹ Reset",
            command=self.reset_timer,
            bg=self.PINK,
            fg="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            padx=12
        )
        self.reset_button.pack(side="left", padx=5)

        self.check_marks = tk.Label(
            self.window,
            text="",
            fg=self.GREEN,
            bg="black",
            font=(self.FONT_NAME, 16, "bold")
        )
        self.check_marks.pack(pady=5)

        self.canvas.itemconfig(self.timer_text, text="00:00")

    def apply_settings(self):
        """Read values from entries and validate them."""
        try:
            work = int(self.work_entry.get())
            short_break = int(self.short_break_entry.get())
            long_break = int(self.long_break_entry.get())

            if work <= 0 or short_break <= 0 or long_break <= 0:
                raise ValueError

            self.work_min = work
            self.short_break_min = short_break
            self.long_break_min = long_break

            self.title_label.config(text="Settings Applied!", fg=self.GREEN)
            self.window.after(1500, lambda: self.title_label.config(text="Pomodoro"))
        except ValueError:
            self.title_label.config(text="Invalid Time!", fg=self.RED)
            self.window.after(1500, lambda: self.title_label.config(text="Pomodoro"))

    def start_timer(self):
        if self.is_running:
            return
        self.is_running = True
        self.start_button.config(state="disabled")

        work_sec = self.work_min * 60
        short_break_sec = self.short_break_min * 60
        long_break_sec = self.long_break_min * 60

        self.reps += 1

        if self.reps % 8 == 0:
            self.count_down(long_break_sec)
            self.title_label.config(text="Break", fg=self.RED)
        elif self.reps % 2 == 0:
            self.count_down(short_break_sec)
            self.title_label.config(text="Break", fg=self.PINK)
        else:
            self.count_down(work_sec)
            self.title_label.config(text="Work", fg=self.GREEN)

    def reset_timer(self):
        self.is_running = False
        self.start_button.config(state="normal")
        if self.timer:
            self.window.after_cancel(self.timer)
        self.canvas.itemconfig(self.timer_text, text="00:00")
        self.title_label.config(text="Pomodoro", fg=self.GREEN)
        self.check_marks.config(text="")
        self.reps = 0

    def count_down(self, count):
        count_min = count // 60
        count_sec = count % 60
        self.canvas.itemconfig(self.timer_text, text=f"{count_min:02d}:{count_sec:02d}")

        if count > 0:
            self.timer = self.window.after(1000, self.count_down, count - 1)
        else:
            self.is_running = False
            self.start_button.config(state="normal")
            self.start_timer()  # Auto-start next phase
            marks = "✔" * (self.reps // 2)
            self.check_marks.config(text=marks)
