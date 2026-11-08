import argparse
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = os.getenv("API_URL", "http://api:8000").rstrip("/")


def request(path: str, method: str = "GET", payload: dict | None = None):
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        f"{BASE_URL}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        try:
            message = json.load(error).get("detail", str(error))
        except Exception:
            message = str(error)
        print(f"Error de API ({error.code}): {message}", file=sys.stderr)
        raise SystemExit(1)
    except urllib.error.URLError as error:
        print(f"No se pudo conectar con {BASE_URL}: {error.reason}", file=sys.stderr)
        print("Comprueba que api esté levantado: docker compose up -d --build", file=sys.stderr)
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente de consola para la API de consulta")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("health", help="Comprueba la conexión con la API")
    commands.add_parser("list", help="Consulta todos los elementos")
    show = commands.add_parser("get", help="Consulta un elemento por su ID")
    show.add_argument("id", type=int)
    create = commands.add_parser("create", help="Guarda un elemento mediante la API")
    create.add_argument("nombre")
    create.add_argument("descripcion", nargs="?", default="")
    args = parser.parse_args()

    if args.command == "health":
        data = request("/health")
    elif args.command == "list":
        data = request("/items")
    elif args.command == "get":
        data = request(f"/items/{args.id}")
    else:
        data = request(
            "/items",
            method="POST",
            payload={"nombre": args.nombre, "descripcion": args.descripcion},
        )
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
