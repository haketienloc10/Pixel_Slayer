from PyQt6.QtCore import QObject, pyqtSignal
from config import LEVEL_2_THRESHOLD


class GameLogic(QObject):
    """Handles the game's logic, such as attack counts and level progression.

    Attributes:
        level_changed (pyqtSignal): Signal emitted when the character's level changes.
        attack_count_changed (pyqtSignal): Signal emitted when the attack count changes.
    """

    level_changed: pyqtSignal = pyqtSignal(int)
    attack_count_changed: pyqtSignal = pyqtSignal(int)

    def __init__(self) -> None:
        """Initializes the GameLogic."""
        super().__init__()
        self.attack_count: int = 0
        self.current_level: int = 1

    def increment_attack(self) -> None:
        """Increments the attack count and checks for level evolution."""
        self.attack_count += 1
        self.attack_count_changed.emit(self.attack_count)
        if self.current_level == 1 and self.attack_count >= LEVEL_2_THRESHOLD:
            self.evolve()

    def evolve(self) -> None:
        """Evolves the character to the next level."""
        self.current_level = 2
        self.level_changed.emit(self.current_level)
