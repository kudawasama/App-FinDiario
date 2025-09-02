import streamlit as st
from utils_deudas import cargar_datos, anadir_deuda, eliminar_deuda, registrar_pago, safe_int

def mostrar_pagina_deudas(user_email):
    st.header("Gestor de Deudas Personales")
    st.markdown("Usa esta aplicación para controlar tus deudas y registrar tus pagos.")
    # El menú de opciones ya se gestiona en app_deudas.py
