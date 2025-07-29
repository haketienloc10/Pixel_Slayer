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
    "display_mode": "double", # Chế độ hiển thị: 'single' hoặc 'double'
}
# -------------------------

class SignalBridge(QObject):
    keyPressed = pyqtSignal()

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

        self.left_dir = os.path.join(SCRIPT_DIRECTORY, "assets", "left")
        self.right_dir = os.path.join(SCRIPT_DIRECTORY, "assets", "right")

        self.left_gifs = [f for f in os.listdir(self.left_dir) if f.endswith('.gif')]
        self.right_gifs = [f for f in os.listdir(self.right_dir) if f.endswith('.gif')]

        if not self.left_gifs and not self.right_gifs:
            print(f"Lỗi: Không tìm thấy file GIF nào trong '{self.left_dir}' hoặc '{self.right_dir}'")
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
        self.movie1_player.stop()
        self.movie2_player.stop()
        self.movie1_finished = False
        self.movie2_finished = False

        mode = CONFIG.get("display_mode", "single")

        if mode == 'single':
            self.label2.hide()
            use_left = random.choice([True, False])
            source_dir = self.left_dir if use_left and self.left_gifs else self.right_dir
            source_list = self.left_gifs if use_left and self.left_gifs else self.right_gifs
            
            if not source_list: # Fallback if one directory is empty
                source_dir = self.right_dir if source_dir == self.left_dir else self.left_dir
                source_list = self.right_gifs if source_dir == self.right_dir else self.left_gifs

            gif_name = random.choice(source_list)
            gif_path = os.path.join(source_dir, gif_name)
            is_flipped = random.choice([True, False])

            size = self._setup_movie_player(self.movie1_player, self.label1, gif_path, is_flipped)
            self.setFixedSize(size)
            self.label1.move(0, 0)

        else: # 'double' mode
            self.label2.show()
            
            gif1_path = os.path.join(self.left_dir, random.choice(self.left_gifs)) if self.left_gifs else ""
            gif2_path = os.path.join(self.right_dir, random.choice(self.right_gifs)) if self.right_gifs else ""
            
            if not gif1_path or not gif2_path: # Handle empty directories
                 self.change_gifs() # Retry
                 return

            size1 = self._setup_movie_player(self.movie1_player, self.label1, gif1_path, is_flipped=False)
            size2 = self._setup_movie_player(self.movie2_player, self.label2, gif2_path, is_flipped=True)

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
        self.movie1_player = MoviePlayer(self)
        self.movie1_finished = False

        self.label2 = QLabel(self)
        self.movie2_player = MoviePlayer(self)
        self.movie2_finished = False
        
        self.hide()

    def connect_signals(self):
        self.signal_bridge.keyPressed.connect(self.handle_key_press)
        self.movie1_player.frameChanged.connect(self.label1.setPixmap)
        self.movie2_player.frameChanged.connect(self.label2.setPixmap)
        self.movie1_player.finished.connect(self.on_gif1_finished)
        self.movie2_player.finished.connect(self.on_gif2_finished)

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
        self.movie1_player.start()
        if CONFIG.get("display_mode") == 'double':
            self.movie2_player.start()

    def on_gif1_finished(self):
        self.movie1_finished = True
        self.check_both_finished()

    def on_gif2_finished(self):
        self.movie2_finished = True
        self.check_both_finished()

    def check_both_finished(self):
        if not self.is_playing: return
        
        mode = CONFIG.get("display_mode", "single")
        if mode == 'single':
            if self.movie1_finished:
                self.is_playing = False
                self.hide()
        else: # double mode
            if self.movie1_finished and self.movie2_finished:
                self.is_playing = False
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
    
    # This is a trick to make Python's signal handler work with PyQt
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
