from pathlib import Path
import shutil
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class Legion:
    name: str
    bit_index: int
    max_level: Optional[int]
    is_unlocked: Callable[[], bool]
    unlock: Callable[[], None]
    lock: Callable[[], None]

@dataclass
class LevelTarget:
    name: str
    get_stage: Callable[[], int]
    set_stage: Callable[[int], None]
    icon_key: Optional[str] = None

class SaveFile:
    SAVE_SIZE = 592

    OFFSETS = {
        "legions_mask": 0x15,
        "current_level": 0x201,
        "sword_exp": (0x49, 0x4A, 0x4B),
        "thanatos_exp": (0x65, 0x66, 0x67, 0x68),
        "thanatos_level": 0x43,
    }

    LEGION_BITS = [
        ("Thanatos", 7),
        ("Blasphemy", 6),
        ("Flawed", 5),
        ("Arrogance", 4),   
        ("Null", 3),  # опасный бит
        ("Malice", 2),
        ("Hatred", 1),
        ("Guilt", 0),
    ]

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

    # ---------- Bit helpers ----------
    def _get_mask(self):
        return self.data[self.OFFSETS["legions_mask"]]

    def _set_mask(self, value):
        self.data[self.OFFSETS["legions_mask"]] = value

    def _is_bit_set(self, bit_index: int) -> bool:
        return bool(self._get_mask() & (1 << bit_index))

    def _set_bit(self, bit_index: int):
        self._set_mask(self._get_mask() | (1 << bit_index))

    def _clear_bit(self, bit_index: int):
        self._set_mask(self._get_mask() & ~(1 << bit_index))

    # ---------- Legions ----------
    def get_legions(self) -> list[Legion]:
        legions = []
        for name, bit in self.LEGION_BITS:
            legions.append(
                Legion(
                    name=name,
                    bit_index=bit,
                    max_level=3 if name == "Thanatos" else None,
                    is_unlocked=lambda b=bit: self._is_bit_set(b),
                    unlock=lambda b=bit: self._set_bit(b),
                    lock=lambda b=bit: self._clear_bit(b),
                )
            )
        return legions

    # ---------- Stage ----------
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
            return
        self.data[self.OFFSETS["current_level"]] = lvl


    

    def reset_exp(self):
        for o in self.OFFSETS["exp"]:
            self.data[o] = 0

    def reset_sword(self):
        for o in self.OFFSETS["sword_exp"]:
            self.data[o] = 0
