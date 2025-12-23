# save_logic.py
from pathlib import Path
import shutil
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class Legion:
    name: str
    max_level: Optional[int]
    is_unlocked: Callable[[], bool]
    unlock: Callable[[], None]
    set_level: Optional[Callable[[int], None]] = None

class SaveFile:

    SAVE_SIZE = 592

    OFFSETS = {
        "malice_crest": 0xFE,
        "thanatos_chip": 0x103,
        "thanatos_crest": 0x104,
        "legions_mask": 0x15,
        "current_level": 0x201,
        "sword_exp": (0x49, 0x4A, 0x4B),
        "thanatos_exp": (0x65, 0x66, 0x67, 0x68),
        "thanatos_level": (0x43),
    }

    def __init__(self):
        self.data = None
        self.path = None

    # ---------- File ----------

    def load(self, path):
        data = bytearray(Path(path).read_bytes())
        if len(data) != self.SAVE_SIZE:
            raise ValueError("Invalid save size")

        self.data = data
        self.path = path
        self._backup()

    def save(self):
        if self.data and self.path:
            Path(self.path).write_bytes(self.data)

    def _backup(self):
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        shutil.copy(self.path, backup_dir / Path(self.path).name)

    # ---------- Status ----------

    def guild_unlocked(self):
        return self.data[self.OFFSETS["legions_mask"]] > 0 or 0x05 or 0xF7 or 0x77

    def malice_unlocked(self):
        return self.data[self.OFFSETS["legions_mask"]] & 0x05 or 0xF7 or 0x77

    def thanatos_unlocked(self):
        return self.data[self.OFFSETS["legions_mask"]] == 0xF7

    # ---------- Actions ----------

    def unlock_guild(self):
        self.data[self.OFFSETS["legions_mask"]] |= 0xF7

    def unlock_malice(self):
        self.data[self.OFFSETS["legions_mask"]] |= 0xF7

    def unlock_thanatos(self):
        self.data[self.OFFSETS["legions_mask"]] = 0xF7

    # Level legion set by 00 - 30
    def set_thanatos_level(self, lvl): 
        self.data[self.OFFSETS["thanatos_exp"]] = lvl

    # Game Level
    def set_level(self, lvl: int):
        if not 0 <= lvl <= 14:
            raise ValueError("Level out of range")
        self.data[self.OFFSETS["current_level"]] = lvl

    def reset_exp(self):
        for o in self.OFFSETS["exp"]:
            self.data[o] = 0

    def reset_sword(self):
        for o in self.OFFSETS["sword_exp"]:
            self.data[o] = 0

    def get_legions(self) -> list[Legion]:
        return [
        Legion(
            name="Guild",
            max_level=None,
            is_unlocked=self.guild_unlocked,
            unlock=self.unlock_guild
        ),
        Legion(
            name="Malice",
            max_level=None,
            is_unlocked=self.malice_unlocked,
            unlock=self.unlock_malice
        ),
        Legion(
            name="Thanatos",
            max_level=3,
            is_unlocked=self.thanatos_unlocked,
            unlock=self.unlock_thanatos,
            #set_level=self.set_thanatos_level(lvl)
        )
    ]
