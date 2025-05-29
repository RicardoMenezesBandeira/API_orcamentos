@echo off
setlocal enabledelayedexpansion

:: Obtém o IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%a
)
set ip_local=!ip:~1!

echo -----------------------------------------
echo Verificando status da porta 80 em !ip_local!...
echo (Aguarde...)
echo.

:: Usa PowerShell para testar a porta
powershell -Command "Test-NetConnection !ip_local! -Port 80"

echo -----------------------------------------
pause
