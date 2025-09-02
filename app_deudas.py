from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import streamlit as st
import pandas as pd
import os
from datetime import datetime
try:
    from streamlit_oauth import OAuth2Component
except ModuleNotFoundError:
    OAuth2Component = None
import jwt
from dotenv import load_dotenv, find_dotenv

# Cargar .env de forma robusta (busca en el cwd y padres)
_ENV_PATH = find_dotenv(usecwd=True)
load_dotenv(_ENV_PATH)


# --- Cargar credenciales desde client_secret_*.json si existe ---
import glob
import json
CLIENT_ID = None
CLIENT_SECRET = None
REDIRECT_URI = None
json_files = glob.glob("client_secret_*.json")
if json_files:
    with open(json_files[0], "r") as f:
        data = json.load(f)
        if "web" in data:
            CLIENT_ID = data["web"].get("client_id")
            CLIENT_SECRET = data["web"].get("client_secret")
            # Usa el primer redirect_uri configurado
            uris = data["web"].get("redirect_uris", [])
            if uris:
                REDIRECT_URI = uris[0]

def _get_cred(name: str):
    """Obtiene credencial desde JSON, st.secrets o variables de entorno."""
    # Prioridad: JSON > st.secrets > env
    if name == "CLIENT_ID" and CLIENT_ID:
        return CLIENT_ID
    if name == "CLIENT_SECRET" and CLIENT_SECRET:
        return CLIENT_SECRET
    if name == "REDIRECT_URI" and REDIRECT_URI:
        return REDIRECT_URI
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name)

# Configura tus credenciales de Google OAuth2 desde secrets/.env
CLIENT_ID = _get_cred("CLIENT_ID")
CLIENT_SECRET = _get_cred("CLIENT_SECRET")
REDIRECT_URI = _get_cred("REDIRECT_URI") or "http://localhost:8501"

missing_vars = [
    name for name, val in (
        ("CLIENT_ID", CLIENT_ID),
        ("CLIENT_SECRET", CLIENT_SECRET),
        ("REDIRECT_URI", REDIRECT_URI),
    ) if not val
]

if OAuth2Component is None:
    st.title("Iniciar sesión con Google")
    st.error("No se encontró la librería 'streamlit-oauth'. Añádela a requirements.txt e instálala (pip install streamlit-oauth). En Streamlit Cloud, asegúrate de que el deploy use ese requirements.txt.")
    st.stop()

if missing_vars:
    st.title("Iniciar sesión con Google")
    st.error(
        "Faltan variables de entorno: " + ", ".join(missing_vars) +
        ". Crea un archivo .env (a partir de .env.example) con tus credenciales de Google OAuth2."
    )
    st.info("Revisa el README para los pasos de configuración de Google OAuth2.")
    # Info de diagnóstico (no muestra secretos)
    st.caption(f"CWD: {os.getcwd()}")
    st.caption(f".env: {'encontrado' if _ENV_PATH else 'no encontrado'} {('→ ' + _ENV_PATH) if _ENV_PATH else ''}")
    st.stop()

if not st.session_state.get('authenticated', False):
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
    # Diagnóstico: muestra el REDIRECT_URI efectivo (no es secreto)
    st.caption(f"Página Oficial:  {REDIRECT_URI}") #REDIRECT_URI configurado:
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
        if st.button("Cerrar sesión"):
            st.session_state['authenticated'] = False
            st.session_state['user_info'] = None
            st.rerun()

