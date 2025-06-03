# smartpay-db

_API REST en Python con FastAPI, PostgreSQL y Tortoise ORM para manejar la base de datos del servicio SmartPay_

## Comenzando 🚀

_Estas instrucciones te permitirán obtener una copia del proyecto en funcionamiento en tu máquina local para propósitos de desarrollo y pruebas._

### Pre-requisitos 📋

_Se necesita Docker_

_Docker_:

En Ubuntu:
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
```

Para más detalles sobre la instalación de Docker:
- Ubuntu: https://www.hostinger.co/tutoriales/como-instalar-y-usar-docker-en-ubuntu/
- Windows y Mac: https://platzi.com/tutoriales/2066-docker/1779-como-instalar-docker-en-windows-y-mac/

### Instalación 🔧

_Una vez instalado Docker, sigue estos pasos:_

1. Clona el repositorio:
```bash
git clone <url-del-repositorio>
cd smartpay-db
```

2. Crea el volumen de Docker necesario:
```bash
docker volume create smartpay-db
```

3. Crea la red de Docker necesaria:
```bash
docker network create smartpay
```

4. Inicia los servicios con Docker Compose:

En Ubuntu:
```bash
sudo docker-compose -f docker/Docker-compose.dev.yml up --build
```

En Windows (Con permisos de administrador):
```bash
docker-compose -f docker/Docker-compose.dev.yml up --build
```

La API quedará ejecutándose en el puerto 8002 por defecto y lista para recibir peticiones.

### Acceso a la API 🌐

- API: http://localhost:8002
- Documentación interactiva (Swagger): http://localhost:8002/docs
- Documentación alternativa (ReDoc): http://localhost:8002/redoc


## Construido con 🛠️

* [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno y rápido para construir APIs con Python
* [Tortoise ORM](https://tortoise.github.io/) - ORM asíncrono para Python
* [PostgreSQL](https://www.postgresql.org/) - Base de datos relacional
* [Docker](https://www.docker.com) - Contenedorización y despliegue
* [Pre-commit](https://pre-commit.com/) - Gestión de hooks de git para control de calidad

## Estructura del Proyecto 📁

```
smartpay-db/
├── app/
│   ├── api/           # Endpoints de la API
│   ├── core/          # Configuración central
│   ├── infra/        # Infraestructura (DB, etc.)
│   ├── schemas/      # Modelos Pydantic
│   └── services/     # Lógica de negocio
├── docker/           # Configuración de Docker
├── tests/           # Tests
└── README.md
```

## Desarrollo 💻

Para desarrollo local, se recomienda:

1. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias de desarrollo:
```bash
pip install -r requirements.txt
```

3. Instalar pre-commit hooks:
```bash
pre-commit install
```

## Licencia 📄

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para detalles
