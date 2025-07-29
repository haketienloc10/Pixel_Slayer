import sys
import os
import signal
import random
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QMovie, QScreen, QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize
from pynput import keyboard

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# --- CẤU HÌNH ỨNG DỤNG ---
CONFIG = {
    "position": "random",
    "target_gif_size": (200, 200),
    "gif_overlap_px": 100, 
    "display_mode": "single", # Chế độ hiển thị: 'single' hoặc 'double'
}
# -------------------------

class SignalBridge(QObject):
    keyPressed = pyqtSignal()

class GIFPlayer(QWidget):
    def __init__(self, signal_bridge):
        super().__init__()
        self.signal_bridge = signal_bridge
        self.is_playing = False

        self.left_dir = os.path.join(SCRIPT_DIRECTORY, "assets", "left")
        self.right_dir = os.path.join(SCRIPT_DIRECTORY, "assets", "right")

        self.left_gifs = [f for f in os.listdir(self.left_dir) if f.endswith('.gif')]
        self.right_gifs = [f for f in os.listdir(self.right_dir) if f.endswith('.gif')]
        self.all_gifs = self.left_gifs + self.right_gifs

        if not self.all_gifs:
            print(f"Lỗi: Không tìm thấy file GIF nào trong thư mục '{self.left_dir}' hoặc '{self.right_dir}'")
            sys.exit(1)

        self.shutdown_timer = QTimer()
        self.init_ui()
        self.connect_signals()

    def _update_gif_and_window_size(self, movie, label):
        target_size_config = CONFIG.get("target_gif_size")
        movie.jumpToFrame(0)
        original_size = movie.frameRect().size()

        if not original_size.isValid():
            return QSize(0, 0)

        if target_size_config:
            target_size = QSize(*target_size_config)
            scaled_size = original_size.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio)
            label.setFixedSize(scaled_size)
            return scaled_size
        else:
            label.setFixedSize(original_size)
            return original_size

    def change_gifs(self):
        """Chọn một hoặc hai GIF tùy theo chế độ và cập nhật kích thước."""
        self.movie1.stop()
        self.movie2.stop()

        mode = CONFIG.get("display_mode", "single")

        if mode == 'single':
            self.label2.hide()

            # 1. Ngẫu nhiên chọn thư mục (left hoặc right)
            if random.choice([True, False]):
                source_dir, source_list = self.left_dir, self.left_gifs
            else:
                source_dir, source_list = self.right_dir, self.right_gifs
            
            # Đảm bảo danh sách đã chọn không rỗng
            if not source_list:
                source_dir = self.right_dir if source_dir == self.left_dir else self.left_dir
                source_list = self.right_gifs if source_dir == self.right_dir else self.left_gifs

            gif_name = random.choice(source_list)
            gif_path = os.path.join(source_dir, gif_name)

            # 2. Ngẫu nhiên quyết định có lật ngược hay không
            self.movie1_is_flipped = random.choice([True, False])

            self.movie1.setFileName(gif_path)
            size = self._update_gif_and_window_size(self.movie1, self.label1)
            self.setFixedSize(size)
            self.label1.move(0, 0)

        else: # Chế độ 'double'
            self.label2.show()
            if random.choice([True, False]) and self.right_gifs:
                gif1_source_dir, gif1_list, self.movie1_is_flipped = self.right_dir, self.right_gifs, True
            else:
                gif1_source_dir, gif1_list, self.movie1_is_flipped = self.left_dir, self.left_gifs, False

            if random.choice([True, False]) and self.left_gifs:
                gif2_source_dir, gif2_list, self.movie2_is_flipped = self.left_dir, self.left_gifs, True
            else:
                gif2_source_dir, gif2_list, self.movie2_is_flipped = self.right_dir, self.right_gifs, False

            gif1_name = random.choice(gif1_list)
            gif2_name = random.choice(gif2_list)

            if gif1_source_dir == gif2_source_dir and len(gif1_list) > 1:
                while gif2_name == gif1_name:
                    gif2_name = random.choice(gif2_list)

            self.movie1.setFileName(os.path.join(gif1_source_dir, gif1_name))
            self.movie2.setFileName(os.path.join(gif2_source_dir, gif2_name))

            size1 = self._update_gif_and_window_size(self.movie1, self.label1)
            size2 = self._update_gif_and_window_size(self.movie2, self.label2)

            overlap = CONFIG.get("gif_overlap_px", 0)
            total_width = size1.width() + size2.width() - overlap
            max_height = max(size1.height(), size2.height())
            self.setFixedSize(total_width, max_height)

            y1_pos = (max_height - size1.height()) // 2
            y2_pos = (max_height - size2.height()) // 2
            self.label1.move(0, y1_pos)
            self.label2.move(size1.width() - overlap, y2_pos)

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label1 = QLabel(self)
        self.movie1 = QMovie(self)
        self.movie1_is_flipped = False

        self.label2 = QLabel(self)
        self.movie2 = QMovie(self)
        self.movie2_is_flipped = False

        self.change_gifs()
        self.hide()

    def connect_signals(self):
        self.signal_bridge.keyPressed.connect(self.handle_key_press)
        self.movie1.frameChanged.connect(self.update_frame)
        self.movie2.frameChanged.connect(self.update_frame)

    def update_frame(self, frame_number):
        movie = self.sender()
        if movie == self.movie1:
            label, is_flipped = self.label1, self.movie1_is_flipped
        elif movie == self.movie2:
            label, is_flipped = self.label2, self.movie2_is_flipped
        else: return

        pixmap = movie.currentPixmap()
        if is_flipped:
            image = pixmap.toImage()
            mirrored_image = image.mirrored(True, False)
            pixmap = QPixmap.fromImage(mirrored_image)
        
        scaled_pixmap = pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(scaled_pixmap)

        if movie.frameCount() > 0 and frame_number == movie.frameCount() - 1:
            self.on_gif_finished()

    def position_window(self):
        primary_screen = QApplication.primaryScreen()
        if not primary_screen: return
        screen_geometry = primary_screen.availableGeometry()
        win_width, win_height = self.width(), self.height()
        x = random.randint(0, screen_geometry.width() - win_width)
        y = random.randint(0, screen_geometry.height() - win_height)
        self.move(x, y)

    def show_gifs(self):
        self.change_gifs()
        self.position_window()
        self.show()
        self.movie1.start()
        if CONFIG.get("display_mode") == 'double':
            self.movie2.start()

    def on_gif_finished(self):
        if not self.is_playing: return
        self.is_playing = False
        self.movie1.stop()
        self.movie2.stop()
        self.hide()

    def handle_key_press(self):
        if self.is_playing: return
        self.is_playing = True
        self.show_gifs()

def main():
    app = QApplication(sys.argv)
    signal_bridge = SignalBridge()
    player = GIFPlayer(signal_bridge)
    
    def on_press(key):
        signal_bridge.keyPressed.emit()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    
    def shutdown_handler(sig, frame):
        print("\nĐã đóng chương trình...")
        listener.stop()
        QApplication.instance().quit()

    signal.signal(signal.SIGINT, shutdown_handler)

    player.shutdown_timer.start(500)
    player.shutdown_timer.timeout.connect(lambda: None)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()