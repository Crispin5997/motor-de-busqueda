@echo off
cd /d "%~dp0"
title PARES - Instalacion
where python >nul 2>nul && (set PY=python) || (set PY=py)
%PY% --version >nul 2>nul
if errorlevel 1 (
  echo.
  echo [ERROR] No se encontro Python en Windows.
  echo Instalalo desde https://www.python.org/downloads/
  echo IMPORTANTE: marca "Add python.exe to PATH" al instalar.
  pause
  exit /b
)
echo Carpeta: %CD%
if not exist requirements.txt (
  echo [ERROR] No encuentro requirements.txt en esta carpeta.
  echo Este .bat debe estar DENTRO de la carpeta buscador-pares descomprimida.
  pause
  exit /b
)
echo Instalando dependencias base...
%PY% -m pip install --quiet fastapi uvicorn httpx rapidfuzz pyyaml python-multipart
if errorlevel 1 goto :err
echo Instalando curl_cffi (huella TLS de Chrome real para pasar anti-bot)...
%PY% -m pip install --quiet curl_cffi
if errorlevel 1 (
  echo   [aviso] curl_cffi no se pudo instalar en tu Python.
  echo   Las tiendas Shopify y la app funcionan igual; solo las tiendas
  echo   con Akamai/DataDome quedaran menos efectivas.
)
echo.
echo Listo. Ahora usa iniciar_buscador.bat
pause
exit /b
:err
echo.
echo [ERROR] Fallo la instalacion de dependencias base.
pause
