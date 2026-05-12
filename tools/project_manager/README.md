# Project Manager

PySide6 desktop editor for `_data/projects.json`.

You can also drag and drop a project folder into the app to scan files, detect screenshots and metadata, infer tags, and create a project entry automatically.

## Run

```powershell
py -m pip install -r tools\project_manager\requirements.txt
py tools\project_manager\main.py
```

The app defaults to the repository `_data/projects.json` file. Preferences can change both the project data path and the settings JSON location.
