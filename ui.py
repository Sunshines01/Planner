import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from functools import partial
from utils import *

class PlannerUI:
    def __init__(self, root, data_manager, on_closing):
        self.root = root
        self.data_manager = data_manager
        self.on_closing = on_closing  # Callback when closing
        self.tab_frames = {}
        self.priority_rag = data_manager.data.get("priority_rag", "🔴")
        self.priority_var = tk.StringVar(value=data_manager.data.get("priority", ""))

    def build(self):
        self.root.title("Planner")
        self.root.state("zoomed")
        self.root.config(bg=BG_COLOUR)

        self.setup_styles()
        self.create_heading()
        self.create_notebook_with_add_button()
        self.create_home_tab()
        self.load_module_tabs()
        self.bind_events()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=BG_COLOUR, padding=10)
        style.configure("TNotebook.Tab", background=ACCENT, foreground="white",
                        padding=(15, 8), font=(FONT_NAME, 11))
        style.map("TNotebook.Tab", background=[('selected', HIGHLIGHT_COLOUR)])

    def create_heading(self):
        tk.Label(
            self.root, text="Planner", font=(FONT_NAME, 20, "bold"),
            bg=BG_COLOUR, fg=ACCENT
        ).pack(pady=15)

        heading_frame = tk.Frame(self.root, bg=BG_COLOUR)
        heading_frame.pack(pady=8)

        self.time_label = tk.Label(heading_frame, font=TITLE_FONT, bg=BG_COLOUR, fg=ACCENT)
        self.time_label.pack()

        tk.Label(
            heading_frame, text="Your Daily Command Center",
            font=FONT, bg=BG_COLOUR, fg=TEXT
        ).pack()

        self.update_clock()

    def update_clock(self):
        self.time_label.config(text=f"📅 {get_current_time_str()}")
        self.root.after(60000, self.update_clock)

    def create_notebook_with_add_button(self):
        notebook_frame = tk.Frame(self.root, bg=BG_COLOUR)
        notebook_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.notebook = ttk.Notebook(notebook_frame)
        self.notebook.pack(side="top", fill="both", expand=True)

        self.add_tab_button = tk.Label(
            notebook_frame, text="➕", font=(FONT_NAME, 14, "bold"),
            bg=ACCENT, fg="white", cursor="hand2", width=3
        )
        self.add_tab_button.place(relx=1.0, y=10, anchor="ne", x=-10)

    def create_home_tab(self):
        home_tab = tk.Frame(self.notebook, bg=BG_COLOUR)
        self.notebook.add(home_tab, text="🏠 Home")
        self.tab_frames["Home"] = home_tab
        self.build_home_content(home_tab)

    def build_home_content(self, parent):
        split_frame = tk.Frame(parent, bg=BG_COLOUR)
        split_frame.pack(fill="both", expand=True, padx=15, pady=10)

        left_frame = tk.Frame(split_frame, bg=BG_COLOUR, width=500)
        left_frame.pack(side="left", fill="both", expand=True)
        left_frame.pack_propagate(False)

        right_frame = tk.Frame(split_frame, bg=BG_COLOUR, width=500)
        right_frame.pack(side="right", fill="both", expand=True)
        right_frame.pack_propagate(False)

        # Priority Task
        tk.Label(left_frame, text="🎯 Priority Task", font=TITLE_FONT,
                 bg=BG_COLOUR, fg=TEXT).pack(anchor="w", padx=25, pady=(15, 8))

        priority_frame = tk.Frame(left_frame, bg=BG_COLOUR)
        priority_frame.pack(padx=25, pady=6, fill="x")

        tk.Entry(priority_frame, textvariable=self.priority_var,
                 font=(FONT_NAME, 11), bd=2, relief="solid").pack(
                     side="left", fill="x", expand=True, ipady=4
                 )

        self.rag_button = tk.Label(
            priority_frame, text=self.priority_rag,
            font=(FONT_NAME, 14, "bold"), width=3, cursor="hand2", bg="white"
        )
        self.rag_button.pack(side="right", padx=(10, 0))
        set_rag_color(self.rag_button, self.priority_rag)
        self.rag_button.bind("<Button-1>", self.cycle_priority_rag)

        # To-Do List
        tk.Label(left_frame, text="✅ Today's To-Do List", font=TITLE_FONT,
                 bg=BG_COLOUR, fg=TEXT).pack(anchor="w", padx=25, pady=(10, 8))
        self.task_list_frame = self.create_task_list(left_frame, self.data_manager.data["modules"]["Home"])

        # Timetable
        tk.Label(right_frame, text="📅 Today's Timetable", font=(FONT_NAME, 14, "bold"),
                 bg=BG_COLOUR, fg=TEXT).pack(anchor="w", padx=25, pady=(10, 10))
        self.create_timetable(right_frame)

    def create_task_list(self, parent, task_list):
        scrollable_frame, canvas = create_scrollable_frame(parent)

        def refresh():
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            for idx, (task, status) in enumerate(task_list):
                row = tk.Frame(scrollable_frame, bg="white")
                row.pack(fill="x", pady=2, padx=10)

                delete_btn = tk.Button(row, text="❌", command=partial(delete_task, idx),
                                       bg="lightcoral", fg="white", width=2, font=(FONT_NAME, 8))
                delete_btn.pack(side="left", padx=2)

                tk.Label(row, text=task, bg="white", font=FONT, anchor="w").pack(
                    side="left", padx=6, fill="x", expand=True
                )

                rag_label = tk.Label(row, text=status, width=3, font=TITLE_FONT)
                rag_label.pack(side="right", padx=6)
                set_rag_color(rag_label, status)

                rag_label.bind("<Button-1>", lambda e, i=idx: cycle_rag(i))

            canvas.config(scrollregion=canvas.bbox("all"))

        def delete_task(idx):
            if 0 <= idx < len(task_list):
                del task_list[idx]
                self.data_manager.save_data()
                refresh()

        def cycle_rag(idx):
            if 0 <= idx < len(task_list):
                task, current = task_list[idx]
                statuses = ["🔴", "🟡", "🟢", "🔘"]
                new_status = statuses[(statuses.index(current) + 1) % 4] if current in statuses else "🔴"
                task_list[idx] = (task, new_status)
                self.data_manager.save_data()
                refresh()

        refresh()

        input_frame = tk.Frame(parent, bg=BG_COLOUR)
        input_frame.pack(pady=8, padx=25, fill="x")

        tk.Label(input_frame, text="➕ Add New Task", font=TITLE_FONT,
                 bg=BG_COLOUR, fg=TEXT).pack(anchor="w")

        entry = tk.Entry(input_frame, font=(FONT_NAME, 11), relief="solid", bd=2)
        entry.pack(fill="x", pady=4)

        def add_task():
            text = entry.get().strip()
            if text:
                task_list.append((text, "🔴"))
                entry.delete(0, "end")
                self.data_manager.save_data()
                refresh()
            else:
                messagebox.showwarning("Empty Task", "Please enter a task!")

        entry.bind("<Return>", lambda e: add_task())
        tk.Button(input_frame, text="➕ Add", command=add_task,
                  bg=ACCENT, fg="white", font=(FONT_NAME, 9, "bold"), width=10).pack(pady=4)

        return parent

    def create_timetable(self, parent):
        scrollable_frame, canvas = create_scrollable_frame(parent)
        entries = {}

        for h in range(24):
            hour = (4 + h) % 24
            am_pm = "AM" if hour < 12 else "PM"
            if hour == 0 or hour == 12:
                display_hour = 12
            else:
                display_hour = hour if hour <= 12 else hour - 12
            time_str = f"{display_hour:02d}:00 {am_pm}"

            row = tk.Frame(scrollable_frame, bg="white")
            row.pack(fill="x", pady=1, padx=5)

            tk.Label(row, text=time_str, width=15, anchor="w", bg="white",
                     font=("Courier", 11, "bold"), fg=ACCENT).pack(side="left")

            saved = self.data_manager.data["timetable"].get(f"{hour:02d}:00", "")
            var = tk.StringVar(value=saved)
            entries[f"{hour:02d}:00"] = var

            tk.Entry(row, textvariable=var, font=(FONT_NAME, 11), width=50).pack(
                side="left", padx=10, fill="x", expand=True)

        def save_timetable():
            for k, v in entries.items():
                self.data_manager.data["timetable"][k] = v.get().strip()
            self.data_manager.save_data()
            messagebox.showinfo("Saved", "Timetable saved! 🌟")

        tk.Button(parent, text="💾 Save All Entries", command=save_timetable,
                  bg=ACCENT, fg="white", font=TITLE_FONT, height=2).pack(pady=15)

    def load_module_tabs(self):
        for name, tasks in self.data_manager.data["modules"].items():
            if name == "Home":
                continue
            self.add_module_tab(name, tasks)

    def add_module_tab(self, name, task_list):
        tab = tk.Frame(self.notebook, bg=BG_COLOUR)
        self.notebook.add(tab, text=name)
        self.tab_frames[name] = tab

        button_frame = tk.Frame(tab, bg=BG_COLOUR)
        button_frame.pack(anchor="ne", padx=20, pady=10)

        delete_btn = tk.Button(
            button_frame, text="🗑️ Delete This Module",
            command=self.make_delete_func(name, tab),
            bg="lightcoral", fg="white", font=(FONT_NAME, 9, "bold"),
            relief="flat", width=20, height=1
        )
        delete_btn.pack()

        self.create_task_list(tab, task_list)

    def make_delete_func(self, name, tab):
        def delete():
            if messagebox.askyesno("Delete Module", f"Delete '{name}'?\nAll tasks will be lost.", icon="warning"):
                if name in self.data_manager.data["modules"]:
                    del self.data_manager.data["modules"][name]
                self.data_manager.save_data()
                self.notebook.forget(tab)
                del self.tab_frames[name]
                messagebox.showinfo("Deleted", f"'{name}' deleted.")
        return delete

    def cycle_priority_rag(self, event=None):
        statuses = ["🔴", "🟡", "🟢", "🔘"]
        self.priority_rag = statuses[(statuses.index(self.priority_rag) + 1) % 4] if self.priority_rag in statuses else "🔴"
        self.rag_button.config(text=self.priority_rag)
        set_rag_color(self.rag_button, self.priority_rag)

    def bind_events(self):
        self.add_tab_button.bind("<Button-1>", lambda e: self.add_new_module())
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def add_new_module(self):
        name = simpledialog.askstring("New Module", "Enter module name:")
        if not name or not name.strip():
            return
        name = name.strip()
        if name in self.data_manager.data["modules"]:
            messagebox.showwarning("Exists", f"Module '{name}' already exists!")
            return

        self.data_manager.data["modules"][name] = []
        self.data_manager.save_data()
        self.add_module_tab(name, [])
        messagebox.showinfo("Success", f"Module '{name}' created!")
