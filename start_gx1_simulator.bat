@echo off
set script_path=%~dp0
set relative_path=%script_path%../python3/
set PYTHONHOME=%relative_path%
set PATH=%relative_path%;%PATH%
cd %~dp0
python -m main
pause