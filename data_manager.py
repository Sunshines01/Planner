import json
import os
from datetime import datetime

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
    "timetable": {},
    "task_history": []
}

# Generate 24-hour timetable (4am → 3am)
for h in range(24):
    hour = (4 + h) % 24
    DEFAULT_DATA["timetable"][f"{hour:02d}:00"] = ""

class DataManager:
    def __init__(self, filepath="data.json"):
        self.filepath = filepath
        self.data = self.load_data()

    def load_data(self):
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, "r", encoding="utf-8") as file:
                    data = json.load(file)
                for key, value in DEFAULT_DATA.items():
                    if key not in data:
                        data[key] = value
                return data
            else:
                return DEFAULT_DATA.copy()
        except Exception as exception:
            print(f"Error loading data: {exception}")
            return DEFAULT_DATA.copy()

    def save_data(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)
        except Exception as exception:
            print(f"Error saving data: {exception}")
