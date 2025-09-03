import streamlit as st
import os
import json

def contactos_file(email):
	return os.path.join("datos_usuarios", f"contactos_{email.replace('@','_').replace('.','_')}.json")

def cargar_contactos(email):
	archivo = contactos_file(email)
	if not os.path.exists(archivo):
		os.makedirs(os.path.dirname(archivo), exist_ok=True)
		with open(archivo, "w") as f:
			json.dump([], f)
	with open(archivo, "r") as f:
		return json.load(f)

def guardar_contactos(email, contactos):
	archivo = contactos_file(email)
	if not os.path.exists(archivo):
		os.makedirs(os.path.dirname(archivo), exist_ok=True)
		with open(archivo, "w") as f:
			json.dump([], f)
	with open(archivo, "w") as f:
		json.dump(contactos, f)

def mostrar_pagina_contactos(user_email):
	st.header("Gestor de Contactos")
	st.markdown("Aquí podrás ver, agregar y eliminar tus contactos de confianza para compartir deudas o información.")

	contactos = cargar_contactos(user_email)
	st.subheader("Tus contactos")
	if contactos:
		for i, contacto in enumerate(contactos):
			st.write(f"{i+1}. {contacto}")
	else:
		st.info("No tienes contactos agregados.")

	st.subheader("Agregar nuevo contacto")
	nuevo_contacto = st.text_input("Correo del contacto")
	if st.button("Agregar contacto") and nuevo_contacto:
		if nuevo_contacto not in contactos:
			contactos.append(nuevo_contacto)
			guardar_contactos(user_email, contactos)
			st.success("Contacto agregado correctamente.")
			st.experimental_rerun()
		else:
			st.warning("Ese contacto ya está en tu lista.")

	st.subheader("Eliminar contacto")
	contacto_eliminar = st.selectbox("Selecciona el contacto a eliminar", contactos) if contactos else None
	if st.button("Eliminar contacto") and contacto_eliminar:
		contactos.remove(contacto_eliminar)
		guardar_contactos(user_email, contactos)
		st.success("Contacto eliminado correctamente.")
		st.experimental_rerun()
