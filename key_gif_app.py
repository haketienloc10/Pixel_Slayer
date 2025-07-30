import sys
import os
import signal
import random
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QMovie, QScreen, QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize
from pynput import keyboard, mouse

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# --- CẤU HÌNH ỨNG DỤNG ---
CONFIG = {
    "position": "bottom",
    "target_gif_size": (200, 200),
}
# -------------------------

class SignalBridge(QObject):
    activationRequired = pyqtSignal()

class MoviePlayer(QObject):
    frameChanged = pyqtSignal(QPixmap)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next_frame)
        self.frames = []
        self.current_frame_index = 0
        self.frame_delay = 50  # ms

    def set_frames(self, frames, delay):
        self.frames = frames
        self.frame_delay = delay if delay > 0 else 50
        self.current_frame_index = 0

    def start(self):
        if not self.frames:
            return
        self.current_frame_index = 0
        self.timer.start(self.frame_delay)
        self.show_next_frame()

    def stop(self):
        self.timer.stop()
        self.frames = []

    def show_next_frame(self):
        if not self.frames:
            self.timer.stop()
            return

        pixmap = self.frames[self.current_frame_index]
        self.frameChanged.emit(pixmap)

        self.current_frame_index += 1
        if self.current_frame_index >= len(self.frames):
            self.timer.stop()
            self.finished.emit()


class GIFPlayer(QWidget):
    def __init__(self, signal_bridge):
        super().__init__()
        self.signal_bridge = signal_bridge
        self.is_playing = False
        self.pixmap_cache = {}

        self.assets_dir = os.path.join(SCRIPT_DIRECTORY, "assets")
        self.gifs = [f for f in os.listdir(self.assets_dir) if f.endswith('.gif')]

        if not self.gifs:
            print(f"Lỗi: Không tìm thấy file GIF nào trong '{self.assets_dir}'")
            sys.exit(1)

        self.init_ui()
        self.connect_signals()

    def _get_cached_movie_frames(self, gif_path, target_size_tuple, is_flipped):
        target_size = QSize(*target_size_tuple)
        cache_key = (gif_path, target_size_tuple, is_flipped)
        if cache_key in self.pixmap_cache:
            return self.pixmap_cache[cache_key]

        movie = QMovie(gif_path)
        if not movie.isValid():
            return [], 0, QSize(0, 0)

        movie.setCacheMode(QMovie.CacheMode.CacheAll)
        movie.jumpToFrame(0)
        
        original_size = movie.frameRect().size()
        if not original_size.isValid():
            return [], 0, QSize(0, 0)

        scaled_size = original_size.scaled(target_size, Qt.AspectRatioMode.KeepAspectRatio)
        delay = movie.nextFrameDelay()

        processed_frames = []
        for i in range(movie.frameCount()):
            movie.jumpToFrame(i);
            pixmap = movie.currentPixmap()
            if is_flipped:
                image = pixmap.toImage()
                mirrored_image = image.mirrored(True, False)
                pixmap = QPixmap.fromImage(mirrored_image)
            
            scaled_pixmap = pixmap.scaled(scaled_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            processed_frames.append(scaled_pixmap)

        self.pixmap_cache[cache_key] = (processed_frames, delay, scaled_size)
        return processed_frames, delay, scaled_size

    def _setup_movie_player(self, movie_player, label, gif_path, is_flipped):
        target_size_config = CONFIG.get("target_gif_size", (200, 200))
        frames, delay, scaled_size = self._get_cached_movie_frames(gif_path, target_size_config, is_flipped)

        if not frames:
            return QSize(0, 0)

        label.setFixedSize(scaled_size)
        movie_player.set_frames(frames, delay)
        return scaled_size

    def change_gifs(self):
        if self.is_playing:
            return

        self.is_playing = True
        self.movie_player.stop()

        gif_name = random.choice(self.gifs)
        gif_path = os.path.join(self.assets_dir, gif_name)
        is_flipped = random.choice([True, False])

        size = self._setup_movie_player(self.movie_player, self.label, gif_path, is_flipped)
        self.setFixedSize(size)
        self.label.move(0, 0)
        self.show_gifs()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.movie_player = MoviePlayer(self)
        
        self.hide()

    def connect_signals(self):
        self.signal_bridge.activationRequired.connect(self.handle_activation_request)
        self.movie_player.frameChanged.connect(self.label.setPixmap)
        self.movie_player.finished.connect(self.on_gif_finished)

    def position_window(self):
        primary_screen = QApplication.primaryScreen()
        if not primary_screen: return
        screen_geometry = primary_screen.availableGeometry()
        win_width, win_height = self.width(), self.height()
        
        position = CONFIG.get("position", "random").lower()
        
        if position == "random":
            x = random.randint(0, screen_geometry.width() - win_width)
            y = random.randint(0, screen_geometry.height() - win_height)
        elif position == "top":
            x = random.randint(0, screen_geometry.width() - win_width)
            y = 0
        elif position == "bottom":
            x = random.randint(0, screen_geometry.width() - win_width)
            y = screen_geometry.height() - win_height
        elif position == "left":
            x = 0
            y = random.randint(0, screen_geometry.height() - win_height)
        elif position == "right":
            x = screen_geometry.width() - win_width
            y = random.randint(0, screen_geometry.height() - win_height)
        elif position == "center":
            # Cho phép một chút ngẫu nhiên xung quanh vị trí giữa
            center_x = (screen_geometry.width() - win_width) // 2
            center_y = (screen_geometry.height() - win_height) // 2
            x = center_x + random.randint(-50, 50)
            y = center_y + random.randint(-50, 50)
            # Đảm bảo không vượt ra ngoài màn hình
            x = max(0, min(x, screen_geometry.width() - win_width))
            y = max(0, min(y, screen_geometry.height() - win_height))
        else:  # default to random if invalid position
            x = random.randint(0, screen_geometry.width() - win_width)
            y = random.randint(0, screen_geometry.height() - win_height)
            
        self.move(x, y)

    def show_gifs(self):
        self.change_gifs()
        self.position_window()
        self.show()
        self.movie_player.start()

    def on_gif_finished(self):
        if not self.is_playing: return
        self.is_playing = False
        self.hide()

    def handle_activation_request(self):
        self.change_gifs()

def main():
    app = QApplication(sys.argv)
    signal_bridge = SignalBridge()
    player = GIFPlayer(signal_bridge)

    def on_press(key):
        signal_bridge.activationRequired.emit()

    def on_click(x, y, button, pressed):
        if button == mouse.Button.left and pressed:
            signal_bridge.activationRequired.emit()

    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener.start()
    mouse_listener.start()

    def shutdown_handler(sig, frame):
        print("\nĐã đóng chương trình...")
        keyboard_listener.stop()
        mouse_listener.stop()
        QApplication.instance().quit()

    signal.signal(signal.SIGINT, shutdown_handler)
    
    # This is a trick to make Python's signal handler work with PyQt
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
