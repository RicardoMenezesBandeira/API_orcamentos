@echo off
setlocal enabledelayedexpansion
set DOCKER_PATH="C:\Program Files\Docker\Docker\Docker Desktop.exe"

echo Verificando se o Docker está rodando...
docker info >nul 2>&1
IF ERRORLEVEL 1 (
    echo Docker não está rodando. Iniciando o Docker Desktop...
    start "" %DOCKER_PATH%
    echo Aguardando Docker iniciar...
    :wait_docker
    timeout /t 2 >nul
    docker info >nul 2>&1
    IF ERRORLEVEL 1 (
        goto wait_docker
    )
)

echo Docker está pronto.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%a
)
echo Acesse sua aplicação em: http://!ip:~1!
echo Abrindo a porta 80 no firewall do Windows...

:: Adiciona uma regra de entrada para permitir tráfego TCP na porta 80
netsh advfirewall firewall add rule name="Abrir Porta 80 TCP" ^
dir=in action=allow protocol=TCP localport=80

:: Verifica se a regra foi adicionada com sucesso
if %errorlevel%==0 (
    echo Porta 80 aberta com sucesso para conexões TCP.
) else (
    echo Falha ao abrir a porta 80. Execute este script como administrador.
)

echo Iniciando docker-compose...
docker-compose up --build

echo ----------------------------------
echo Containers finalizados ou encerrados.
pause
