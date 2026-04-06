@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: No se encontro el entorno virtual.
    echo Ejecuta primero: setup.bat
    exit /b 1
)

call "venv\Scripts\activate.bat" >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    exit /b 1
)

set "INPUT_DIR=.\in"
set "OUTPUT_DIR=.\out"
set "FORMAT=wav"
set "RECURSIVE=0"

:menu
cls
echo ===========================================================
echo  any2wav - Menu interactivo (Windows)
echo ===========================================================
echo.
echo Configuracion actual:
echo   Entrada: !INPUT_DIR!
echo   Salida : !OUTPUT_DIR!
if /I "!FORMAT!"=="wav" (
    echo   Formato: WAV
) else (
    echo   Formato: MP3
)
if "!RECURSIVE!"=="1" (
    echo   Subcarpetas: SI
) else (
    echo   Subcarpetas: NO
)
echo.
echo  1. Cambiar carpeta de entrada
echo  2. Cambiar carpeta de salida
echo  3. Cambiar formato (WAV/MP3)
echo  4. Incluir/excluir subcarpetas
echo  5. Convertir
echo  6. Preview (dry-run)
echo  0. Salir
echo.
set /p "CHOICE=Selecciona una opcion: "

if "%CHOICE%"=="1" goto select_input
if "%CHOICE%"=="2" goto select_output
if "%CHOICE%"=="3" goto toggle_format
if "%CHOICE%"=="4" goto toggle_recursive
if "%CHOICE%"=="5" goto run_conversion
if "%CHOICE%"=="6" goto run_preview
if "%CHOICE%"=="0" goto exit_app

echo.
echo Opcion invalida.
pause
goto menu

:select_input
echo.
set /p "NEW_INPUT=Ruta de carpeta de entrada: "
set "NEW_INPUT=%NEW_INPUT:"=%"
if "!NEW_INPUT!"=="" goto menu

if exist "!NEW_INPUT!\NUL" (
    set "INPUT_DIR=!NEW_INPUT!"
    echo Carpeta de entrada actualizada: !INPUT_DIR!
) else (
    echo ERROR: La carpeta no existe.
)
pause
goto menu

:select_output
echo.
set /p "NEW_OUTPUT=Ruta de carpeta de salida: "
set "NEW_OUTPUT=%NEW_OUTPUT:"=%"
if "!NEW_OUTPUT!"=="" goto menu

set "OUTPUT_DIR=!NEW_OUTPUT!"
echo Carpeta de salida actualizada: !OUTPUT_DIR!
pause
goto menu

:toggle_format
if /I "!FORMAT!"=="wav" (
    set "FORMAT=mp3"
) else (
    set "FORMAT=wav"
)
echo.
echo Formato actualizado: !FORMAT!
timeout /t 1 >nul
goto menu

:toggle_recursive
if "!RECURSIVE!"=="1" (
    set "RECURSIVE=0"
) else (
    set "RECURSIVE=1"
)
echo.
if "!RECURSIVE!"=="1" (
    echo Subcarpetas activadas.
) else (
    echo Subcarpetas desactivadas.
)
timeout /t 1 >nul
goto menu

:run_conversion
if not exist "!INPUT_DIR!\NUL" (
    echo.
    echo ERROR: La carpeta de entrada no existe.
    pause
    goto menu
)

echo.
echo Iniciando conversion...
echo.
if "!RECURSIVE!"=="1" (
    any2wav "!INPUT_DIR!" -o "!OUTPUT_DIR!" -f !FORMAT! -r
) else (
    any2wav "!INPUT_DIR!" -o "!OUTPUT_DIR!" -f !FORMAT!
)
echo.
pause
goto menu

:run_preview
if not exist "!INPUT_DIR!\NUL" (
    echo.
    echo ERROR: La carpeta de entrada no existe.
    pause
    goto menu
)

echo.
echo Preview (dry-run)...
echo.
if "!RECURSIVE!"=="1" (
    any2wav "!INPUT_DIR!" -o "!OUTPUT_DIR!" -f !FORMAT! -r --dry-run
) else (
    any2wav "!INPUT_DIR!" -o "!OUTPUT_DIR!" -f !FORMAT! --dry-run
)
echo.
pause
goto menu

:exit_app
echo.
echo Hasta luego.
exit /b 0
