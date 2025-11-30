So many days one words i am thinking to make my own mouse clicker application, because i saw some features are not presented in those things so i taught why cannot i build it on my own.

today as i started reading, and chatting with chatgpt, i found some things.

(Already-made apps)
TinyTask (FREE, 35 KB) 👉 https://www.tinytask.net/
Features:
RECORD everything
PLAYBACK exactly
Very light (35 KB)
Portable EXE
Loop playback
Adjustable speed
This is the best simple choice if you just need record → repeat.

but it also doesnt have the feature, certain shortcut, to trigger some certain task.

So i stated building it 

See the file called Initialbuild.txt where what happened and what casuse

short summary was about the file.

when stated installed it installed in some specific location, i not kept in environment so i got error their is some specif command to use that location to star, building the process.



# I started making the application
Avaliable languages are the python, C++, go.
i already good with the python so i stated using it.


STEP 1 — Install required Python libraries
pip install pynput PyQt5 keyboard

pynput → captures mouse & keyboard
pynput → captures mouse & keyboard

tinytask_clone.py
FULL WORKING CODE (TinyTask-Python)

STEP 4 — BUILD EXE
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed tinytask_clone.py

Rebuild:
C:\Users\stain\AppData\Roaming\Python\Python313\Scripts\pyinstaller.exe --onefile --windowed tinytask_clone.py


Your EXE will be in:
cd dist
tinytask_clone.exe


then i decided to stop building, once the application full ready then i am going to build the application.



version 1:  tinytask_base.py

FINAL BASE VERSION CODE (TINY-TASK STYLE)

Now I’ll generate your FINAL BASE VERSION of the TinyTask-style application:

✔ Normal window
✔ Menu bar (File / Options / Settings)
✔ Icon + text buttons (Play, Start Recording, Stop Recording, Stop Playback)
✔ Safe recording/playback
✔ ESC = emergency stop
✔ No hotkeys
✔ save/load
✔ No compile
✔ Stable + extendable


File
 ├── Save Recording
 ├── Load Recording
 └── Exit


UI:
🟩 File / Options / Settings menus
🟩 Buttons with icon-like symbols + text
🟩 Normal window (not always on top)
🟩 Clean and simple layout

Functionality:
🟩 Start Recording
🟩 Stop Recording
🟩 Play
🟩 Stop Playback
🟩 ESC key instantly stops playback
🟩 Threads safe
🟩 No infinite loops
🟩 No CPU lock
🟩 Events stored safely

python tinytask_base.py


Version 2: tinytask_dynamic.py

pip install PyQt5 pynput keyboard


version 2.1: Working model
having shortcuts to trigger the event.
saving/loading the actions.

problems
manager window if i close automatically it closing entire application. 
need to enhance ui