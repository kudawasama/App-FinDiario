import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_oauth import OAuth2Component
import jwt
from dotenv import load_dotenv

load_dotenv()

# Configura tus credenciales de Google OAuth2 desde variables de entorno
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

missing_vars = [
    name for name, val in (
        ("CLIENT_ID", CLIENT_ID),
        ("CLIENT_SECRET", CLIENT_SECRET),
        ("REDIRECT_URI", REDIRECT_URI),
    ) if not val
]

if missing_vars:
    st.title("Iniciar sesión con Google")
    st.error(
        "Faltan variables de entorno: " + ", ".join(missing_vars) +
        ". Crea un archivo .env (a partir de .env.example) con tus credenciales de Google OAuth2."
    )
    st.info("Revisa el README para los pasos de configuración de Google OAuth2.")
    st.stop()

st.title("Iniciar sesión con Google")
oauth2 = OAuth2Component(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint="https://oauth2.googleapis.com/token",
)

# --- SIDEBAR: LOGIN Y CERRAR SESIÓN ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

with st.sidebar:
    st.header("Autenticación")
    if not st.session_state['authenticated']:
        result = oauth2.authorize_button(
            name="Google",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile",
            key="google_login",
            icon="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 48 48'%3E%3Cdefs%3E%3Cpath id='a' d='M44.5 20H24v8.5h11.8C34.7 33.9 30.1 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 4.1 29.6 2 24 2 11.8 2 2 11.8 2 24s9.8 22 22 22c11 0 21-8 21-22 0-1.3-.2-2.7-.5-4z'/%3E%3C/defs%3E%3CclipPath id='b'%3E%3Cuse xlink:href='%23a' overflow='visible'/%3E%3C/clipPath%3E%3Cpath clip-path='url(%23b)' fill='%23FBBC05' d='M0 37V11l17 13z'/%3E%3Cpath clip-path='url(%23b)' fill='%23EA4335' d='M0 11l17 13 7-6.1L48 14V0H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%2334A853' d='M0 37l30-23 7.9 1L48 0v48H0z'/%3E%3Cpath clip-path='url(%23b)' fill='%234285F4' d='M48 48L17 24l-4-3 35-10z'/%3E%3C/svg%3E",
            use_container_width=False
        )
        if result and "token" in result:
            id_token = result["token"]["id_token"]
            user_info = jwt.decode(id_token, options={"verify_signature": False})
            st.session_state['authenticated'] = True
            st.session_state['user_info'] = user_info
            st.success(f"¡Bienvenido, {user_info.get('name', 'Usuario')}!")
            st.rerun()
    else:
        user_info = st.session_state['user_info']
        st.write(f"Usuario: {user_info.get('name', '')}")
        st.write(f"Correo: {user_info.get('email', '')}")
        if st.button("Cerrar sesión"):
            st.session_state['authenticated'] = False
            st.session_state['user_info'] = None
            st.rerun()

