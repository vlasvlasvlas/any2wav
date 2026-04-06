@echo off
setlocal EnableExtensions

set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

if not exist "%BASE_DIR%run.bat" (
    echo ERROR: No se encontro run.bat en la carpeta del proyecto.
    echo.
    pause
    exit /b 1
)

if not exist "%BASE_DIR%venv\Scripts\python.exe" (
    echo Entorno virtual no encontrado. Ejecutando setup.bat...
    call "%BASE_DIR%setup.bat"
    if errorlevel 1 (
        echo ERROR: Fallo la configuracion.
        echo.
        pause
        exit /b 1
    )
)

call "%BASE_DIR%run.bat"
set "EXIT_CODE=%errorlevel%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo ERROR: La aplicacion finalizo con codigo %EXIT_CODE%.
    echo.
    pause
)
exit /b %EXIT_CODE%
