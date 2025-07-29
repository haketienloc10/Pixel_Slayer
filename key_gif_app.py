import sys
import os
import signal # THÊM DÒNG NÀY
import random
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QMovie, QMouseEvent, QScreen
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from pynput import keyboard

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# --- CẤU HÌNH ỨNG DỤNG ---
CONFIG = {
    "gif_path": os.path.join(SCRIPT_DIRECTORY, "assets", "axe.gif"),
    "position": "random",
    "hide_delay_ms": 500,
    "gif_size": (150, 150),
}
# -------------------------

class SignalBridge(QObject):
    keyPressed = pyqtSignal()
    keyReleased = pyqtSignal()

class GIFPlayer(QWidget):
    # ... (Toàn bộ nội dung của lớp GIFPlayer giữ nguyên như cũ)
    def __init__(self, signal_bridge):
        super().__init__()
        self.signal_bridge = signal_bridge
        self.hide_timer = QTimer(self)
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.movie = QMovie(self)
        self.label.setMovie(self.movie)

        gif_path = CONFIG["gif_path"]
        if not os.path.exists(gif_path):
            print(f"Lỗi: Không tìm thấy file GIF tại '{gif_path}'")
            print("Vui lòng kiểm tra lại đường dẫn trong mục CONFIG.")
            sys.exit(1)

        self.movie.setFileName(gif_path)
        
        if CONFIG["gif_size"]:
            width, height = CONFIG["gif_size"]
            self.movie.setScaledSize(self.sizeHint().scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio))
            self.setFixedSize(width, height)
            self.label.setFixedSize(width, height)
        else:
            self.movie.jumpToFrame(0)
            self.setFixedSize(self.movie.frameRect().size())
            self.label.setFixedSize(self.movie.frameRect().size())

        self.position_window()
        # Cửa sổ sẽ ẩn cho đến khi phím được nhấn lần đầu.
        # Chạy và dừng GIF một lần để tính toán kích thước cửa sổ chính xác.
        self.movie.start()
        self.movie.stop()
        self.movie.jumpToFrame(0)
        
    def connect_signals(self):
        self.signal_bridge.keyPressed.connect(self.handle_key_press)
        self.signal_bridge.keyReleased.connect(self.handle_key_release)
        self.hide_timer.timeout.connect(self.hide_gif)
        #self.hide_timer.timeout.connect(self.stop_gif)
        self.hide_timer.setSingleShot(True)

    def position_window(self):
        primary_screen = QApplication.primaryScreen()
        if not primary_screen:
            print("Lỗi: Không thể tìm thấy màn hình chính.")
            return
            
        screen_geometry = primary_screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        win_width = self.width()
        win_height = self.height()
        
        margin = 20

        pos = CONFIG["position"]
        if pos == "random":
            x = random.randint(0, screen_width - win_width)
            y = random.randint(0, screen_height - win_height)
            self.move(x, y)
        elif pos == "bottom-right":
            self.move(screen_width - win_width - margin, screen_height - win_height - margin)
        elif pos == "bottom-left":
            self.move(margin, screen_height - win_height - margin)
        elif pos == "top-right":
            self.move(screen_width - win_width - margin, margin)
        elif pos == "top-left":
            self.move(margin, margin)
        elif pos == "center":
            self.move((screen_width - win_width) // 2, (screen_height - win_height) // 2)

    def show_gif(self):
        if self.isHidden():
            self.show()
        if self.movie.state() != QMovie.MovieState.Running:
            # self.position_window() # Bỏ dòng này
            self.movie.start()

    def hide_gif(self):
        self.hide()
        self.position_window() # Thêm vào đây

    def stop_gif(self):
        self.movie.stop()
        self.movie.jumpToFrame(0)

    def handle_key_press(self):
        self.hide_timer.stop()
        self.show_gif()
        
    def handle_key_release(self):
        self.hide_timer.start(CONFIG["hide_delay_ms"])


def main():
    """Hàm chính để khởi tạo và chạy ứng dụng."""
    app = QApplication(sys.argv)
    
    signal_bridge = SignalBridge()
    player = GIFPlayer(signal_bridge)
    
    def on_press(key):
        signal_bridge.keyPressed.emit()

    def on_release(key):
        signal_bridge.keyReleased.emit()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    # --- THAY ĐỔI LỚN BẮT ĐẦU TỪ ĐÂY ---
    
    # 1. Định nghĩa hàm xử lý việc tắt chương trình
    def shutdown_handler(sig, frame):
        print("\nĐã đóng chương trình...")
        listener.stop()  # Dừng luồng nghe phím
        QApplication.instance().quit() # Yêu cầu ứng dụng Qt thoát

    # 2. Đăng ký hàm xử lý cho tín hiệu SIGINT (tín hiệu của Ctrl+C)
    signal.signal(signal.SIGINT, shutdown_handler)

    # 3. Tạo một Timer để đảm bảo luồng chính của Python có thể xử lý tín hiệu
    #    (Đây là một kỹ thuật cần thiết khi làm việc với signal và vòng lặp của Qt)
    timer = QTimer()
    timer.start(500) # Cứ 500ms, bộ xử lý tín hiệu của Python sẽ được "đánh thức"
    timer.timeout.connect(lambda: None) 

    # --- KẾT THÚC THAY ĐỔI ---
    
    # Bắt đầu vòng lặp sự kiện của ứng dụng Qt
    sys.exit(app.exec())


if __name__ == "__main__":
    main()