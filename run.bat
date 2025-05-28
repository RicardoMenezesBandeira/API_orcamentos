@echo off
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
echo Iniciando docker-compose...
docker-compose up --build
