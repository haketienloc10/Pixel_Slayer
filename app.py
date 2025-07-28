import sys
from collections import deque
from pathlib import Path
from typing import Deque, Dict, Optional

from PyQt6.QtCore import (QObject, QPoint, Qt, QTimer, pyqtSignal)
from PyQt6.QtGui import QMouseEvent, QMovie, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from config import ASSET_DIR, SPRITES
from logic import GameLogic
from input import Communicate


class PixelSlayerWidget(QWidget):
    """Main application widget that displays the game characters.

    This widget manages the UI, character sprites, and user interactions.
    """

    def __init__(self, comm: "Communicate", game_logic: GameLogic) -> None:
        """Initializes the PixelSlayerWidget.

        Args:
            comm (Communicate): The communication object for key presses.
            game_logic (GameLogic): The game logic handler.
        """
        super().__init__()
        self.comm: "Communicate" = comm
        self.game_logic: GameLogic = game_logic
        self.pixmaps: Dict[str, Dict[int, Dict[str, QPixmap]]] = {}
        self.movies: Dict[str, Dict[int, Dict[str, QMovie]]] = {}
        self.old_pos: QPoint = QPoint()
        self.action_queue: Deque[str] = deque()
        self.is_processing_action: bool = False

        self.load_assets()
        self.init_ui()

        # --- Connect signals ---
        self.comm.key_pressed.connect(self.queue_attack)
        self.game_logic.level_changed.connect(self.on_level_changed)
        self.game_logic.attack_count_changed.connect(self.on_attack_count_changed)

        # --- Timer for processing the action queue ---
        self.queue_timer: QTimer = QTimer(self)
        self.queue_timer.timeout.connect(self.process_action_queue)
        self.queue_timer.start(50)  # Check the queue every 50ms

    def load_assets(self) -> None:
        """Pre-loads all necessary sprites (images and GIFs)."""
        for category, levels in SPRITES.items():
            self.pixmaps[category] = {}
            self.movies[category] = {}
            for level, states in levels.items():
                self.pixmaps[category][level] = {}
                self.movies[category][level] = {}
                for state, filename in states.items():
                    path: Path = ASSET_DIR / filename
                    if not path.exists():
                        print(f"Error: Asset not found at {path}")
                        sys.exit(1)  # Exit if essential asset is missing

                    if path.suffix == ".gif":
                        movie = QMovie(str(path))
                        self.movies[category][level][state] = movie
                    else:
                        pixmap = QPixmap(str(path))
                        self.pixmaps[category][level][state] = pixmap

    def init_ui(self) -> None:
        """Initializes the user interface."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 200, 150)

        self.layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self.layout)

        self.character_label: QLabel = QLabel(self)
        self.monster_label: QLabel = QLabel(self)
        self.counter_label: QLabel = QLabel("Attacks: 0", self)
        self.counter_label.setStyleSheet(
            "color: white; font-weight: bold; background-color: rgba(0,0,0,150); padding: 2px;"
        )
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.monster_label)
        self.layout.addWidget(self.character_label)
        self.layout.addWidget(self.counter_label)

        self.reset_sprites()
        self.show()

    def set_sprite(self, label: QLabel, category: str, level: int, state: str) -> None:
        """Sets the appropriate pixmap or movie on a label.

        Args:
            label (QLabel): The label to set the sprite on.
            category (str): The category of the sprite (e.g., "character").
            level (int): The current level of the sprite.
            state (str): The state of the sprite (e.g., "idle", "attack").
        """
        if state in self.movies[category][level]:
            movie = self.movies[category][level][state]
            label.setMovie(movie)
            movie.start()
        elif state in self.pixmaps[category][level]:
            label.setPixmap(self.pixmaps[category][level][state])

    def queue_attack(self) -> None:
        """Adds an 'attack' action to the queue."""
        self.action_queue.append("attack")

    def process_action_queue(self) -> None:
        """Processes one action from the queue if not already processing."""
        if not self.is_processing_action and self.action_queue:
            action = self.action_queue.popleft()
            if action == "attack":
                self.execute_attack()

    def execute_attack(self) -> None:
        """Handles the attack logic and animation."""
        self.is_processing_action = True
        self.game_logic.increment_attack()
        self.set_sprite(
            self.character_label, "character", self.game_logic.current_level, "attack"
        )
        self.set_sprite(
            self.monster_label, "monster", self.game_logic.current_level, "hurt"
        )
        QTimer.singleShot(150, self.reset_sprites)

    def reset_sprites(self) -> None:
        """Resets sprites to their idle state and allows the next action."""
        self.set_sprite(
            self.character_label, "character", self.game_logic.current_level, "idle"
        )
        self.set_sprite(
            self.monster_label, "monster", self.game_logic.current_level, "idle"
        )
        self.is_processing_action = False

    def on_level_changed(self, level: int) -> None:
        """Updates UI when the level changes.

        Args:
            level (int): The new level.
        """
        print(f"EVOLVED to Level {level}!")
        self.reset_sprites()
        self.counter_label.setText(f"EVOLVED! Attacks: {self.game_logic.attack_count}")
        self.counter_label.setStyleSheet(
            "color: yellow; font-weight: bold; background-color: rgba(0,100,0,200); padding: 2px;"
        )

    def on_attack_count_changed(self, count: int) -> None:
        """Updates the counter label.

        Args:
            count (int): The new attack count.
        """
        if self.game_logic.current_level == 1:
            self.counter_label.setText(f"Attacks: {count}")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles mouse press events for window dragging.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handles mouse move events for window dragging.

        Args:
            event (QMouseEvent): The mouse event.
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
