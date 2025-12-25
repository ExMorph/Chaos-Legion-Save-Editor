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

@dataclass
class LevelTarget:
    name: str
    get_stage: Callable[[], int]
    set_stage: Callable[[int], None]
    icon_key: Optional[str] = None

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

    def all_legions_locked(self):
        return self.data[self.OFFSETS["legions_mask"]] == 00

    def guild_unlocked(self):
        return self.data[self.OFFSETS["legions_mask"]] in (0x01, 0x05, 0xF7, 0x77)

    def malice_unlocked(self):
        return self.data[self.OFFSETS["legions_mask"]] in (0x04, 0x05, 0x06, 0xF7, 0x77)

    def blasphemous_unlocked(self):
        return self.data[self.OFFSETS["legions_mask"]] in (0xF7, 0x77)

    def arrogance_unlocked(self):
        return self.data[self.OFFSETS["legions_mask"]] in (0xF7, 0x77)

    def flawed_unlocked(self):
        return self.data[self.OFFSETS["legions_mask"]] in (0xF7, 0x77)

    def hatred_unlocked(self):
        return self.data[self.OFFSETS["legions_mask"]] in (0x02, 0x06, 0x07, 0xF7, 0x77)

    def thanatos_unlocked(self):
        return self.data[self.OFFSETS["legions_mask"]] == 0xF7

    # ---------- Actions ----------

    def lock_all_legions(self):
        self.data[self.OFFSETS["legions_mask"]] = 0x00

    def unlock_guild(self):
        self.data[self.OFFSETS["legions_mask"]] = 0x01

    def unlock_malice(self):
        self.data[self.OFFSETS["legions_mask"]] |= 0x04

    def unlock_blasphemous(self):
        self.data[self.OFFSETS["legions_mask"]] = 0x77

    def unlock_arrogance(self):
        self.data[self.OFFSETS["legions_mask"]] = 0x77

    def unlock_flawed(self):
        self.data[self.OFFSETS["legions_mask"]] = 0x77

    def unlock_hatred(self):
        self.data[self.OFFSETS["legions_mask"]] |= 0x02#0x07

    def unlock_thanatos(self):
        self.data[self.OFFSETS["legions_mask"]] = 0xF7

    # Level legion set by 00 - 30
    def set_thanatos_level(self, lvl): 
        self.data[self.OFFSETS["thanatos_exp"]] = lvl

    # Game Level

    def get_game_level_target(self):
        return LevelTarget(
        name="Stage",
        get_stage=self.get_current_stage,
        set_stage=self.set_current_stage,
        icon_key="game_stage"
    )

    def get_current_stage(self) -> int:
        if not self.data:
            return 0
        return self.data[self.OFFSETS["current_level"]]

    def set_current_stage(self, lvl: int):
        if not self.data:
            return 0
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
            name="Empty",
            max_level=None,
            is_unlocked=self.all_legions_locked,
            unlock=self.lock_all_legions
        ),
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
            name="Blasphemous",
            max_level=None,
            is_unlocked=self.blasphemous_unlocked,
            unlock=self.unlock_blasphemous
        ),
        Legion(
            name="Arrogance",
            max_level=None,
            is_unlocked=self.arrogance_unlocked,
            unlock=self.unlock_arrogance
        ),
        Legion(
            name="Flawed",
            max_level=None,
            is_unlocked=self.flawed_unlocked,
            unlock=self.unlock_flawed
        ),
        Legion(
            name="Hatred",
            max_level=None,
            is_unlocked=self.hatred_unlocked,
            unlock=self.unlock_hatred
        ),
        Legion(
            name="Thanatos",
            max_level=3,
            is_unlocked=self.thanatos_unlocked,
            unlock=self.unlock_thanatos,
            #set_level=self.set_thanatos_level()
        )
    ]
