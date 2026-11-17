@echo off
setlocal
cd /d "%~dp0.."
set "PYTHON=%CD%\venv\Scripts\python.exe"
if not exist "%PYTHON%" (
  echo Existing project Python environment was not found: %PYTHON%
  echo This launcher expects the existing venv folder. It will not create or modify an environment.
  pause
  exit /b 1
)
"%PYTHON%" -c "import pymysql; print('PyMySQL:', pymysql.__version__)" || (echo PyMySQL import failed in the existing environment. No other packages will be reinstalled.& pause & exit /b 1)
"%PYTHON%" "%~dp0app.py"
pause
