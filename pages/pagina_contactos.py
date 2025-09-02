import streamlit as st
from app_deudas import cargar_contactos, agregar_contacto, eliminar_contacto

def mostrar_pagina_contactos(user_email):
    st.header("Gestión de Contactos")
    contactos = cargar_contactos(user_email)
    st.subheader("Contactos registrados:")
    if contactos:
        for c in contactos:
            st.write(f"- {c}")
    else:
        st.info("No tienes contactos aún.")
    st.write("")
    st.write("Agregar contacto (email registrado):")
    nuevo_contacto = st.text_input("Email de contacto", key="nuevo_contacto_page")
    if st.button("Agregar contacto"):
        if nuevo_contacto and nuevo_contacto != user_email:
            exito, mensaje = agregar_contacto(user_email, nuevo_contacto)
            if exito:
                st.success(mensaje)
            else:
                st.error(mensaje)
        else:
            st.error("Ingresa un email válido y diferente al tuyo.")
    st.write("")
    st.write("Eliminar contacto:")
    contacto_a_eliminar = st.selectbox("Selecciona contacto", options=contactos, key="eliminar_contacto_page")
    if st.button("Eliminar contacto"):
        if contacto_a_eliminar:
            exito, mensaje = eliminar_contacto(user_email, contacto_a_eliminar)
            if exito:
                st.success(mensaje)
            else:
                st.error(mensaje)