# --- APP PRINCIPAL SOLO SI AUTENTICADO ---
if st.session_state['authenticated']:
    user_info = st.session_state['user_info']
    # Nombre del archivo donde se guardarán los datos
    ARCHIVO_CSV = 'deudas.csv'

    # =========================
    # Funciones de manejo de datos
    # =========================

    def safe_int(val):
        """Convierte a entero de forma segura (NaN/valores inválidos -> 0)."""
        try:
            num = pd.to_numeric(val, errors='coerce')
            if pd.isna(num):
                return 0
            return int(num)
        except Exception:
            return 0

    def crear_archivo_csv():
        """Crea el archivo CSV si no existe y escribe los encabezados."""
        if not os.path.exists(ARCHIVO_CSV):
            df_vacio = pd.DataFrame(columns=['Acreedor', 'Monto Total', 'Monto Restante', 'Ultimo Pago', 'Fecha Vencimiento'])
            df_vacio.to_csv(ARCHIVO_CSV, index=False)

    def cargar_datos():
        """Carga los datos del archivo CSV en un DataFrame de pandas."""
        crear_archivo_csv()
        try:
            df = pd.read_csv(ARCHIVO_CSV)
            # Asegurar tipos enteros para montos si es posible
            for col in ['Monto Total', 'Monto Restante', 'Ultimo Pago']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            return df
        except pd.errors.EmptyDataError:
            # Si el archivo está vacío, crea encabezados y retorna un DataFrame vacío
            df_vacio = pd.DataFrame(columns=['Acreedor', 'Monto Total', 'Monto Restante', 'Ultimo Pago', 'Fecha Vencimiento'])
            df_vacio.to_csv(ARCHIVO_CSV, index=False)
            return df_vacio

    def guardar_datos(df):
        """Guarda los datos del DataFrame en el archivo CSV."""
        df.to_csv(ARCHIVO_CSV, index=False)

    def anadir_deuda(acreedor, monto_total, fecha_vencimiento):
        """Añade una nueva deuda al DataFrame."""
        df = cargar_datos()
        try:
            monto_total = int(monto_total)
        except Exception:
            monto_total = 0
        nueva_fila = {
            'Acreedor': acreedor,
            'Monto Total': monto_total,
            'Monto Restante': monto_total,
            'Ultimo Pago': 0,
            'Fecha Vencimiento': fecha_vencimiento
        }
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        guardar_datos(df)

    def registrar_pago(indice, monto_pago):
        """Registra un pago para una deuda existente."""
        df = cargar_datos()
        monto_restante_actual = safe_int(df.loc[indice, 'Monto Restante'])
        try:
            monto_pago = safe_int(monto_pago)
        except Exception:
            return False, "El monto del pago debe ser un número entero válido."

        if monto_pago > monto_restante_actual:
            return False, "El pago no puede ser mayor que el monto restante."

        df.loc[indice, 'Monto Restante'] = monto_restante_actual - monto_pago
        df.loc[indice, 'Ultimo Pago'] = monto_pago
        guardar_datos(df)
        return True, "Pago registrado con éxito."




    # =========================
    # Interfaz de Usuario con Streamlit
    # =========================

    st.set_page_config(page_title="Gestor de Deudas Personales", page_icon="💸")

    # Título y subtítulo
    st.title("💸 Gestor de Deudas Personales")
    st.markdown("Usa esta aplicación para controlar tus deudas y registrar tus pagos.")

    # Menú lateral para la navegación
    st.sidebar.header("Menú de opciones")
    opcion = st.sidebar.radio(
        "Selecciona una opción:",
        ["Añadir Deuda", "Listar y Pagar", "Resumen de Deudas"]
    )

    # Sección 1: Añadir Deuda
    if opcion == "Añadir Deuda":
        st.header("Añadir Nueva Deuda")
        with st.form("form_anadir_deuda"):
            acreedor = st.text_input("Nombre del acreedor")
            monto_total = st.number_input("Monto total de la deuda", min_value=0, step=1)
            fecha_vencimiento = st.date_input("Fecha de vencimiento")

            enviado = st.form_submit_button("Añadir Deuda")
            if enviado:
                if acreedor and monto_total > 0:
                    fecha_vencimiento_str = fecha_vencimiento.strftime("%d-%m-%Y")
                    anadir_deuda(acreedor, monto_total, fecha_vencimiento_str)
                    st.success("Deuda añadida exitosamente.")
                else:
                    st.error("Por favor, llena todos los campos.")

    # Sección 2: Listar y Pagar
    elif opcion == "Listar y Pagar":
        st.header("Listado de Deudas y Pagos")
        df = cargar_datos()
        if not df.empty:
            # Mostrar la tabla de deudas
            st.dataframe(df.style.highlight_max(axis=0, color='red', subset=['Monto Restante']))

            st.subheader("Registrar un Pago")
            with st.form("form_registrar_pago"):
                deuda_a_pagar = st.selectbox(
                    "Selecciona la deuda a pagar:",
                    options=df.index,
                    format_func=lambda x: f"{df.loc[x, 'Acreedor']} - ${safe_int(df.loc[x, 'Monto Restante']):,} restantes"
                )
                monto_pago = st.number_input("Monto del pago", min_value=0, step=1)

                pago_enviado = st.form_submit_button("Registrar Pago")
                if pago_enviado:
                    if monto_pago > 0:
                        exito, mensaje = registrar_pago(deuda_a_pagar, monto_pago)
                        if exito:
                            st.success(mensaje)
                            st.rerun()  # Para refrescar la tabla
                        else:
                            st.error(mensaje)
                    else:
                        st.error("El monto del pago debe ser un número positivo.")
        else:
            st.info("Aún no tienes deudas registradas.")

    # Sección 3: Resumen de Deudas
    elif opcion == "Resumen de Deudas":
        st.header("Resumen General")
        df = cargar_datos()
        if not df.empty:
            monto_total_deudas = int(df['Monto Total'].sum())
            monto_pagado = int(df['Ultimo Pago'].sum())  # El último pago registrado

            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Monto Total de Deudas", value=f"${monto_total_deudas:,}")
            with col2:
                st.metric(label="Monto Total Pagado", value=f"${monto_pagado:,}")
        else:
            st.info("Aún no tienes deudas registradas para mostrar un resumen.")
else:
    st.info("Por favor, inicia sesión con tu cuenta de Google para acceder a la app de deudas.")



