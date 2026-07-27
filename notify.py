@echo off
cd /d "%~dp0"
title PARES - Importar tiendas desde marcadores
where python >nul 2>nul && (set PY=python) || (set PY=py)
if "%~1"=="" (
  echo.
  echo COMO USARLO:
  echo   1. Chrome: chrome://bookmarks - menu de 3 puntos - Exportar marcadores
  echo   2. Arrastra el archivo .html EXPORTADO encima de este .bat
  echo.
  pause
  exit /b
)
if not exist importar_tiendas.py (
  echo [ERROR] No encuentro importar_tiendas.py en esta carpeta:
  echo   %CD%
  echo Este .bat debe estar DENTRO de la carpeta buscador-pares descomprimida.
  pause
  exit /b
)
echo Procesando: %~1
echo.
%PY% importar_tiendas.py "%~1"
echo.
pause
