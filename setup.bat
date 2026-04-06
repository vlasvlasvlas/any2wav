@echo off
setlocal EnableExtensions

set "BASE_DIR=%~dp0"
set "VENV_PYTHON=%BASE_DIR%venv\Scripts\python.exe"
set "REQ_FILE=%BASE_DIR%requirements.txt"

cd /d "%BASE_DIR%"

echo.
echo ============================================
echo   any2wav - Configuracion (Windows)
echo ============================================
echo.

echo [1/4] Verificando Python...
set "PYTHON_EXE="
set "PYTHON_ARGS="

where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_EXE=py"
    set "PYTHON_ARGS=-3"
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON_EXE=python"
    )
)

if "%PYTHON_EXE%"=="" (
    call :fail "Python 3 no esta instalado o no esta en PATH. Descargalo desde https://python.org"
)

"%PYTHON_EXE%" %PYTHON_ARGS% --version
if errorlevel 1 (
    call :fail "No se pudo ejecutar Python."
)

echo.
echo [2/4] Verificando FFmpeg...
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo ERROR: FFmpeg no esta instalado o no esta en PATH.
    echo.
    echo Instala FFmpeg y agrega la carpeta bin al PATH:
    echo https://ffmpeg.org/download.html
    echo.
    echo Opcion rapida (winget):
    echo winget install --id Gyan.FFmpeg -e
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%A in ('ffmpeg -version ^| findstr /B /C:"ffmpeg version"') do (
    echo %%A
    goto :ffmpeg_ok
)
:ffmpeg_ok

echo.
echo [3/4] Creando entorno virtual...
if exist "%VENV_PYTHON%" (
    echo AVISO: Ya existe ./venv, se reutiliza.
) else (
    "%PYTHON_EXE%" %PYTHON_ARGS% -m venv "%BASE_DIR%venv"
    if errorlevel 1 (
        call :fail "No se pudo crear el entorno virtual."
    )
    echo OK: Entorno virtual creado en .\venv
)

echo.
echo [4/4] Instalando dependencias...
"%VENV_PYTHON%" -m pip install --upgrade pip
if errorlevel 1 call :fail "Fallo la actualizacion de pip."
"%VENV_PYTHON%" -m pip install -r "%REQ_FILE%"
if errorlevel 1 call :fail "Fallo la instalacion de requirements."
"%VENV_PYTHON%" -m pip install -e "%BASE_DIR%"
if errorlevel 1 call :fail "Fallo la instalacion editable del proyecto."
echo OK: Dependencias instaladas.

echo.
echo ============================================
echo   Configuracion completada
echo ============================================
echo.
echo Uso rapido en Windows:
echo   1) Menu interactivo: run.bat
echo   2) CLI:
echo      venv\Scripts\activate
echo      any2wav .\in -f wav
echo.

exit /b 0

:fail
echo ERROR: %~1
echo.
pause
exit /b 1
