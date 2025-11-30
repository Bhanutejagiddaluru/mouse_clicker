import os
import json
import time
import threading
import keyboard
from pynput.mouse import Listener as MouseListener, Controller as MouseController, Button
from pynput.keyboard import Listener as KeyListener, Key, Controller as KeyController
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import sys

############################################
# PATHS
############################################

DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "mouse_click")
SHORTCUT_FILE = os.path.join(DOWNLOAD_DIR, "shortcuts.json")

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

############################################
# GLOBAL VARS
############################################

mouse = MouseController()
keyboard_controller = KeyController()

events = []
recording = False
playing = False
global_shortcuts = []  # Loaded from JSON


############################################
# MACRO RECORDING FUNCTIONS
############################################

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
    global events, recording
    events = []
    recording = True
    print("🔴 Recording started")
    MouseListener(on_click=on_mouse_click, on_move=on_mouse_move).start()
    KeyListener(on_press=on_key_press).start()

def stop_recording():
    global recording
    recording = False
    print(f"⛔ Recording stopped | {len(events)} events")


############################################
# PLAYBACK FUNCTIONS
############################################

def emergency_stop_listener(key):
    global recording, playing
    if key == Key.esc:
        print("⚠ ESC → Emergency STOP")
        playing = False
        recording = False
        return False

def playback():
    global playing

    if not events:
        print("⚠ No events to play!")
        playing = False
        return

    playing = True
    print("▶ Playback started")

    KeyListener(on_press=emergency_stop_listener).start()

    base_time = events[0][5]

    for event in events:
        if not playing:
            break

        action, x, y, a, b, t = event

        time.sleep(t - base_time)
        base_time = t

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
                    keyboard_controller.press(keyobj)
                    keyboard_controller.release(keyobj)
                else:
                    keyboard_controller.type(a.replace("'", ""))
            except:
                pass

    print("⏹ Playback finished")
    playing = False

def start_playback():
    threading.Thread(target=playback, daemon=True).start()

def stop_playback():
    global playing
    playing = False
    print("⛔ Playback force stopped")


############################################
# SAVE & LOAD MACRO
############################################

def save_macro(parent):
    if not events:
        QMessageBox.warning(parent, "Warning", "Nothing to save!")
        return

    file, _ = QFileDialog.getSaveFileName(parent, "Save Recording", DOWNLOAD_DIR, "Macro Files (*.macro)")
    if not file:
        return

    json_events = [list(e) for e in events]
    with open(file, "w") as f:
        json.dump(json_events, f)

    print("💾 Saved macro:", file)

def load_macro(file):
    global events
    with open(file, "r") as f:
        data = json.load(f)
    events = [tuple(e) for e in data]
    print("📂 Loaded macro:", file)


############################################
# GLOBAL SHORTCUT SYSTEM
############################################

def load_shortcut_config():
    global global_shortcuts
    if not os.path.exists(SHORTCUT_FILE):
        global_shortcuts = []
        return

    with open(SHORTCUT_FILE, "r") as f:
        global_shortcuts = json.load(f)

def save_shortcut_config():
    with open(SHORTCUT_FILE, "w") as f:
        json.dump(global_shortcuts, f, indent=4)

############################################
# SAFE HOTKEY MANAGER (WORKS WITH PYTHON 3.13)
############################################

registered_hotkeys = []   # store handles

def clear_all_hotkeys():
    global registered_hotkeys

    for h in registered_hotkeys:
        try:
            keyboard.remove_hotkey(h)
        except:
            pass

    registered_hotkeys = []

def register_all_hotkeys():
    global registered_hotkeys

    clear_all_hotkeys()

    for entry in global_shortcuts:
        shortcut = entry["shortcut"]
        file = os.path.join(DOWNLOAD_DIR, entry["file"])

        # function creator
        def make_play_func(file=file):
            return lambda: (
                print(f"🎯 Hotkey pressed → {shortcut} → {file}"),
                load_macro(file),
                start_playback()
            )

        # register and store handle
        try:
            handle = keyboard.add_hotkey(shortcut, make_play_func())
            registered_hotkeys.append(handle)
            print(f"🔗 Registered hotkey: {shortcut} → {file}")

        except Exception as e:
            print(f"❌ Failed to register hotkey '{shortcut}': {e}")


