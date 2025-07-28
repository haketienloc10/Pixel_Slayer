
import sys
import os
import threading
from pynput import keyboard

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap, QMouseEvent, QMovie
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject, QTimer

# --- Cấu hình ---
LEVEL_2_THRESHOLD = 50  # Giảm xuống để test cho nhanh
ASSET_DIR = "assets"

class Communicate(QObject):
    """Dùng để giao tiếp an toàn giữa luồng pynput và luồng GUI PyQt."""
    key_pressed = pyqtSignal()

class PixelSlayerWidget(QWidget):
    def __init__(self, comm):
        super().__init__()
        self.comm = comm
        self.attack_count = 0
        self.current_level = 1
        self.old_pos = QPoint()

        # --- Định nghĩa các bộ sprite cho các cấp ---
        self.character_sprites = {
            1: {"idle": "warrior_lv1_idle.png", "attack": "warrior_lv1_attack.png"},
            2: {"idle": "warrior_lv2_idle.png", "attack": "warrior_lv2_attack.png"},
        }
        self.monster_sprites = {
            1: {"idle": "monster_lv1_idle.png", "hurt": "monster_lv1_hurt.png"},
            2: {"idle": "monster_lv2_idle.png", "hurt": "monster_lv2_hurt.png"},
        }

        self.init_ui()
        self.comm.key_pressed.connect(self.handle_attack)

    def init_ui(self):
        """Khởi tạo giao diện người dùng."""
        # --- Thiết lập cửa sổ ---
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |       # Không có viền
            Qt.WindowType.WindowStaysOnTopHint |      # Luôn ở trên cùng
            Qt.WindowType.Tool                        # Không hiển thị trên taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) # Nền trong suốt
        self.setGeometry(100, 100, 200, 150) # Vị trí và kích thước ban đầu

        # --- Layout và các thành phần ---
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Label hiển thị nhân vật
        self.character_label = QLabel(self)
        self.character_pixmap_idle = QPixmap(os.path.join(ASSET_DIR, self.character_sprites[self.current_level]["idle"]))
        self.character_pixmap_attack = QPixmap(os.path.join(ASSET_DIR, self.character_sprites[self.current_level]["attack"]))
        self.character_label.setPixmap(self.character_pixmap_idle)
        self.character_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label hiển thị quái vật
        self.monster_label = QLabel(self)
        self.monster_pixmap_idle = QPixmap(os.path.join(ASSET_DIR, self.monster_sprites[self.current_level]["idle"]))
        self.monster_pixmap_hurt = QPixmap(os.path.join(ASSET_DIR, self.monster_sprites[self.current_level]["hurt"]))
        self.monster_label.setPixmap(self.monster_pixmap_idle)
        self.monster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label hiển thị bộ đếm
        self.counter_label = QLabel(f"Attacks: {self.attack_count}", self)
        self.counter_label.setStyleSheet("color: white; font-weight: bold; background-color: rgba(0,0,0,150); padding: 2px;")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Thêm vào layout
        self.layout.addWidget(self.monster_label)
        self.layout.addWidget(self.character_label)
        self.layout.addWidget(self.counter_label)

        self.show()

    def handle_attack(self):
        """Xử lý logic khi có phím được nhấn."""
        self.attack_count += 1
        self.counter_label.setText(f"Attacks: {self.attack_count}")

        # --- Hoạt ảnh tấn công ---
        self.character_label.setPixmap(self.character_pixmap_attack)
        self.monster_label.setPixmap(self.monster_pixmap_hurt)

        # Dùng QTimer để quay về trạng thái đứng yên sau 100ms
        QTimer.singleShot(100, self.reset_sprites)

        # --- Kiểm tra tiến hóa ---
        if self.current_level == 1 and self.attack_count >= LEVEL_2_THRESHOLD:
            self.evolve()

    def reset_sprites(self):
        """Phục hồi sprite về trạng thái đứng yên."""
        self.character_label.setPixmap(self.character_pixmap_idle)
        self.monster_label.setPixmap(self.monster_pixmap_idle)

    def evolve(self):
        """Xử lý logic tiến hóa."""
        self.current_level = 2
        print("EVOLVED!") # In ra console để debug

        # Cập nhật lại pixmap cho cấp độ mới
        self.character_pixmap_idle = QPixmap(os.path.join(ASSET_DIR, self.character_sprites[self.current_level]["idle"]))
        self.character_pixmap_attack = QPixmap(os.path.join(ASSET_DIR, self.character_sprites[self.current_level]["attack"]))
        self.monster_pixmap_idle = QPixmap(os.path.join(ASSET_DIR, self.monster_sprites[self.current_level]["idle"]))
        self.monster_pixmap_hurt = QPixmap(os.path.join(ASSET_DIR, self.monster_sprites[self.current_level]["hurt"]))

        # Cập nhật ảnh hiển thị
        self.reset_sprites()
        # Có thể thêm hiệu ứng đặc biệt ở đây
        self.counter_label.setText(f"EVOLVED! Attacks: {self.attack_count}")
        self.counter_label.setStyleSheet("color: yellow; font-weight: bold; background-color: rgba(0,100,0,200); padding: 2px;")


    # --- Các hàm để kéo thả cửa sổ ---
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

def key_listener_thread(comm: Communicate):
    """Luồng này chạy ngầm để lắng nghe sự kiện gõ phím toàn hệ thống."""
    def on_press(key):
        # Gửi tín hiệu tới luồng chính một cách an toàn
        comm.key_pressed.emit()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def main():
    app = QApplication(sys.argv)
    
    # Tạo đối tượng giao tiếp
    comm = Communicate()

    # Khởi tạo widget
    widget = PixelSlayerWidget(comm)

    # Bắt đầu luồng lắng nghe phím
    listener_thread = threading.Thread(target=key_listener_thread, args=(comm,), daemon=True)
    listener_thread.start()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
