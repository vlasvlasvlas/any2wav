@echo off
setlocal EnableExtensions

cd /d "%~dp0"

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
    echo ERROR: Python 3 no esta instalado o no esta en PATH.
    echo Descargalo desde https://python.org
    exit /b 1
)

"%PYTHON_EXE%" %PYTHON_ARGS% --version
if errorlevel 1 (
    echo ERROR: No se pudo ejecutar Python.
    exit /b 1
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
    exit /b 1
)

for /f "delims=" %%A in ('ffmpeg -version ^| findstr /B /C:"ffmpeg version"') do (
    echo %%A
    goto :ffmpeg_ok
)
:ffmpeg_ok

echo.
echo [3/4] Creando entorno virtual...
if exist "venv\Scripts\python.exe" (
    echo AVISO: Ya existe ./venv, se reutiliza.
) else (
    "%PYTHON_EXE%" %PYTHON_ARGS% -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        exit /b 1
    )
    echo OK: Entorno virtual creado en .\venv
)

echo.
echo [4/4] Instalando dependencias...
call "venv\Scripts\activate.bat"
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1
pip install -r requirements.txt
if errorlevel 1 exit /b 1
pip install -e .
if errorlevel 1 exit /b 1
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
