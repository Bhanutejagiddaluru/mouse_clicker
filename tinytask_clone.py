from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from pynput.mouse import Listener as MouseListener, Controller as MouseController, Button
from pynput.keyboard import Listener as KeyListener, Key, Controller as KeyController
import time
import threading
import sys

mouse = MouseController()
keyboard = KeyController()

events = []
recording = False
playing = False

# Emergency stop key
def stop_key_listener(key):
    global playing, recording
    if key == Key.esc:
        print("ESC pressed → Emergency STOP")
        recording = False
        playing = False
        return False


### ================================
### RECORDING
### ================================
def on_click(x, y, button, pressed):
    if recording:
        events.append(("click", x, y, button, pressed, time.time()))

def on_move(x, y):
    if recording:
        events.append(("move", x, y, None, None, time.time()))

def on_key_press(key):
    if recording:
        events.append(("key", key, None, None, None, time.time()))


def start_recording():
    global recording, events
    events = []
    recording = True

    print("🔴 Recording started")

    # Listeners run in background threads
    MouseListener(on_click=on_click, on_move=on_move).start()
    KeyListener(on_press=on_key_press).start()


def stop_recording():
    global recording
    recording = False
    print("🛑 Recording stopped")
    print("Events recorded:", len(events))


### ================================
### PLAYBACK
### ================================
def playback():
    global playing
    playing = True

    if not events:
        print("⚠ No events recorded!")
        playing = False
        return

    print("▶ Playback started")

    # Start emergency ESC listener
    KeyListener(on_press=stop_key_listener).start()

    base = events[0][5]

    for event in events:
        if not playing:
            break

        action, x, y, a, b, t = event

        # sleep according to original timing
        time.sleep(t - base)
        base = t

        if action == "move":
            mouse.position = (x, y)

        elif action == "click":
            mouse.position = (x, y)
            if b:
                mouse.press(a)
            else:
                mouse.release(a)

        elif action == "key":
            try:
                if isinstance(x, Key):
                    keyboard.press(x)
                    keyboard.release(x)
                else:
                    keyboard.type(x.char)
            except:
                pass

    print("⏹ Playback finished")
    playing = False


def start_playback():
    threading.Thread(target=playback, daemon=True).start()


### ================================
### UI
### ================================
class UI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TinyTask Safe Clone")
        self.setFixedSize(260, 150)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)

        layout = QVBoxLayout()

        self.btn_record = QPushButton("🔴 Start Recording")
        self.btn_stop_record = QPushButton("🛑 Stop Recording")
        self.btn_play = QPushButton("▶ Play Once")
        self.btn_stop_play = QPushButton("⏹ Stop Playback")

        self.btn_record.clicked.connect(start_recording)
        self.btn_stop_record.clicked.connect(stop_recording)
        self.btn_play.clicked.connect(start_playback)
        self.btn_stop_play.clicked.connect(self.force_stop)

        layout.addWidget(self.btn_record)
        layout.addWidget(self.btn_stop_record)
        layout.addWidget(self.btn_play)
        layout.addWidget(self.btn_stop_play)

        self.setLayout(layout)

    def force_stop(self):
        global playing, recording
        playing = False
        recording = False
        print("⛔ Force stop clicked")


### ================================
### APP START
### ================================
app = QApplication(sys.argv)
window = UI()
window.show()
sys.exit(app.exec_())
