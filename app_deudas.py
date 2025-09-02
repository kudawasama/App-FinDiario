import streamlit as st
import pandas as pd
import os
import hashlib
import json

# Archivo donde se guardan los usuarios registrados
# --- Gestión de contactos ---
def contactos_file(email):
    return os.path.join("datos_usuarios", f"contactos_{email_to_filename(email)}.json")

def cargar_contactos(email):
    archivo = contactos_file(email)
    if os.path.exists(archivo):
        with open(archivo, "r") as f:
            return json.load(f)
    return []

def guardar_contactos(email, contactos):
    archivo = contactos_file(email)
    with open(archivo, "w") as f:
        json.dump(contactos, f)

def agregar_contacto(email, contacto_email):
    contactos = cargar_contactos(email)
    if contacto_email not in contactos:
        contactos.append(contacto_email)
        guardar_contactos(email, contactos)
        return True, "Contacto agregado."
    else:
        return False, "El contacto ya existe."

def eliminar_contacto(email, contacto_email):
    contactos = cargar_contactos(email)
    if contacto_email in contactos:
        contactos.remove(contacto_email)
        guardar_contactos(email, contactos)
        return True, "Contacto eliminado."
    else:
        return False, "El contacto no existe."
USUARIOS_FILE = "usuarios.json"

# Función para hashear la contraseña
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Cargar usuarios desde el archivo JSON
def cargar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r") as f:
            return json.load(f)
    return {}

# Guardar usuarios en el archivo JSON
def guardar_usuarios(usuarios):
    with open(USUARIOS_FILE, "w") as f:
        json.dump(usuarios, f)

# Registrar un nuevo usuario
def registrar_usuario(email, password):
    usuarios = cargar_usuarios()
    if email in usuarios:
        return False, "El correo ya está registrado."
    usuarios[email] = hash_password(password)
    guardar_usuarios(usuarios)
    return True, "Usuario registrado exitosamente."

# Autenticar usuario
def autenticar_usuario(email, password):
    usuarios = cargar_usuarios()
    if email in usuarios and usuarios[email] == hash_password(password):
        return True
    return False

# Inicializar variables de sesión
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None

# Sidebar para login/registro
with st.sidebar:
    st.header("Autenticación")
    if not st.session_state['authenticated']:
        tab1, tab2 = st.tabs(["Iniciar sesión", "Registrarse"])
        with tab1:
            email = st.text_input("Correo electrónico")
            password = st.text_input("Contraseña", type="password")
            if st.button("Iniciar sesión"):
                if autenticar_usuario(email, password):
                    st.session_state['authenticated'] = True
                    st.session_state['user_email'] = email
                    st.success("¡Bienvenido!")
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos.")
        with tab2:
            email_reg = st.text_input("Correo electrónico para registro")
            password_reg = st.text_input("Contraseña para registro", type="password")
            if st.button("Registrarse"):
                exito, mensaje = registrar_usuario(email_reg, password_reg)
                if exito:
                    st.success(mensaje)
                else:
                    st.error(mensaje)
    else:
        st.write(f"Usuario: {st.session_state['user_email']}")
        if st.button("Cerrar sesión"):
            st.session_state['authenticated'] = False
            st.session_state['user_email'] = None
            st.rerun()

# Función para convertir email en nombre de archivo seguro
def email_to_filename(email):
    import re
    return re.sub(r'[^a-zA-Z0-9]', '_', email)

