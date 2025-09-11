import tkinter as tk
import tkinter.messagebox as messagebox
from ui import PlannerUI
from data_manager import DataManager


def run_app():
    window = tk.Tk()
    data_manager = DataManager()
    def save_on_close():
        data_manager.data["priority"] = ui.priority_var.get().strip()
        data_manager.data["priority_rag"] = ui.priority_rag
        data_manager.save_data()
        window.destroy()

    ui = PlannerUI(window, data_manager, save_on_close)
    ui.build()

    try:
        window.mainloop()
    except Exception as exception:
        messagebox.showerror("Error", f"App crashed: {exception}")



if __name__ == "__main__":
    run_app()
