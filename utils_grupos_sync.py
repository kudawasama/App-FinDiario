import os
import json

def grupo_file(grupo_id):
    return os.path.join("datos_usuarios", f"grupo_{grupo_id}.json")

def cargar_grupo(grupo_id):
    archivo = grupo_file(grupo_id)
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            return json.load(f)
    return None

def guardar_grupo(grupo_id, grupo):
    archivo = grupo_file(grupo_id)
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    with open(archivo, "w") as f:
        json.dump(grupo, f)

def listar_grupos():
    carpeta = "datos_usuarios"
    if not os.path.exists(carpeta):
        return []
    return [f for f in os.listdir(carpeta) if f.startswith("grupo_") and f.endswith(".json")]

def buscar_grupos_por_usuario(email):
    grupos = []
    for archivo in listar_grupos():
        with open(os.path.join("datos_usuarios", archivo), "r") as f:
            grupo = json.load(f)
            if email in grupo.get("miembros", []):
                grupos.append(grupo)
    return grupos