# Si el usuario está autenticado, define el archivo CSV de deudas
if st.session_state['authenticated']:
    user_email = st.session_state['user_email']
    # --- Sección de gestión de contactos ---
    st.sidebar.subheader("Mis contactos")
    contactos = cargar_contactos(user_email)
    st.sidebar.write("Contactos registrados:")
    if contactos:
        for c in contactos:
            st.sidebar.write(f"- {c}")
    else:
        st.sidebar.info("No tienes contactos aún.")

    st.sidebar.write("")
    st.sidebar.write("Agregar contacto (email registrado):")
    nuevo_contacto = st.sidebar.text_input("Email de contacto", key="nuevo_contacto")
    if st.sidebar.button("Agregar contacto"):
        if nuevo_contacto and nuevo_contacto != user_email:
            exito, mensaje = agregar_contacto(user_email, nuevo_contacto)
            if exito:
                st.sidebar.success(mensaje)
            else:
                st.sidebar.error(mensaje)
        else:
            st.sidebar.error("Ingresa un email válido y diferente al tuyo.")

    st.sidebar.write("")
    st.sidebar.write("Eliminar contacto:")
    contacto_a_eliminar = st.sidebar.selectbox("Selecciona contacto", options=contactos, key="eliminar_contacto")
    if st.sidebar.button("Eliminar contacto"):
        if contacto_a_eliminar:
            exito, mensaje = eliminar_contacto(user_email, contacto_a_eliminar)
            if exito:
                st.sidebar.success(mensaje)
            else:
                st.sidebar.error(mensaje)
    user_email = st.session_state['user_email']
    ARCHIVO_CSV = os.path.join("datos_usuarios", f"deudas_{email_to_filename(user_email)}.csv")

    # --- Footer de privacidad simple ---
    st.markdown("""
    <div style='position:fixed;left:18px;bottom:18px;width:340px;background:rgba(30,30,30,0.92);border-radius:10px;box-shadow:0 2px 12px #0005;padding:12px 18px 10px 18px;font-size:13px;color:#e0e0e0;z-index:99999;opacity:0.97;'>
        <b>Política de privacidad:</b> Tus datos se almacenan únicamente en tu cuenta y no se comparten ni suben a la nube. Puedes descargar o eliminar tus datos en cualquier momento.
    </div>
    """, unsafe_allow_html=True)

    # Botón para eliminar datos del usuario
    if st.button("Eliminar mis datos"): 
        if os.path.exists(ARCHIVO_CSV):
            os.remove(ARCHIVO_CSV)
            st.success("Tus datos han sido eliminados.")

    # Opción para descargar el archivo CSV
    if os.path.exists(ARCHIVO_CSV):
        with open(ARCHIVO_CSV, "rb") as f:
            st.download_button(
                label="Descargar mis deudas (CSV)",
                data=f,
                file_name=os.path.basename(ARCHIVO_CSV),
                mime="text/csv"
            )
    # Opción para importar CSV
    st.subheader("Importar deudas desde CSV")
    archivo_importado = st.file_uploader("Selecciona un archivo CSV para importar", type="csv")
    if archivo_importado:
        df_import = pd.read_csv(archivo_importado)
        df_import.to_csv(ARCHIVO_CSV, index=False)
        st.success("Archivo importado correctamente.")

# --- Bloque inferior de usuario y reglamento ---
# (Este bloque tiene problemas porque usa user_info, que no existe en el login local)
# ...código del footer y borrado de datos...

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
        os.makedirs(os.path.dirname(ARCHIVO_CSV), exist_ok=True)
        df_vacio = pd.DataFrame(columns=['Acreedor', 'Monto Total', 'Monto Restante', 'Ultimo Pago', 'Fecha Vencimiento'])
        df_vacio.to_csv(ARCHIVO_CSV, index=False)

def cargar_datos():
    """Carga los datos del archivo CSV en un DataFrame de pandas."""
    crear_archivo_csv()
    try:
        df = pd.read_csv(ARCHIVO_CSV)
        for col in ['Monto Total', 'Monto Restante', 'Ultimo Pago']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        return df
    except pd.errors.EmptyDataError:
        df_vacio = pd.DataFrame(columns=['Acreedor', 'Monto Total', 'Monto Restante', 'Ultimo Pago', 'Fecha Vencimiento'])
        df_vacio.to_csv(ARCHIVO_CSV, index=False)
        return pd.DataFrame(columns=['Acreedor', 'Monto Total', 'Monto Restante', 'Ultimo Pago', 'Fecha Vencimiento'])

def guardar_datos(df):
    """Guarda los datos del DataFrame en el archivo CSV."""
    df.to_csv(ARCHIVO_CSV, index=False)

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

# =========================
# Interfaz de Usuario con Streamlit
# =========================

if st.session_state['authenticated']:
    st.set_page_config(page_title="Gestor de Deudas Personales", page_icon="💸")
    st.title("💸 Gestor de Deudas Personales")
    st.markdown("Usa esta aplicación para controlar tus deudas y registrar tus pagos.")

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
                            st.rerun()
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
            monto_pagado = int(df['Ultimo Pago'].sum())

            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Monto Total de Deudas", value=f"${monto_total_deudas:,}")
            with col2:
                st.metric(label="Monto Total Pagado", value=f"${monto_pagado:,}")
        else:
            st.info("Aún no tienes deudas registradas para mostrar un resumen.")
else:
    st.info("Por favor, inicia sesión con tu cuenta para acceder a la app de deudas.")



