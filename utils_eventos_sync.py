import os
import json

def evento_file(evento_id):
    return os.path.join("datos_usuarios", f"evento_{evento_id}.json")

def cargar_evento(evento_id):
    archivo = evento_file(evento_id)
    if not os.path.exists(archivo):
        os.makedirs(os.path.dirname(archivo), exist_ok=True)
        with open(archivo, "w") as f:
            json.dump({"id": evento_id, "grupo_id": "", "nombre": "", "admin": "", "participantes": [], "montos": {}, "pagos": {}}, f)
    with open(archivo, "r") as f:
        return json.load(f)

def guardar_evento(evento_id, evento):
    archivo = evento_file(evento_id)
    if not os.path.exists(archivo):
        os.makedirs(os.path.dirname(archivo), exist_ok=True)
        with open(archivo, "w") as f:
            json.dump({"id": evento_id, "grupo_id": "", "nombre": "", "admin": "", "participantes": [], "montos": {}, "pagos": {}}, f)
    with open(archivo, "w") as f:
        json.dump(evento, f)

def listar_eventos():
    carpeta = "datos_usuarios"
    if not os.path.exists(carpeta):
        return []
    return [f for f in os.listdir(carpeta) if f.startswith("evento_") and f.endswith(".json")]

def buscar_eventos_por_grupo(grupo_id):
    eventos = []
    for archivo in listar_eventos():
        with open(os.path.join("datos_usuarios", archivo), "r") as f:
            evento = json.load(f)
            if evento.get("grupo_id") == grupo_id:
                eventos.append(evento)
    return eventos
