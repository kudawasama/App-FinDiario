import os
import json

# --- Estructura de datos para grupos y eventos ---
# Cada grupo tiene: nombre, miembros, lista de eventos
# Cada evento tiene: nombre, administrador, participantes, montos, pagos, comprobantes

def grupos_file(email):
    return os.path.join("datos_usuarios", f"grupos_{email.replace('@','_').replace('.','_')}.json")

def cargar_grupos(email):
    archivo = grupos_file(email)
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            return json.load(f)
    return []

def guardar_grupos(email, grupos):
    archivo = grupos_file(email)
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    with open(archivo, "w") as f:
        json.dump(grupos, f)

def eventos_file(grupo_id):
    return os.path.join("datos_usuarios", f"eventos_{grupo_id}.json")

def cargar_eventos(grupo_id):
    archivo = eventos_file(grupo_id)
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            return json.load(f)
    return []

def guardar_eventos(grupo_id, eventos):
    archivo = eventos_file(grupo_id)
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    with open(archivo, "w") as f:
        json.dump(eventos, f)

# Ejemplo de estructura de grupo y evento
# grupo = {
#   "id": "amigos_uni",
#   "nombre": "Amigos de la Uni",
#   "miembros": ["ana@email.com", "luis@email.com", ...],
#   "eventos": ["fiesta_cumple", "viaje_playa"]
# }
# evento = {
#   "id": "fiesta_cumple",
#   "nombre": "Fiesta de cumpleaños",
#   "admin": "luis@email.com",
#   "participantes": ["ana@email.com", "luis@email.com", ...],
#   "montos": {"ana@email.com": 100, "luis@email.com": 100, ...},
#   "pagos": {"ana@email.com": {"monto": 100, "comprobante": "pago_ana.jpg", "confirmado": false}, ...}
# }
