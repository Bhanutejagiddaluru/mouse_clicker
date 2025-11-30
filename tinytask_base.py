from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from pynput.mouse import Listener as MouseListener, Controller as MouseController, Button
from pynput.keyboard import Listener as KeyListener, Key, Controller as KeyController
import time
import threading
import sys
import json

mouse = MouseController()
keyboard = KeyController()

events = []
recording = False
playing = False


### ============================
### EMERGENCY STOP (ESC)
### ============================
def emergency_stop_listener(key):
    global recording, playing
    if key == Key.esc:
        print("⚠ ESC pressed → Emergency STOP")
        recording = False
        playing = False
        return False


### ============================
### RECORDING
### ============================
def on_mouse_click(x, y, button, pressed):
    if recording:
        events.append(("click", x, y, str(button), pressed, time.time()))

def on_mouse_move(x, y):
    if recording:
        events.append(("move", x, y, None, None, time.time()))

def on_key_press(key):
    if recording:
        events.append(("key", str(key), None, None, None, time.time()))

def start_recording():
    global recording, events
    events = []
    recording = True
    print("🔴 Recording started")

    MouseListener(on_click=on_mouse_click, on_move=on_mouse_move).start()
    KeyListener(on_press=on_key_press).start()

def stop_recording():
    global recording
    recording = False
    print("⛔ Recording stopped | Total events:", len(events))


### ============================
### PLAYBACK
### ============================
def playback():
    global playing

    if not events:
        print("⚠ No events recorded!")
        playing = False
        return

    playing = True
    print("▶ Playback started")

    KeyListener(on_press=emergency_stop_listener).start()

    base = events[0][5]

    for event in events:
        if not playing:
            break

        action, x, y, a, b, t = event
        time.sleep(t - base)
        base = t

        if action == "move":
            mouse.position = (x, y)

        elif action == "click":
            mouse.position = (x, y)
            if b:
                mouse.press(eval(a))
            else:
                mouse.release(eval(a))

        elif action == "key":
            try:
                if "Key." in a:
                    keyname = a.replace("'", "")
                    keyobj = Key[keyname.split(".")[1]]
                    keyboard.press(keyobj)
                    keyboard.release(keyobj)
                else:
                    keyboard.type(a.replace("'", ""))
            except:
                pass

    print("⏹ Playback finished")
    playing = False

def start_playback():
    threading.Thread(target=playback, daemon=True).start()

def stop_playback():
    global playing
    playing = False
    print("⛔ Playback force-stopped")


### ============================
### SAVE & LOAD
### ============================
def save_recording(parent):
    if not events:
        QMessageBox.warning(parent, "Warning", "Nothing to save!")
        return

    filename, _ = QFileDialog.getSaveFileName(parent, "Save Recording", "", "Macro Files (*.macro)")
    if not filename:
        return

    # Convert to JSON-safe format
    json_events = []
    for e in events:
        json_events.append(list(e))

    with open(filename, "w") as f:
        json.dump(json_events, f)

    print("💾 Saved:", filename)


def load_recording(parent):
    global events

    filename, _ = QFileDialog.getOpenFileName(parent, "Load Recording", "", "Macro Files (*.macro)")
    if not filename:
        return

    with open(filename, "r") as f:
        loaded = json.load(f)

    events = [tuple(e) for e in loaded]
    print("📂 Loaded recording | Events:", len(events))


### ============================
### UI
### ============================
class TinyTaskUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TinyTask Clone")
        self.setFixedSize(430, 200)
        self.setWindowFlags(Qt.Tool)

        ### MENU BAR ###
        menubar = self.menuBar()

        ### File Menu ###
        file_menu = menubar.addMenu("File")

        save_action = QAction("Save Recording", self)
        save_action.triggered.connect(lambda: save_recording(self))
        file_menu.addAction(save_action)

        load_action = QAction("Load Recording", self)
        load_action.triggered.connect(lambda: load_recording(self))
        file_menu.addAction(load_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        ### Options & Settings (empty for now) ###
        menubar.addMenu("Options")
        menubar.addMenu("Settings")

        ### TOOLBAR ###
        widget = QWidget()
        layout = QVBoxLayout()

        row = QHBoxLayout()

        btn_play = QPushButton("▶ Play")
        btn_play.clicked.connect(start_playback)
        row.addWidget(btn_play)

        btn_start_rec = QPushButton("● Start Recording")
        btn_start_rec.clicked.connect(start_recording)
        row.addWidget(btn_start_rec)

        btn_stop_rec = QPushButton("■ Stop Recording")
        btn_stop_rec.clicked.connect(stop_recording)
        row.addWidget(btn_stop_rec)

        btn_stop_play = QPushButton("⏹ Stop Playback")
        btn_stop_play.clicked.connect(stop_playback)
        row.addWidget(btn_stop_play)

        layout.addLayout(row)
        widget.setLayout(layout)
        self.setCentralWidget(widget)


### ============================
### APP START
### ============================
app = QApplication(sys.argv)
ui = TinyTaskUI()
ui.show()
sys.exit(app.exec_())
