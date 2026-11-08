## Construir y levantar los dos servicios

Desde la carpeta que contiene `docker-compose.yml`:

```bash
docker compose build
docker compose up -d
docker compose ps
```

Ver el estado y los logs:

```bash
docker compose logs -f api
```

La API también está disponible desde el equipo anfitrión en `http://localhost:8000`; su documentación está en `http://localhost:8000/docs`.

## Demostración de comunicación ida y vuelta

Ejecuta el comando **desde el contenedor cliente**. El primer comando envía un `POST` al servicio `api` y guarda el dato en SQLite. Copia el `id` que devuelve:

```bash
docker compose exec cliente python client.py create "Audifonos" "Dato creado desde el contenedor cliente"
```

Luego consulta ese mismo ID, también desde el contenedor cliente:

```bash
docker compose exec cliente python client.py get 4
```

Reemplaza `4` por el `id` devuelto por el comando `create`. Para mostrar todos los datos:

```bash
docker compose exec cliente python client.py list
```

La variable `API_URL=http://api:8000` está configurada para `cliente`; la respuesta del `POST` y del `GET` vuelve a la consola del cliente.

## Evidencias de red Docker

La red tiene nombre fijo para facilitar la inspección. Como ambos servicios quedan levantados, el resultado muestra los dos contenedores conectados:

```bash
docker network inspect red_consulta
```

También puedes verificar el nombre usado por el cliente y el estado de salud de la API:

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

La prueba desde el host es opcional; para evidenciar la comunicación entre contenedores, usa `docker compose exec cliente`.

## Detener

```bash
docker compose down
```

Los datos siguen guardados en `api_data`. Para borrar también la base y empezar de cero:

```bash
docker compose down -v
```
