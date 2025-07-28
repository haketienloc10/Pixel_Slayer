import sys
import os
import threading
from pynput import keyboard

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap, QMouseEvent, QMovie
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject, QTimer

# --- Constants ---
LEVEL_2_THRESHOLD = 50
ASSET_DIR = "assets"

# --- Sprite Definitions ---
SPRITES = {
    "character": {
        1: {"idle": "warrior_lv1_idle.png", "attack": "warrior_lv1_attack.png"},
        2: {"idle": "warrior_lv2_idle.png", "attack": "warrior_lv2_attack.png"},
    },
    "monster": {
        1: {"idle": "monster_lv1_idle.png", "hurt": "monster_lv1_hurt.png"},
        2: {"idle": "monster_lv2_idle.png", "hurt": "monster_lv2_hurt.png"},
    }
}

class GameLogic(QObject):
    """Handles the game's logic, such as attack counts and level progression."""
    level_changed = pyqtSignal(int)
    attack_count_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.attack_count = 0
        self.current_level = 1

    def increment_attack(self):
        self.attack_count += 1
        self.attack_count_changed.emit(self.attack_count)
        if self.current_level == 1 and self.attack_count >= LEVEL_2_THRESHOLD:
            self.evolve()

    def evolve(self):
        self.current_level = 2
        self.level_changed.emit(self.current_level)

class PixelSlayerWidget(QWidget):
    """Main application widget."""
    def __init__(self, comm, game_logic):
        super().__init__()
        self.comm = comm
        self.game_logic = game_logic
        self.pixmaps = {}
        self.movies = {}
        self.old_pos = QPoint()

        self.load_assets()
        self.init_ui()

        # --- Connect signals ---
        self.comm.key_pressed.connect(self.handle_attack)
        self.game_logic.level_changed.connect(self.on_level_changed)
        self.game_logic.attack_count_changed.connect(self.on_attack_count_changed)


    def load_assets(self):
        """Pre-loads all necessary sprites (images and GIFs)."""
        for category, levels in SPRITES.items():
            self.pixmaps[category] = {}
            self.movies[category] = {}
            for level, states in levels.items():
                self.pixmaps[category][level] = {}
                self.movies[category][level] = {}
                for state, filename in states.items():
                    path = os.path.join(ASSET_DIR, filename)
                    if not os.path.exists(path):
                        print(f"Error: Asset not found at {path}")
                        sys.exit(1) # Exit if essential asset is missing

                    if filename.endswith(".gif"):
                        movie = QMovie(path)
                        self.movies[category][level][state] = movie
                    else:
                        pixmap = QPixmap(path)
                        self.pixmaps[category][level][state] = pixmap


    def init_ui(self):
        """Initializes the user interface."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 200, 150)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.character_label = QLabel(self)
        self.monster_label = QLabel(self)
        self.counter_label = QLabel("Attacks: 0", self)
        self.counter_label.setStyleSheet("color: white; font-weight: bold; background-color: rgba(0,0,0,150); padding: 2px;")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.monster_label)
        self.layout.addWidget(self.character_label)
        self.layout.addWidget(self.counter_label)

        self.reset_sprites()
        self.show()

    def set_sprite(self, label, category, level, state):
        """Sets the appropriate pixmap or movie on a label."""
        if state in self.movies[category][level]:
            label.setMovie(self.movies[category][level][state])
            self.movies[category][level][state].start()
        elif state in self.pixmaps[category][level]:
            label.setPixmap(self.pixmaps[category][level][state])


    def handle_attack(self):
        """Handles the attack logic."""
        self.game_logic.increment_attack()
        self.set_sprite(self.character_label, "character", self.game_logic.current_level, "attack")
        self.set_sprite(self.monster_label, "monster", self.game_logic.current_level, "hurt")
        QTimer.singleShot(150, self.reset_sprites)


    def reset_sprites(self):
        """Resets sprites to their idle state."""
        self.set_sprite(self.character_label, "character", self.game_logic.current_level, "idle")
        self.set_sprite(self.monster_label, "monster", self.game_logic.current_level, "idle")

    def on_level_changed(self, level):
        """Updates UI when the level changes."""
        print(f"EVOLVED to Level {level}!")
        self.reset_sprites()
        self.counter_label.setText(f"EVOLVED! Attacks: {self.game_logic.attack_count}")
        self.counter_label.setStyleSheet("color: yellow; font-weight: bold; background-color: rgba(0,100,0,200); padding: 2px;")

    def on_attack_count_changed(self, count):
        """Updates the counter label."""
        if self.game_logic.current_level == 1:
            self.counter_label.setText(f"Attacks: {count}")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()


class Communicate(QObject):
    """Communicates between the keyboard listener and the GUI thread."""
    key_pressed = pyqtSignal()

def key_listener_thread(comm: Communicate):
    """Listens for global key presses in a separate thread."""
    def on_press(key):
        comm.key_pressed.emit()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def main():
    app = QApplication(sys.argv)
    comm = Communicate()
    game_logic = GameLogic()
    widget = PixelSlayerWidget(comm, game_logic)

    listener = threading.Thread(target=key_listener_thread, args=(comm,), daemon=True)
    listener.start()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()