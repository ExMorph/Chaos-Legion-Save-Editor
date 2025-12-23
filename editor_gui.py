# editor_gui.py
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from save_logic import SaveFile

class SaveEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chaos Legion Save Editor")

        self.save = SaveFile()

        tk.Button(root, text="Select Save File", command=self.select_file).pack(pady=5)

        self.file_label = tk.Label(root, text="No file selected", wraplength=480)
        self.file_label.pack()

        self.status_frame = tk.LabelFrame(root, text="Legions")
        self.status_frame.pack(padx=10, pady=10, fill="x")

        self.lbl_guild = tk.Label(self.status_frame, text="Guild: N/A")
        self.lbl_arrow = tk.Label(self.status_frame, text="Arrow: N/A")
        self.lbl_thanatos = tk.Label(self.status_frame, text="Thanatos: N/A")

        self.lbl_guild.pack(anchor="w")
        self.lbl_arrow.pack(anchor="w")
        self.lbl_thanatos.pack(anchor="w")

        tk.Button(root, text="Legion Unlock", command=self.legion_menu).pack(pady=5)
        tk.Button(root, text="Set Level", command=self.level_menu).pack(pady=5)
        tk.Button(root, text="Save & Exit", command=self.save_and_exit).pack(pady=5)

    # ---------- GUI Actions ----------

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Chaos Legion Save", "*.DAT")])
        if not path:
            return

        try:
            self.save.load(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.file_label.config(text=path)
        self.refresh_status()

    def refresh_status(self):
        self.lbl_guild.config(
            text=f"Guild: {'UNLOCKED' if self.save.guild_unlocked() else 'LOCKED'}"
        )
        self.lbl_arrow.config(
            text=f"Arrow: {'UNLOCKED' if self.save.arrow_unlocked() else 'LOCKED'}"
        )
        self.lbl_thanatos.config(
            text=f"Thanatos: {'UNLOCKED' if self.save.thanatos_unlocked() else 'LOCKED'}"
        )

    def legion_menu(self):
        if not self.save.data:
            messagebox.showwarning("No save", "Load save first")
            return

        win = tk.Toplevel(self.root)
        win.title("Legions")

        for legion in self.save.get_legions():
            unlocked = legion.is_unlocked()
            color = "green" if unlocked else "red"
            status = "UNLOCKED" if unlocked else "LOCKED"

        btn = tk.Button(
        win,
        text=f"{legion.name} [{status}]",
        bg=color,
        fg="white",
        width=30,
        command=lambda l=legion: self._on_legion_selected(l, win)
        )
        btn.pack(padx=10, pady=5)

    def _on_legion_selected(self, legion, win):
        legion.unlock()
        self.refresh_status()
        messagebox.showinfo("Done", f"{legion.name} updated")
        win.destroy()

    def _unlock_legion(self, fn, win):
        fn()
        self.refresh_status()
        messagebox.showinfo("Done", "Legion updated")
        win.destroy()

    def legion_level_menu(self, legion):
        if legion.max_level is None:
            return

        win = tk.Toplevel(self.root)
        win.title(f"{legion.name} Level")

        for lvl in range(legion.max_level + 1):
            btn = tk.Button(
                win,
                text=f"Level {lvl}",
                width=25,
                command=lambda l=lvl: self._set_legion_level(legion, l, win)
            )
            btn.pack(padx=10, pady=4)

    def _set_legion_level(self, legion, lvl, win):
        if legion.set_level is None:
            return

        legion.set_level(lvl)
        self.save.save()

        messagebox.showinfo("Done", f"{legion.name} level set to {lvl}")
        win.destroy()

    def level_menu(self):
        if not self.save.data:
            messagebox.showwarning("No save", "Load save first")
            return

        choice = simpledialog.askinteger(
            "Level",
            "1 - 14\n0 - Cancel",
            minvalue=0,
            maxvalue=14
        )

        if 0 <= choice <= 14:
            self.save.set_level(choice)
        else:
            return

        self.refresh_status()
        messagebox.showinfo("Done", "Level updated")

    def save_and_exit(self):
        self.save.save()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SaveEditorGUI(root)
    root.mainloop()
