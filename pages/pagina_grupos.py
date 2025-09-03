import streamlit as st
import os
import json

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

def mostrar_pagina_grupos(user_email):
    st.header("Gestor de Grupos")
    st.markdown("Crea y administra grupos para compartir deudas o gastos en común.")

    grupos = cargar_grupos(user_email)
    st.subheader("Tus grupos")
    if grupos:
        for i, grupo in enumerate(grupos):
            st.write(f"{i+1}. {grupo}")
    else:
        st.info("No tienes grupos creados.")

    st.subheader("Crear nuevo grupo")
    nuevo_grupo = st.text_input("Nombre del grupo")
    if st.button("Crear grupo") and nuevo_grupo:
        if nuevo_grupo not in grupos:
            grupos.append(nuevo_grupo)
            guardar_grupos(user_email, grupos)
            st.success("Grupo creado correctamente.")
            st.experimental_rerun()
        else:
            st.warning("Ya existe un grupo con ese nombre.")

    st.subheader("Eliminar grupo")
    grupo_eliminar = st.selectbox("Selecciona el grupo a eliminar", grupos) if grupos else None
    if st.button("Eliminar grupo") and grupo_eliminar:
        grupos.remove(grupo_eliminar)
        guardar_grupos(user_email, grupos)
        st.success("Grupo eliminado correctamente.")
        st.experimental_rerun()
import streamlit as st

def mostrar_pagina_grupos(user_email):
    st.header("Gestor de Grupos")
    st.markdown("Aquí podrás crear y administrar grupos para compartir deudas o gastos en común.")
    st.info("Funcionalidad en desarrollo. Pronto podrás gestionar tus grupos desde aquí.")