############################################
# SHORTCUT MANAGER UI
############################################

class ShortcutManager(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.activateWindow()
        self.raise_()
        self.setWindowTitle("Manage Shortcuts")
        self.setFixedSize(500, 350)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Shortcut", "Recording"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Load data
        self.load_table()

        # Buttons
        btn_row = QHBoxLayout()
        btn_add = QPushButton("Add Shortcut")
        btn_delete = QPushButton("Delete Selected")
        btn_save = QPushButton("Save Changes")

        btn_add.clicked.connect(self.add_shortcut)
        btn_delete.clicked.connect(self.delete_shortcut)
        btn_save.clicked.connect(self.save_changes)

        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_delete)
        btn_row.addWidget(btn_save)

        layout.addLayout(btn_row)

    def load_table(self):
        self.table.setRowCount(len(global_shortcuts))
        for row, entry in enumerate(global_shortcuts):
            self.table.setItem(row, 0, QTableWidgetItem(entry["shortcut"]))
            self.table.setItem(row, 1, QTableWidgetItem(entry["file"]))

    def add_shortcut(self):
        dlg = AddShortcutDialog()
        dlg.show()
        dlg.activateWindow()
        dlg.raise_()
        dlg.exec_()
        self.load_table()


    def delete_shortcut(self):
        selected = self.table.currentRow()
        if selected >= 0:
            del global_shortcuts[selected]
            self.load_table()

    def save_changes(self):
        new_list = []
        for row in range(self.table.rowCount()):
            shortcut = self.table.item(row, 0).text()
            file = self.table.item(row, 1).text()
            new_list.append({"shortcut": shortcut, "file": file})

        global global_shortcuts
        global_shortcuts = new_list

        save_shortcut_config()
        register_all_hotkeys()

        QMessageBox.information(self, "Saved", "Shortcuts updated!")


