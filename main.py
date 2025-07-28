import sys
import threading

from PyQt6.QtWidgets import QApplication

from app import PixelSlayerWidget
from logic import GameLogic
from input import Communicate, key_listener_thread


def main() -> None:
    """Main function to run the application."""
    app = QApplication(sys.argv)
    comm = Communicate()
    game_logic = GameLogic()
    _ = PixelSlayerWidget(comm, game_logic)

    listener = threading.Thread(
        target=key_listener_thread, args=(comm,), daemon=True
    )
    listener.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()