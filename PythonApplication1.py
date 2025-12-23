import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
import shutil

SAVE_SIZE = 592

# ______________ OFFSETS ______________

OFFSETS = {
    "guild_flag": 0xFE,
    "legion_mask": 0x107,
    "current_level": 0x201,
    "sword_lvl": (0x49, 0x4A, 0x4B),
    "exp": (0x65, 0x66, 0x67, 0x68),
}

LEGIONS = {
    1: "Guild",
    2: "Arrow",
    3: "Thanatos"
}

# ______________ STATUS CHECKS ______________

def guild_unlocked(data):
    return data[OFFSETS["guild_flag"]] > 0

def arrow_unlocked(data):
    return data[OFFSETS["legion_mask"]] & 0x01

def thanatos_unlocked(data):
    return data[OFFSETS["legion_mask"]] == 0xF7

# ______________ GUI ______________

class ChaosLegionEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chaos Legion Save Editor")

        self.data = None
        self.save_path = None

        tk.Button(root, text="Select Save File", command=self.load_save).pack(pady=5)

        self.file_label = tk.Label(root, text="No file selected", wraplength=480)
        self.file_label.pack()

        self.legion_frame = tk.LabelFrame(root, text="Legions")
        self.legion_frame.pack(padx=10, pady=10, fill="x")

        self.legion_labels = {}
        for lid, name in LEGIONS.items():
            lbl = tk.Label(self.legion_frame, text=f"{lid}. {name}: N/A")
            lbl.pack(anchor="w")
            self.legion_labels[lid] = lbl

        tk.Button(root, text="Open Legion Menu", command=self.open_legion_menu).pack(pady=5)
        tk.Button(root, text="Set Level (from 01 to 14)",  command=lambda: self.set_level()).pack(fill="x")
        tk.Button(root, text="Save & Exit", command=self.save_and_exit).pack(pady=5)

    # ______________ FILE ______________

    def load_save(self):
        path = filedialog.askopenfilename(
            title="Select Chaos Legion save",
            filetypes=[("Chaos Legion Save", "*.DAT")]
        )
        if not path:
            return

        try:
            data = bytearray(Path(path).read_bytes())
            if len(data) != SAVE_SIZE:
                raise ValueError("Invalid save size")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        shutil.copy(path, backup_dir / Path(path).name)

        self.data = data
        self.save_path = path
        self.file_label.config(text=path)
        self.refresh_legion_status()

    # ______________ STATUS ______________

    def refresh_legion_status(self):
        if not self.data:
            return

        self.legion_labels[1].config(
            text=f"1. Guild: {'UNLOCKED' if guild_unlocked(self.data) else 'LOCKED'}"
        )
        self.legion_labels[2].config(
            text=f"2. Arrow: {'UNLOCKED' if arrow_unlocked(self.data) else 'LOCKED'}"
        )
        self.legion_labels[3].config(
            text=f"3. Thanatos: {'UNLOCKED' if thanatos_unlocked(self.data) else 'LOCKED'}"
        )

    # ______________ LEGION MENU ______________

    def open_legion_menu(self):
        if not self.data:
            messagebox.showwarning("No save", "Load a save file first")
            return

        legion_id = simpledialog.askinteger(
            "Legion",
            "Enter legion number:\n1 - Guild\n2 - Arrow\n3 - Thanatos\n0 - Cancel",
            minvalue=0,
            maxvalue=3
        )

        if not legion_id or legion_id == 0:
            return

        name = LEGIONS[legion_id]
        win = tk.Toplevel(self.root)
        win.title(f"{name} Legion")

        tk.Label(win, text=f"{name} Legion").pack(pady=5)

        tk.Button(win, text="Unlock Legion",
                  command=lambda: self.unlock_legion(legion_id)).pack(fill="x")

        tk.Button(win, text="Set Legion Level (from 00 to 14)",
                  command=lambda: self.set_level()).pack(fill="x")

        tk.Button(win, text="Reset EXP",
                  command=lambda: self.reset_exp()).pack(fill="x")

        if legion_id == 1:
            tk.Button(win, text="Reset Sword Level",
                      command=self.reset_sword).pack(fill="x")

        tk.Button(win, text="Back", command=win.destroy).pack(pady=5)

    # ______________ ACTIONS ______________

    def unlock_legion(self, legion_id):
        if legion_id == 1:
            self.data[OFFSETS["guild_flag"]] = 1
            self.data[OFFSETS["legion_mask"]] |= 0x01
        elif legion_id == 2:
            self.data[OFFSETS["legion_mask"]] |= 0x01
        elif legion_id == 3:
            self.data[OFFSETS["legion_mask"]] = 0xF7

        self.refresh_legion_status()
        messagebox.showinfo("Done", "Legion unlocked")

    def set_level(self):
        lvl = simpledialog.askinteger(
            "Set Level",
            "Enter level (from 0 to 14)",
            minvalue=0,
            maxvalue=14
        )
        if lvl is None:
            return
        self.data[OFFSETS["current_level"]] = lvl
        messagebox.showinfo("Done", f"Level set to {lvl:02}")

    def reset_exp(self):
        for o in OFFSETS["exp"]:
            self.data[o] = 0
        messagebox.showinfo("Done", "EXP reset")

    def reset_sword(self):
        for o in OFFSETS["sword_lvl"]:
            self.data[o] = 0
        messagebox.showinfo("Done", "Sword level reset")

    # ______________ SAVE ______________

    def save_and_exit(self):
        if self.data and self.save_path:
            Path(self.save_path).write_bytes(self.data)
        self.root.destroy()

# ______________ RUN ______________

if __name__ == "__main__":
    root = tk.Tk()
    app = ChaosLegionEditorGUI(root)
    root.mainloop()