############################################
# DIALOG TO ADD A SHORTCUT
############################################
class AddShortcutDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Shortcut")
        self.setFixedSize(420, 230)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setModal(True)
        self.activateWindow()
        self.raise_()

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)
        self.setLayout(layout)

        title = QLabel("Create New Shortcut")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(title)

        layout.addSpacing(5)

        # ---------- Shortcut capture field ----------
        shortcut_label = QLabel("Press keys for shortcut:")
        shortcut_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(shortcut_label)

        self.keybox = QLineEdit()
        self.keybox.setPlaceholderText("Click here and press shortcut keys...")
        self.keybox.setReadOnly(True)
        self.keybox.setFixedHeight(32)
        self.keybox.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding-left: 8px;
                border: 1px solid #999;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.keybox)
        self.keybox.installEventFilter(self)

        # ---------- File selection ----------
        file_label = QLabel("Select macro file:")
        file_label.setStyleSheet("font-size: 13px; margin-top: 8px;")
        layout.addWidget(file_label)

        file_row = QHBoxLayout()
        self.file_display = QLineEdit()
        self.file_display.setReadOnly(True)
        self.file_display.setFixedHeight(32)
        self.file_display.setStyleSheet("""
            QLineEdit {
                font-size: 13px;
                padding-left: 8px;
                border: 1px solid #999;
                border-radius: 6px;
            }
        """)

        btn_choose = QPushButton("Browse")
        btn_choose.setFixedHeight(32)
        btn_choose.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                font-size: 13px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #005EA6;
            }
        """)
        btn_choose.clicked.connect(self.select_file)

        file_row.addWidget(self.file_display)
        file_row.addWidget(btn_choose)
        layout.addLayout(file_row)

        # ---------- Save button ----------
        btn_save = QPushButton("Save Shortcut")
        btn_save.setFixedHeight(36)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        btn_save.clicked.connect(self.save)
        layout.addWidget(btn_save)

        self.selected_file = None


    ############################################
    # Capture Shortcut Logic
    ############################################
    def eventFilter(self, obj, event):
        if obj == self.keybox and event.type() == event.KeyPress:
            key = event.key()
            mod = QApplication.keyboardModifiers()

            parts = []
            if mod & Qt.ControlModifier:
                parts.append("ctrl")
            if mod & Qt.AltModifier:
                parts.append("alt")
            if mod & Qt.ShiftModifier:
                parts.append("shift")

            key_text = event.text().lower()
            if key_text:
                parts.append(key_text)

            final = "+".join(parts)
            self.keybox.setText(final)
            return True

        return False


    ############################################
    # File Picker
    ############################################
    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select .macro file",
                                              DOWNLOAD_DIR,
                                              "Macro Files (*.macro)")
        if file:
            self.selected_file = os.path.basename(file)
            self.file_display.setText(self.selected_file)


    ############################################
    # Save Validation
    ############################################
    def save(self):
        shortcut = self.keybox.text().strip()
        file = self.selected_file

        if not shortcut or shortcut.endswith("+"):
            QMessageBox.warning(self, "Error", "Please press a complete shortcut (e.g. ctrl+alt+1).")
            return

        if not file:
            QMessageBox.warning(self, "Error", "Please select a macro file.")
            return

        for entry in global_shortcuts:
            if entry["shortcut"] == shortcut:
                QMessageBox.warning(self, "Error", "This shortcut already exists.")
                return

        global_shortcuts.append({
            "shortcut": shortcut,
            "file": file
        })

        save_shortcut_config()
        register_all_hotkeys()
        self.close()


############################################
# MAIN UI
############################################

class TinyTaskApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TinyTask Dynamic")
        self.setFixedSize(450, 220)
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)


        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        save_action = QAction("Save Recording", self)
        save_action.triggered.connect(lambda: save_macro(self))
        file_menu.addAction(save_action)

        load_action = QAction("Load Recording", self)
        load_action.triggered.connect(lambda: self.load_macro_dialog())
        file_menu.addAction(load_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        file_menu.addAction(exit_action)


        # Shortcut Manager
        shortcut_menu = menubar.addMenu("Shortcuts")
        shortcut_menu.addAction("Manage Shortcuts", self.open_shortcut_manager)

        # Toolbar Buttons
        widget = QWidget()
        layout = QVBoxLayout()

        row = QHBoxLayout()

        btn_play = QPushButton("▶ Play")
        btn_play.clicked.connect(start_playback)
        row.addWidget(btn_play)

        btn_start = QPushButton("● Start Recording")
        btn_start.clicked.connect(start_recording)
        row.addWidget(btn_start)

        btn_stop = QPushButton("■ Stop Recording")
        btn_stop.clicked.connect(stop_recording)
        row.addWidget(btn_stop)

        btn_stop_play = QPushButton("⏹ Stop Playback")
        btn_stop_play.clicked.connect(stop_playback)
        row.addWidget(btn_stop_play)

        layout.addLayout(row)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def load_macro_dialog(self):
        file, _ = QFileDialog.getOpenFileName(self, "Load Recording", DOWNLOAD_DIR, "Macro Files (*.macro)")
        if file:
            load_macro(file)

    def open_shortcut_manager(self):
        dlg = ShortcutManager()
        dlg.show()
        dlg.activateWindow()
        dlg.raise_()
        dlg.exec_()


    def exit_app(self):
        # Stop playback/recording
        global recording, playing
        recording = False
        playing = False

        # Remove all global hotkeys
        try:
            keyboard.unhook_all()
        except:
            pass

        # Kill Qt app
        QApplication.quit()

        # Force kill Python process
        os._exit(0)


############################################
# APP STARTUP
############################################

load_shortcut_config()
register_all_hotkeys()

############################################
# FIXED HOTKEYS FOR RECORDING
############################################

def register_recording_hotkeys():
    # Ctrl + 1 → Start Recording
    keyboard.add_hotkey("ctrl+1", lambda: (
        print("🎙️ CTRL+1 → Start Recording"),
        start_recording()
    ))

    # Ctrl + 2 → Stop Recording
    keyboard.add_hotkey("ctrl+2", lambda: (
        print("⛔ CTRL+2 → Stop Recording"),
        stop_recording()
    ))

register_recording_hotkeys()

app = QApplication(sys.argv)
window = TinyTaskApp()
window.show()
sys.exit(app.exec_())