# --- Bloque discreto inferior para usuario y reglamento ---
if st.session_state.get('authenticated', False):
    user_info = st.session_state['user_info']
    nombre = user_info.get('name', '')
    correo = user_info.get('email', '')
    st.markdown(f"""
    <style>
    .user-reglamento-footer {{
        position: fixed;
        left: 18px;
        bottom: 18px;
        width: 340px;
        background: rgba(30,30,30,0.92);
        border-radius: 10px;
        box-shadow: 0 2px 12px #0005;
        padding: 12px 18px 10px 18px;
        font-size: 13px;
        color: #e0e0e0;
        z-index: 99999;
        opacity: 0.97;
        transition: opacity 0.2s;
    }}
    .user-reglamento-footer:hover {{
        opacity: 1;
    }}
    .user-reglamento-footer .user-info {{
        font-weight: 500;
        font-size: 14px;
        margin-bottom: 2px;
        color: #fff;
    }}
    .user-reglamento-footer .user-email {{
        font-size: 12px;
        color: #b0b0b0;
        margin-bottom: 6px;
    }}
    .user-reglamento-footer .reglamento {{
        font-size: 12px;
        color: #aaa;
        margin-top: 4px;
    }}
    </style>
    <div class="user-reglamento-footer">
        <div class="user-info">👤 {nombre}</div>
        <div class="user-email">{correo}</div>
        <div class="reglamento">
            <b>Política de privacidad:</b> Tus datos se almacenan únicamente en tu cuenta y no se comparten ni suben a la nube. Puedes descargar o eliminar tus datos en cualquier momento.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- APP PRINCIPAL SOLO SI AUTENTICADO ---
if st.session_state['authenticated']:

    # --- Google Drive: Autenticación y funciones ---
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = None
    json_files = glob.glob("client_secret_*.json")
    if json_files:
        flow = InstalledAppFlow.from_client_secrets_file(json_files[0], SCOPES)
        creds = flow.run_local_server(port=0)
        drive_service = build('drive', 'v3', credentials=creds)
    else:
        st.warning('No se encontró client_secret_*.json para Google Drive.')

    def subir_a_drive(local_path, nombre_drive):
        if not creds:
            st.error('No autenticado con Google Drive.')
            return
        # Buscar si ya existe el archivo
        results = drive_service.files().list(q=f"name='{nombre_drive}' and trashed=false", fields="files(id, name)").execute()
        files = results.get('files', [])
        media = MediaFileUpload(local_path, mimetype='text/csv')
        if files:
            # Actualizar archivo existente
            file_id = files[0]['id']
            drive_service.files().update(fileId=file_id, media_body=media).execute()
            st.success('Archivo actualizado en Google Drive.')
        else:
            # Subir nuevo archivo
            file_metadata = {'name': nombre_drive}
            drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            st.success('Archivo subido a Google Drive.')

    def descargar_de_drive(nombre_drive, local_path):
        if not creds:
            st.error('No autenticado con Google Drive.')
            return
        results = drive_service.files().list(q=f"name='{nombre_drive}' and trashed=false", fields="files(id, name)").execute()
        files = results.get('files', [])
        if files:
            file_id = files[0]['id']
            request = drive_service.files().get_media(fileId=file_id)
            fh = io.FileIO(local_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            st.success('Archivo descargado de Google Drive.')
        else:
            st.warning('No se encontró el archivo en Google Drive.')


    # Definir funciones y variables de usuario solo una vez
    import re
    def email_to_filename(email):
        return re.sub(r'[^a-zA-Z0-9]', '_', email)
    user_info = st.session_state['user_info']
    user_email = user_info.get('email', 'default')
    ARCHIVO_CSV = os.path.join("datos_usuarios", f"deudas_{email_to_filename(user_email)}.csv")
    nombre_drive = f"deudas_{email_to_filename(user_email)}.csv"

    # Opción de respaldo manual (descargar CSV)
    if os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, "rb") as f:
            st.download_button(
                label="Descargar mis deudas (CSV)",
                data=f,
                file_name=os.path.basename(ARCHIVO_CSV),
                mime="text/csv"
            )

    # Botón de borrado en la parte inferior derecha, pequeño
    st.markdown("""
    <style>
    .delete-btn-container {
        position: fixed;
        right: 20px;
        bottom: 10px;
        z-index: 9999;
        font-size: 11px;
        color: #888;
        text-align: right;
    }
    .delete-btn-container button {
        font-size: 11px !important;
        padding: 2px 8px !important;
        margin-top: 2px;
    }
    </style>
    <div class='delete-btn-container'>
        <form action="#" method="post">
            <input type="submit" value="Eliminar mis datos" onclick="window.eliminarDatosUsuario && window.eliminarDatosUsuario(); return false;" style="font-size:11px; padding:2px 8px;">
        </form>
    </div>
    <script>
    window.eliminarDatosUsuario = function() {
        fetch(window.location.href, {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: 'eliminar_datos=1'}).then(()=>window.location.reload());
    }
    </script>
    """, unsafe_allow_html=True)

    # Manejo del borrado real en backend
    import streamlit as st
    if st.query_params.get('eliminar_datos') or st.session_state.get('eliminar_datos', False):
        import re
        def email_to_filename(email):
            return re.sub(r'[^a-zA-Z0-9]', '_', email)
        user_email = user_info.get('email', 'default')
        archivo = os.path.join("datos_usuarios", f"deudas_{email_to_filename(user_email)}.csv")
        if os.path.exists(archivo):
            os.remove(archivo)
        st.session_state['eliminar_datos'] = False
        st.success("Tus datos han sido eliminados.")

    user_info = st.session_state['user_info']
    import re
    def email_to_filename(email):
        return re.sub(r'[^a-zA-Z0-9]', '_', email)
    user_email = user_info.get('email', 'default')
    ARCHIVO_CSV = os.path.join("datos_usuarios", f"deudas_{email_to_filename(user_email)}.csv")

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
            # Crear la carpeta si no existe
            os.makedirs(os.path.dirname(ARCHIVO_CSV), exist_ok=True)
            df_vacio = pd.DataFrame(columns=['Acreedor', 'Monto Total', 'Monto Restante', 'Ultimo Pago', 'Fecha Vencimiento'])
            df_vacio.to_csv(ARCHIVO_CSV, index=False)
            # Sincronizar con Drive al crear archivo vacío
            subir_a_drive(ARCHIVO_CSV, nombre_drive)

    def cargar_datos():
        """Carga los datos del archivo CSV en un DataFrame de pandas."""
        # Descargar siempre la última versión de Drive antes de leer
        descargar_de_drive(nombre_drive, ARCHIVO_CSV)
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
            subir_a_drive(ARCHIVO_CSV, nombre_drive)
            return df_vacio


    def guardar_datos(df):
        """Guarda los datos del DataFrame en el archivo CSV y lo sube a Google Drive."""
        df.to_csv(ARCHIVO_CSV, index=False)
        subir_a_drive(ARCHIVO_CSV, nombre_drive)

    def eliminar_deuda(indice):
        """Elimina una deuda por índice y guarda el DataFrame actualizado."""
        df = cargar_datos()
        if 0 <= indice < len(df):
            df = df.drop(indice).reset_index(drop=True)
            guardar_datos(df)
            return True, "Deuda eliminada exitosamente."
        else:
            return False, "Índice de deuda inválido."

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

            st.subheader("Eliminar una Deuda")
            with st.form("form_eliminar_deuda"):
                deuda_a_eliminar = st.selectbox(
                    "Selecciona la deuda a eliminar:",
                    options=df.index,
                    format_func=lambda x: f"{df.loc[x, 'Acreedor']} - ${safe_int(df.loc[x, 'Monto Restante']):,} restantes (vence {df.loc[x, 'Fecha Vencimiento']})"
                )
                eliminar_enviado = st.form_submit_button("Eliminar Deuda")
                if eliminar_enviado:
                    exito, mensaje = eliminar_deuda(deuda_a_eliminar)
                    if exito:
                        st.success(mensaje)
                        st.rerun()
                    else:
                        st.error(mensaje)
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



