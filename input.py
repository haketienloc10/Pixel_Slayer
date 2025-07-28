from typing import Optional

from pynput import keyboard
from PyQt6.QtCore import QObject, pyqtSignal


class Communicate(QObject):
    """Communicates between the keyboard listener and the GUI thread.

    Attributes:
        key_pressed (pyqtSignal): Signal emitted when a key is pressed.
    """

    key_pressed: pyqtSignal = pyqtSignal()


def key_listener_thread(comm: Communicate) -> None:
    """Listens for global key presses in a separate thread.

    Args:
        comm (Communicate): The communication object to signal key presses.
    """

    def on_press(key: Optional[keyboard.Key | keyboard.KeyCode]) -> None:
        """Callback function for key presses."""
        comm.key_pressed.emit()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
