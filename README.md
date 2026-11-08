# consulta-docker

Proyecto de la materia Integración Continua. Son dos contenedores que se comunican por una red de Docker: una API hecha con FastAPI que guarda los datos en SQLite y un cliente de consola que la consulta usando el nombre del servicio (`http://api:8000`), sin pasar por `localhost`.

## Estructura

```
consulta-docker/
├── api/                  # API FastAPI + SQLite (puerto 8000)
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── client/               # Cliente de consola
│   ├── client.py
│   ├── Dockerfile
│   └── .dockerignore
├── .github/workflows/
│   └── ci.yml            # GitHub Actions
├── docker-compose.yml
├── .env.example
└── .gitignore
```

En `docker-compose.yml` están los servicios `api` y `cliente`, la red `red_consulta` y el volumen `api_data`, donde queda la base de datos. El cliente arranca solo cuando el healthcheck de la API responde.

## Configuración

Las variables se leen desde un archivo `.env`. Ese archivo no se sube al repositorio, así que hay que crearlo a partir de la plantilla:

```bash
cp .env.example .env
```

En PowerShell:

```powershell
Copy-Item .env.example .env
```

| Variable | Valor por defecto | Para qué sirve |
|---|---|---|
| `DATABASE_PATH` | `/data/consulta.db` | Ruta de la base SQLite dentro del contenedor de la API |
| `API_URL` | `http://api:8000` | Dirección que usa el cliente para llegar a la API |

## Construir y levantar los dos servicios

Desde la carpeta que contiene `docker-compose.yml`:

```bash
docker compose build
docker compose up -d
docker compose ps
```

Para ver los logs de la API:

```bash
docker compose logs -f api
```

La API también responde desde el equipo anfitrión en `http://localhost:8000`, y su documentación está en `http://localhost:8000/docs`.

## Demostración de comunicación ida y vuelta

Los comandos se ejecutan desde el contenedor cliente. El primero envía un `POST` al servicio `api`, que guarda el dato en SQLite y devuelve un `id`:

```bash
docker compose exec cliente python client.py create "Audifonos" "Dato creado desde el contenedor cliente"
```

Con ese `id` se consulta el mismo dato:

```bash
docker compose exec cliente python client.py get 4
```

Cambia `4` por el `id` que devolvió `create`. Para ver todos los datos:

```bash
docker compose exec cliente python client.py list
```

## Evidencias de red Docker

La red tiene un nombre fijo, así que se puede inspeccionar directamente. Con los dos servicios arriba, aparecen ambos contenedores conectados:

```bash
docker network inspect red_consulta
```

Para comprobar qué dirección usa el cliente y el estado de salud de la API:

```bash
docker compose exec cliente python -c "import os; print(os.environ['API_URL'])"
docker compose ps
```

## Probar la API desde el host (opcional)

```bash
curl http://localhost:8000/health
curl http://localhost:8000/items
```

Crear un dato desde PowerShell:

```powershell
curl.exe -X POST "http://localhost:8000/items" -H "Content-Type: application/json" --data-binary '{"nombre":"Aud\\u00edfonos","descripcion":"Dato de prueba"}'
```

Esto sirve para probar la API, pero la comunicación entre contenedores se demuestra con `docker compose exec cliente`.

## Integración continua

El workflow `.github/workflows/ci.yml` corre en cada push y en cada pull request. Crea el `.env` desde `.env.example`, construye y levanta los contenedores, espera el healthcheck, crea un dato desde el cliente, lo consulta por su `id` y al final apaga todo con `docker compose down -v`.

## Flujo de ramas

`main` tiene la versión entregada y `develop` es la rama de integración. Cada parte del proyecto se trabajó en su propia rama (`feature/api`, `feature/cliente`, `feature/docker-compose`, `feature/ci`) y entró a `develop` por pull request. Ninguna de las dos ramas principales acepta commits directos.

## Detener

```bash
docker compose down
```

Los datos se conservan en el volumen `api_data`. Para borrarlo y empezar de cero:

```bash
docker compose down -v
```
