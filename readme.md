# Realtime pressure feedback system

---

## Platform

Run in windows PC, and the project is programmed in Qt.

## Build

Build into .exe

```powershell
# Produce build directory and dist directory
# The app.exe is located inside the dist directory
# After building, **manually copy** the following directories into the dist directory to make the app.exe working
# conf, correction, font, img, log, Protocols, resource, translate
pyinstaller.exe --onefile app.py
```
