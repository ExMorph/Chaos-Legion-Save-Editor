import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from save_logic import SaveFile

class SaveEditorGUI:
    def __init__(self, root):
        self.root = root
        self.icons = {}
        self.save = SaveFile()
        self.load_icons()

        self.root.title("Chaos Legion Save Editor")

        # --- выбор файла ---
        tk.Button(root, text="Select Save File", command=self.select_file).pack(pady=5)
        self.file_label = tk.Label(root, text="No file selected", wraplength=480)
        self.file_label.pack()

        # --- блок Stage как кнопка ---
        self.stage_frame = tk.LabelFrame(root, text="Stage")
        self.stage_frame.pack(padx=10, pady=10, fill="x")

        self.stage_button = tk.Button(
            self.stage_frame,
            text="Current Level: N/A",
            compound="left",
            width=220,
            command=self.open_stage_window
        )
        self.stage_button.pack(padx=10, pady=5)

        # --- блок Legions ---
        self.legions_frame = tk.LabelFrame(root, text="Legions")
        self.legions_frame.pack(padx=10, pady=10, fill="x")

        self.create_legion_buttons()

        # --- кнопка сохранени¤ ---
        tk.Button(root, text="Exit", command=self.save_and_exit).pack(pady=5)

    # ---------- GUI Actions ----------

    def load_icons(self):
        try:
            self.icons["thanatos"] = tk.PhotoImage(file="icons/thanatos/Main.png")
            self.icons["guilt"] = tk.PhotoImage(file="icons/guild/Main.png")
            self.icons["malice"] = tk.PhotoImage(file="icons/malice/Main.png")
            self.icons["blasphemy"] = tk.PhotoImage(file="icons/blasphemous/Main.png")
            self.icons["arrogance"] = tk.PhotoImage(file="icons/arrogance/Main.png")
            self.icons["flawed"] = tk.PhotoImage(file="icons/flawed/Main.png")
            self.icons["hatred"] = tk.PhotoImage(file="icons/hatred/Main.png")
            self.icons["empty"] = tk.PhotoImage(file="icons/sieg/Main.png")

            for lvl in range(15):  # уровни 0Ц14
                self.icons[f"game_level_{lvl}"] = tk.PhotoImage(
                    file=f"icons/game_levels/lvl{lvl}.png"
                )
        except Exception as e:
            messagebox.showerror("Icon error", str(e))

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
        self.refresh_stage()
        self.create_legion_buttons()

    def refresh_stage(self):
        if not self.save.data:
            self.stage_button.config(text="Current Level: N/A", image="")
            return

        current = self.save.get_current_stage()
        self.stage_button.config(text=f"Current Level: {current}")

        icon = self.icons.get(f"game_level_{current}")
        if icon:
            self.stage_button.config(image=icon)
            self.stage_button.image = icon

    def open_stage_window(self):
        if not self.save.data:
            messagebox.showwarning("No save", "Load save first")
            return

        win = tk.Toplevel(self.root)
        win.title("Select Stage")

        grid = tk.Frame(win)
        grid.pack(padx=10, pady=10)

        for lvl in range(15):  # уровни 0Ц14
            icon = self.icons.get(f"game_level_{lvl}")
            btn = tk.Button(
                grid,
                text=f"{lvl:02}",
                image=icon,
                compound="top",
                width=70,
                height=70,
                command=lambda l=lvl: self._apply_stage(l, win)
            )
            btn.grid(row=lvl // 5, column=lvl % 5, padx=5, pady=5)

    def _apply_stage(self, lvl, win):
        self.save.set_current_stage(lvl)
        self.refresh_stage()
        self.save.save()
        messagebox.showinfo("Done", f"Stage set to {lvl}")
        win.destroy()

    def create_legion_buttons(self):
        # очищаем рамку
        for widget in self.legions_frame.winfo_children():
            widget.destroy()

        if not self.save.data:
            tk.Label(self.legions_frame, text="Load save first").pack()
            return

        # берём список легионов, исключаем Null и разворачиваем порядок
        legions = [l for l in self.save.get_legions() if l.name != "Null"]
        legions.reverse()  # теперь Guilt → Thanatos

        for legion in legions:
            unlocked = legion.is_unlocked()
            status = "UNLOCKED" if unlocked else "LOCKED"
            color = "green" if unlocked else "red"
            icon = self.icons.get(legion.name.lower())

            btn = tk.Button(
                self.legions_frame,
                text=f"{legion.name} [{status}]",
                image=icon,
                compound="left",
                anchor="w",
                width=220,
                fg=color,
                command=lambda l=legion: self._on_legion_selected(l)
            )
            btn.pack(padx=10, pady=5, fill="x")


    def _on_legion_selected(self, legion):
        mask_before = self.save.data[self.save.OFFSETS["legions_mask"]]
        print(f"Toggling {legion.name}, mask before: {hex(mask_before)}")

        if legion.is_unlocked():
            legion.lock()
            action = "locked"
        else:
            legion.unlock()
            action = "unlocked"

        mask_after = self.save.data[self.save.OFFSETS["legions_mask"]]
        print(f"mask after: {hex(mask_after)}")

        # уведомление
        if self.save._get_mask() == 0x00:
            messagebox.showinfo("Info", "All legions closed.\nWarning: When opening the Level Up menu the game crashes \nLoad your save file and resave")
        else:
            messagebox.showinfo("Done", f"{legion.name} {action}")

        self.create_legion_buttons()
        self.save.save()


    def save_and_exit(self):
        self.root.destroy()




if __name__ == "__main__":
    root = tk.Tk()
    app = SaveEditorGUI(root)
    root.mainloop()
