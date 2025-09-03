import streamlit as st
import os
import json

def grupo_file(grupo_id):
	return os.path.join("datos_usuarios", f"grupo_{grupo_id}.json")

def cargar_grupo(grupo_id):
	archivo = grupo_file(grupo_id)
	if not os.path.exists(archivo):
		os.makedirs(os.path.dirname(archivo), exist_ok=True)
		with open(archivo, "w") as f:
			json.dump({"id": grupo_id, "nombre": "", "miembros": []}, f)
	with open(archivo, "r") as f:
		return json.load(f)

def guardar_grupo(grupo_id, grupo):
	archivo = grupo_file(grupo_id)
	if not os.path.exists(archivo):
		os.makedirs(os.path.dirname(archivo), exist_ok=True)
		with open(archivo, "w") as f:
			json.dump({"id": grupo_id, "nombre": "", "miembros": []}, f)
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

def mostrar_pagina_grupos(user_email):
	st.header("Gestor de Grupos")
	st.markdown("Crea y administra grupos para compartir deudas o gastos en común.")

	grupos = buscar_grupos_por_usuario(user_email)
	st.subheader("Tus grupos")
	if grupos:
		grupo_idx = st.selectbox("Selecciona un grupo", range(len(grupos)), format_func=lambda i: grupos[i]["nombre"])
		grupo = grupos[grupo_idx]
		st.write(f"Grupo: {grupo['nombre']}")
		st.write("Miembros:")
		for miembro in grupo.get("miembros", [user_email]):
			st.write(f"- {miembro}")
		st.subheader("Agregar miembro")
		nuevo_miembro = st.text_input("Correo del nuevo miembro")
		if st.button("Agregar miembro") and nuevo_miembro:
			if nuevo_miembro not in grupo["miembros"]:
				grupo["miembros"].append(nuevo_miembro)
				guardar_grupo(grupo['id'], grupo)
				st.success("Miembro agregado correctamente.")
				st.experimental_rerun()
			else:
				st.warning("Ese miembro ya está en el grupo.")
		st.subheader("Eliminar miembro")
		miembro_eliminar = st.selectbox("Selecciona el miembro a eliminar", grupo["miembros"]) if "miembros" in grupo else None
		if st.button("Eliminar miembro") and miembro_eliminar and miembro_eliminar != user_email:
			grupo["miembros"].remove(miembro_eliminar)
			guardar_grupo(grupo['id'], grupo)
			st.success("Miembro eliminado correctamente.")
			st.experimental_rerun()
		elif st.button("Eliminar miembro") and miembro_eliminar == user_email:
			st.warning("No puedes eliminarte a ti mismo del grupo.")
	else:
		st.info("No tienes grupos creados.")

	st.subheader("Crear nuevo grupo")
	nuevo_grupo = st.text_input("Nombre del grupo")
	if st.button("Crear grupo") and nuevo_grupo:
		import uuid
		grupo_id = str(uuid.uuid4())
		if not any(g["nombre"] == nuevo_grupo for g in grupos):
			grupo = {"id": grupo_id, "nombre": nuevo_grupo, "miembros": [user_email]}
			guardar_grupo(grupo_id, grupo)
			st.success("Grupo creado correctamente.")
			st.experimental_rerun()
		else:
			st.warning("Ya existe un grupo con ese nombre.")

	st.subheader("Eliminar grupo")
	grupo_eliminar = st.selectbox("Selecciona el grupo a eliminar", [g["nombre"] for g in grupos]) if grupos else None
	if st.button("Eliminar grupo") and grupo_eliminar:
		for g in grupos:
			if g["nombre"] == grupo_eliminar:
				import os
				os.remove(grupo_file(g["id"]))
		st.success("Grupo eliminado correctamente.")
		st.experimental_rerun()
