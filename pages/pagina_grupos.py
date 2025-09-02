import streamlit as st
import os
import json
from app_deudas import cargar_contactos
from utils_deudas import email_to_filename

def mostrar_pagina_grupos(user_email):
    st.header("Gestión de Grupos/Comunidades")
    grupos_file = os.path.join("datos_usuarios", f"grupos_{email_to_filename(user_email)}.json")
    def cargar_grupos():
        if os.path.exists(grupos_file):
            with open(grupos_file, "r") as f:
                return json.load(f)
        return []
    def guardar_grupos(grupos):
        with open(grupos_file, "w") as f:
            json.dump(grupos, f)
    grupos = cargar_grupos()
    st.subheader("Tus grupos:")
    if grupos:
        for g in grupos:
            st.write(f"- {g['nombre']} (miembros: {', '.join(g['miembros'])})")
    else:
        st.info("No tienes grupos aún.")
    st.write("")
    st.write("Crear nuevo grupo:")
    nombre_grupo = st.text_input("Nombre del grupo", key="nombre_grupo")
    contactos = cargar_contactos(user_email)
    miembros_seleccionados = st.multiselect("Selecciona miembros (de tus contactos)", options=contactos, key="miembros_grupo")
    if st.button("Crear grupo"):
        if nombre_grupo and miembros_seleccionados:
            nuevo_grupo = {"nombre": nombre_grupo, "miembros": miembros_seleccionados + [user_email]}
            grupos.append(nuevo_grupo)
            guardar_grupos(grupos)
            st.success(f"Grupo '{nombre_grupo}' creado.")
        else:
            st.error("Debes ingresar un nombre y seleccionar al menos un miembro.")
    st.write("")
    st.write("Eliminar grupo:")
    grupo_a_eliminar = st.selectbox("Selecciona grupo", options=[g['nombre'] for g in grupos], key="eliminar_grupo")
    if st.button("Eliminar grupo"):
        if grupo_a_eliminar:
            grupos = [g for g in grupos if g['nombre'] != grupo_a_eliminar]
            guardar_grupos(grupos)
            st.success(f"Grupo '{grupo_a_eliminar}' eliminado.")
