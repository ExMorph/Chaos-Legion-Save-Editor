from pathlib import Path
import shutil
import tkinter as tk
from tkinter import filedialog

SAVE_SIZE = 592

# ---------- File selection ----------

def select_save_file():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Select Chaos Legion save file",
        filetypes=[("Chaos Legion Save", "*.DAT")]
    )

# ---------- Save handling ----------

def load_save(path):
    data = bytearray(Path(path).read_bytes())
    if len(data) != SAVE_SIZE:
        raise ValueError("Unexpected save file size")
    return data

def save(path, data):
    Path(path).write_bytes(data)

def backup(path):
    path = Path(path)
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    shutil.copy(path, backup_dir / path.name)

# ---------- Game edits ----------

def enable_thanatos(data):
    data[0x104] = 0x01     # Thanatos unlocked
    data[0x15]  = 0xF7     # Ultimate item
    data[0x43]  = 0x00     # Level
    data[0x65]  = 0x00     # EXP
    data[0x66]  = 0x00
    data[0x67]  = 0x00
    data[0x68]  = 0x00

def get_current_level(data):
    return data[0x201]

def set_level(data):
    print(f"Current level: {get_current_level(data):02}")
    print("Set level (00–14)")

    while True:
        choice = input("> ").strip()

        if not choice.isdigit():
            print("Please enter a number (00–14)")
            continue

        lvl = int(choice)

        if lvl < 0 or lvl > 14:
            print("Level must be between 00 and 14")
            continue

        data[0x201] = lvl
        print(f"Level set to {lvl:02}")
        break

# ---------- Main menu ----------

def main():
    print("Chaos Legion Save Editor")
    print("------------------------")

    save_path = select_save_file()
    if not save_path:
        print("No file selected. Exiting.")
        return

    print(f"Selected file: {save_path}")

    try:
        data = load_save(save_path)
    except Exception as e:
        print(f"Error: {e}")
        return

    backup(save_path)
    print("Backup created.\n")

    while True:
        print("\nMenu:")
        print("1 - Enable Thanatos egg")
        print("2 - Set current level")
        print("0 - Save and exit")

        choice = input("> ").strip()

        if choice == "1":
            enable_thanatos(data)
            print("Thanatos enabled.")

        elif choice == "2":
            set_level(data)

        elif choice == "0":
            save(save_path, data)
            print("Save updated. You can now load it in-game.")
            break

        else:
            print("Unknown option.")

if __name__ == "__main__":
    main()
