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
            name="Iniciar sesión con Google",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile",
            key="google_login"
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
            st.experimental_rerun()

# --- APP PRINCIPAL SOLO SI AUTENTICADO ---
if st.session_state['authenticated']:
    user_info = st.session_state['user_info']
    # Nombre del archivo donde se guardarán los datos
    ARCHIVO_CSV = 'deudas.csv'

    # =========================
    # Funciones de manejo de datos
    # =========================

    def crear_archivo_csv():
        """Crea el archivo CSV si no existe y escribe los encabezados."""
        if not os.path.exists(ARCHIVO_CSV):
            df_vacio = pd.DataFrame(columns=['Acreedor', 'Monto Total', 'Monto Restante', 'Ultimo Pago', 'Fecha Vencimiento'])
            df_vacio.to_csv(ARCHIVO_CSV, index=False)

    def cargar_datos():
        """Carga los datos del archivo CSV en un DataFrame de pandas."""
        crear_archivo_csv()
        try:
            return pd.read_csv(ARCHIVO_CSV)
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
        monto_restante_actual = df.loc[indice, 'Monto Restante']

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
            monto_total = st.number_input("Monto total de la deuda", min_value=0.0, format="%.2f")
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
                    format_func=lambda x: f"{df.loc[x, 'Acreedor']} - ${df.loc[x, 'Monto Restante']:.2f} restantes"
                )
                monto_pago = st.number_input("Monto del pago", min_value=0.0, format="%.2f")

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
            monto_total_deudas = df['Monto Total'].sum()
            monto_pagado = df['Ultimo Pago'].sum()  # El último pago registrado

            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Monto Total de Deudas", value=f"${monto_total_deudas:,.2f}")
            with col2:
                st.metric(label="Monto Total Pagado", value=f"${monto_pagado:,.2f}")
        else:
            st.info("Aún no tienes deudas registradas para mostrar un resumen.")
else:
    st.info("Por favor, inicia sesión con tu cuenta de Google para acceder a la app de deudas.")



