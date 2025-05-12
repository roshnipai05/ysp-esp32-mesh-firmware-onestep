@echo off
setlocal enabledelayedexpansion

REM ===================== CONFIGURATION =====================
SET REPO_URL=https://github.com/Makerspace-Ashoka/ysp-esp32-mesh-firmware.git
SET REPO_NAME=ysp-esp32-mesh-firmware
SET PYTHON_INSTALLER=https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
SET VSCODE_INSTALLER=https://update.code.visualstudio.com/latest/win32-x64-user/stable
SET GIT_INSTALLER=https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe
SET REQUIREMENTS_URL=https://raw.githubusercontent.com/ysp-esp32-mesh-firmware/python-interface/src/requirements.txt

REM ===================== CHECK FOR GIT =====================
where git >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] Git not found. Downloading Git...
    powershell -Command "Invoke-WebRequest -Uri %GIT_INSTALLER% -OutFile git-installer.exe"
    start /wait git-installer.exe /VERYSILENT
    del git-installer.exe
) ELSE (
    echo [INFO] Git is already installed.
)

REM ========== CHECK FOR PYTHON >= 3.10 AND FUNCTIONAL ===========
SET PYTHON=
SET PYTHON_VERSION_OK=0

> check_version.py echo import sys
>> check_version.py echo major, minor = sys.version_info[:2]
>> check_version.py echo exit(0) if (major > 3 or (major == 3 and minor >= 10)) else exit(1)

FOR %%P IN (python python3 py) DO (
    %%P check_version.py >nul 2>nul
    IF !ERRORLEVEL! == 0 (
        SET PYTHON=%%P
        SET PYTHON_VERSION_OK=1
        GOTO FoundPython
    )
)

DEL check_version.py

:FoundPython
IF NOT !PYTHON_VERSION_OK! EQU 1 (
    echo [INFO] Python >= 3.10 not found or not functional. Installing Python...
    powershell -Command "Invoke-WebRequest -Uri %PYTHON_INSTALLER% -OutFile python-installer.exe"
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python-installer.exe
    SET PYTHON=python
)

echo [INFO] Using Python command: %PYTHON%

REM ===================== CHECK FOR VSCODE =====================
where code >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [INFO] VSCode not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri %VSCODE_INSTALLER% -OutFile vscode-installer.exe"
    start /wait vscode-installer.exe /silent
    del vscode-installer.exe
) ELSE (
    echo [INFO] VSCode is already installed.
)

REM ===================== DOWNLOAD REPO =====================
echo [INFO] Downloading GitHub repo as ZIP...
powershell -Command "Invoke-WebRequest -Uri %REPO_URL%/archive/refs/heads/main.zip -OutFile repo.zip"
powershell -Command "Expand-Archive -Path repo.zip -DestinationPath . -Force"
ren %REPO_NAME%-main %REPO_NAME%
del repo.zip

REM ========== SET UP VIRTUAL ENVIRONMENT ==========
cd %REPO_NAME%
echo [INFO] Creating virtual environment...
%PYTHON% -m venv .venv

REM ========== ACTIVATE AND INSTALL DEPENDENCIES ==========
call .venv\Scripts\activate
powershell -Command "Invoke-WebRequest -Uri %REQUIREMENTS_URL% -OutFile requirements.txt"
echo [INFO] Installing dependencies from requirements.txt...
pip install -r requirements.txt

REM ===================== OPEN VSCODE =====================
cd python-interface\src
echo [INFO] Opening VSCode in project folder...
code .

endlocal
