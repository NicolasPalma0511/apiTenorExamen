#!/bin/bash

# Variables
PROJECT_DIR="apiTenorExamen"
PYTHON_DIR="$PROJECT_DIR/flask"
DOTNET_DIR="$PROJECT_DIR/dotnet"
API_PORT=5000
GITHUB_REPO_URL="https://github.com/NicolasPalma0511/apiTenorExamen"

# Función para comprobar errores
check_error() {
    if [ $? -ne 0 ]; then
        echo "Error durante la ejecución: $1"
        exit 1
    fi
}

# Descargar archivos de GitHub
git clone $GITHUB_REPO_URL $PROJECT_DIR
check_error "Error clonando repositorio de GitHub."

# Iniciar el contenedor de la API en .NET
api_container_id=$(docker run -d -it -p $API_PORT:$API_PORT mcr.microsoft.com/dotnet/sdk:8.0 /bin/bash)
check_error "Error iniciando contenedor de .NET."

# Espera un momento para asegurarse de que el contenedor esté completamente iniciado
sleep 10

# Crear la API en el contenedor de .NET
docker container exec --workdir / $api_container_id dotnet new webapi -o MyMicroservice --no-https
check_error "Error creando la API en el contenedor de .NET."


# Copiar archivos necesarios al contenedor
docker container cp $PYTHON_DIR/requirements.txt $api_container_id:/home/app/requirements.txt
docker container cp $PYTHON_DIR/process.py $api_container_id:/home/app/process.py
docker container cp $DOTNET_DIR/Program.cs $api_container_id:/MyMicroservice/Program.cs
check_error "Error copiando archivos al contenedor."

# Instalar Python en el contenedor de .NET
docker container exec --workdir / $api_container_id bash -c 'apt-get update && apt-get install -y python3 python3-pip && apt-get install -y python3.11-venv'
check_error "Error instalando Python en el contenedor de .NET."

# Crear un entorno virtual y activar
docker container exec --workdir /home/app $api_container_id python3 -m venv venv
check_error "Error creando el entorno virtual."

# Instalar dependencias de Python en el entorno virtual
docker container exec --workdir /home/app $api_container_id bash -c 'source venv/bin/activate && pip install -r requirements.txt'
check_error "Error instalando dependencias de Python en el entorno virtual."

# Restaurar las dependencias y ejecutar la API dentro del contenedor
docker container exec --workdir /MyMicroservice $api_container_id dotnet restore
check_error "Error restaurando dependencias en el contenedor de .NET."
docker container exec --workdir /MyMicroservice $api_container_id dotnet run --urls http://0.0.0.0:$API_PORT &
check_error "Error ejecutando la API en el contenedor de .NET."

