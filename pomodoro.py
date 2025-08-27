import tkinter as tk
import math

class PomodoroTimer:
    PINK = "#e2979c"
    RED = "#e7305b"
    GREEN = "#9bdeac"
    YELLOW = "#f7f5dd"
    FONT_NAME = "Courier"
    WORK_MIN = 25
    SHORT_BREAK_MIN = 5
    LONG_BREAK_MIN = 15

    def __init__(self, parent):
        self.parent = parent
        self.reps = 0
        self.timer = None
        self.is_running = False

        self.frame = tk.Frame(parent, bg="black")
        self.frame.pack(pady=10, fill="x", padx=20)

        self.title_label = tk.Label(
            self.frame,
            text="🍅 Pomodoro",
            fg=self.GREEN,
            bg="black",
            font=("Helvetica", 14, "bold")
        )
        self.title_label.pack(pady=5)

        self.canvas = tk.Canvas(self.frame, width=200, height=224, bg="black", highlightthickness=0)
        try:
            self.tomato_img = tk.PhotoImage(file="tomato.png")
            self.canvas.create_image(100, 112, image=self.tomato_img)
        except tk.TclError:
            self.canvas.create_oval(30, 30, 170, 170, fill=self.RED, outline="", width=2)
        self.timer_text = self.canvas.create_text(
            100, 130,
            text="00:00",
            fill="white",
            font=(self.FONT_NAME, 30, "bold")
        )
        self.canvas.pack(pady=10)

        btn_frame = tk.Frame(self.frame, bg="black")
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
            self.frame,
            text="",
            fg=self.GREEN,
            bg="black",
            font=(self.FONT_NAME, 16, "bold")
        )
        self.check_marks.pack(pady=5)

        self.canvas.itemconfig(self.timer_text, text="00:00")

    def start_timer(self):
        if self.is_running:
            return
        self.is_running = True
        self.start_button.config(state="disabled")

        work_sec = self.WORK_MIN * 60
        short_break_sec = self.SHORT_BREAK_MIN * 60
        long_break_sec = self.LONG_BREAK_MIN * 60

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
            self.parent.after_cancel(self.timer)
        self.canvas.itemconfig(self.timer_text, text="00:00")
        self.title_label.config(text="🍅 Pomodoro", fg=self.GREEN)
        self.check_marks.config(text="")
        self.reps = 0

    def count_down(self, count):
        count_min = count // 60
        count_sec = count % 60
        self.canvas.itemconfig(self.timer_text, text=f"{count_min:02d}:{count_sec:02d}")

        if count > 0:
            self.timer = self.parent.after(1000, self.count_down, count - 1)
        else:
            self.is_running = False
            self.start_button.config(state="normal")
            self.start_timer()
            marks = "✔" * (self.reps // 2)
            self.check_marks.config(text=marks)
