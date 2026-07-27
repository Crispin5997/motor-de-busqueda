@echo off
cd /d "%~dp0"
title PARES - Buscador privado (NO CIERRES ESTA VENTANA)
where python >nul 2>nul && (set PY=python) || (set PY=py)
if not exist app.py (
  echo [ERROR] No encuentro app.py en esta carpeta:
  echo   %CD%
  echo Este .bat debe estar DENTRO de la carpeta buscador-pares descomprimida.
  pause
  exit /b
)
echo Iniciando buscador en http://localhost:8712 ...
echo Esta ventana negra ES el servidor: dejala abierta mientras uses la app.
start "" /min cmd /c "timeout /t 2 >nul && start http://localhost:8712"
%PY% -m uvicorn app:app --port 8712
echo.
echo El servidor se detuvo. Si fue un error, lee arriba o corre diagnostico.bat
pause
